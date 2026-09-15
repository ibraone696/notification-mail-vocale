"""Surveillance d'un compte mail : connexion IMAP, IDLE ou polling, filtrage et annonce."""
from __future__ import annotations

import email
import logging
import threading
import time
from email.header import decode_header

from imapclient import IMAPClient

from db import HistoriqueMails
from speech import annoncer, notification_visuelle

logger = logging.getLogger(__name__)

DELAI_IDLE_SECONDES = 300  # durée max d'une session IDLE avant renouvellement
BACKOFF_MAX_SECONDES = 300


def decoder_entete(valeur):
    if not valeur:
        return ""
    morceau, encodage = decode_header(valeur)[0]
    if isinstance(morceau, bytes):
        return morceau.decode(encodage or "utf-8", errors="ignore")
    return morceau


def extraire_corps_texte(message, longueur_max: int) -> str:
    """Récupère un court extrait texte du corps du mail (ignore HTML et pièces jointes)."""
    try:
        if message.is_multipart():
            for partie in message.walk():
                if partie.get_content_type() == "text/plain" and not partie.get_filename():
                    charset = partie.get_content_charset() or "utf-8"
                    payload = partie.get_payload(decode=True)
                    if not payload:
                        continue
                    texte = payload.decode(charset, errors="ignore")
                    return texte.strip()[:longueur_max]
            return ""
        else:
            charset = message.get_content_charset() or "utf-8"
            payload = message.get_payload(decode=True)
            if not payload:
                return ""
            texte = payload.decode(charset, errors="ignore")
            return texte.strip()[:longueur_max]
    except Exception:
        return ""


class SurveillantCompte(threading.Thread):
    """Un thread par compte mail : connexion IMAP + boucle IDLE ou polling en secours."""

    def __init__(
        self,
        compte: dict,
        mot_de_passe: str,
        config,
        historique: HistoriqueMails,
        etat_pause: threading.Event,
        etat_dnd_manuel: threading.Event,
        etat_arret: threading.Event,
    ):
        super().__init__(daemon=True, name=f"Surveillant-{compte.get('nom', compte['email'])}")
        self.compte = compte
        self.mot_de_passe = mot_de_passe
        self.config = config
        self.historique = historique
        self.etat_pause = etat_pause
        self.etat_dnd_manuel = etat_dnd_manuel
        self.etat_arret = etat_arret
        self.delai_backoff = 5

    # ------------------------------------------------------------------
    def run(self):
        while not self.etat_arret.is_set():
            try:
                self._boucle_connexion()
            except Exception as e:
                logger.error(
                    "[%s] Connexion perdue ou erreur : %s. Nouvelle tentative dans %ss.",
                    self.compte["email"], e, self.delai_backoff,
                )
                time.sleep(self.delai_backoff)
                self.delai_backoff = min(self.delai_backoff * 2, BACKOFF_MAX_SECONDES)

    # ------------------------------------------------------------------
    def _boucle_connexion(self):
        serveur = self.compte["serveur_imap"]
        port = self.compte.get("port", 993)
        dossier = self.compte.get("dossier", "INBOX")

        with IMAPClient(serveur, port=port, use_uid=True, ssl=True) as client:
            client.login(self.compte["email"], self.mot_de_passe)
            client.select_folder(dossier)
            self.delai_backoff = 5  # connexion réussie : on réinitialise le backoff
            logger.info("[%s] Connecté, surveillance de %s.", self.compte["email"], dossier)

            # Traite les mails déjà présents et non lus au démarrage
            self._traiter_non_lus(client)

            if client.has_capability("IDLE"):
                self._boucle_idle(client)
            else:
                logger.warning(
                    "[%s] IDLE non supporté par le serveur, passage en mode polling (%ss).",
                    self.compte["email"], self.config.intervalle_secours,
                )
                self._boucle_polling(client)

    # ------------------------------------------------------------------
    def _boucle_idle(self, client: IMAPClient):
        while not self.etat_arret.is_set():
            client.idle()
            try:
                reponses = client.idle_check(timeout=DELAI_IDLE_SECONDES)
            finally:
                client.idle_done()

            if reponses:
                self._traiter_non_lus(client)

    def _boucle_polling(self, client: IMAPClient):
        while not self.etat_arret.is_set():
            self._traiter_non_lus(client)
            time.sleep(self.config.intervalle_secours)
            client.noop()  # garde la connexion active

    # ------------------------------------------------------------------
    def _traiter_non_lus(self, client: IMAPClient):
        ids = client.search(["UNSEEN"])
        if not ids:
            return

        marquer_lu = self.compte.get("marquer_comme_lu", False)

        for uid in ids:
            reponse = client.fetch([uid], ["RFC822"], peek=not marquer_lu)
            brut = reponse[uid][b"RFC822"]
            message = email.message_from_bytes(brut)

            message_id = decoder_entete(message.get("Message-ID")) or f"{self.compte['email']}-{uid}"
            if self.historique.deja_traite(message_id):
                continue

            expediteur_brut = decoder_entete(message.get("From"))
            expediteur = expediteur_brut.split("<")[0].strip().strip('"') or expediteur_brut
            adresse_expediteur = expediteur_brut.lower()
            sujet = decoder_entete(message.get("Subject"))

            if self._doit_ignorer(adresse_expediteur, sujet):
                self.historique.enregistrer(message_id, self.compte["email"], expediteur, sujet)
                continue

            est_vip = any(vip in adresse_expediteur for vip in self.config.expediteurs_vip)

            self.historique.enregistrer(message_id, self.compte["email"], expediteur, sujet)
            self._annoncer_mail(expediteur, sujet, message, est_vip)

    def _doit_ignorer(self, adresse_expediteur: str, sujet: str) -> bool:
        for motif in self.config.expediteurs_ignores:
            if motif in adresse_expediteur:
                return True
        sujet_minuscule = sujet.lower()
        for mot in self.config.mots_cles_ignores:
            if mot in sujet_minuscule:
                return True
        return False

    def _annoncer_mail(self, expediteur: str, sujet: str, message, est_vip: bool):
        if self.etat_pause.is_set():
            logger.info("Notifications en pause, mail de %s non annoncé.", expediteur)
            return

        if self.config.ne_pas_deranger_actif(vip=est_vip) or (
            self.etat_dnd_manuel.is_set() and not est_vip
        ):
            logger.info("Ne pas déranger actif, mail de %s non annoncé à voix haute.", expediteur)
            return

        prefixe = "Mail important. " if est_vip else ""
        annonce = f"{prefixe}Vous avez reçu un nouveau mail de {expediteur}. Le sujet est : {sujet}."

        if self.config.lire_extrait_corps:
            extrait = extraire_corps_texte(message, self.config.longueur_extrait)
            if extrait:
                annonce += f" Extrait : {extrait}"

        logger.info("[ALERTE] %s", annonce)
        notification_visuelle(
            f"Nouveau mail — {expediteur}", sujet, active=self.config.notification_visuelle_active
        )
        annoncer(annonce, self.config.voix)
