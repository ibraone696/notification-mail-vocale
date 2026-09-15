"""Point d'entrée : charge la configuration, gère les mots de passe (trousseau système),
démarre un thread de surveillance par compte mail et l'icône dans la barre système."""
from __future__ import annotations

import argparse
import getpass
import logging
import logging.handlers
import os
import sys
import threading
import time

import keyring

from config import Configuration
from db import HistoriqueMails
from account_watcher import SurveillantCompte
from tray import IconeBarreSysteme
from speech import annoncer, lister_voix_disponibles

SERVICE_KEYRING = "notification_mail_vocale"


def configurer_logging(fichier_log: str):
    logger_racine = logging.getLogger()
    logger_racine.setLevel(logging.INFO)

    formatteur = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    gestionnaire_fichier = logging.handlers.RotatingFileHandler(
        fichier_log, maxBytes=2_000_000, backupCount=3, encoding="utf-8"
    )
    gestionnaire_fichier.setFormatter(formatteur)
    logger_racine.addHandler(gestionnaire_fichier)

    gestionnaire_console = logging.StreamHandler(sys.stdout)
    gestionnaire_console.setFormatter(formatteur)
    logger_racine.addHandler(gestionnaire_console)


def obtenir_mot_de_passe(email_compte: str) -> str:
    """Cherche le mot de passe dans le trousseau du système, puis dans une variable
    d'environnement en secours (utile pour un serveur sans trousseau graphique)."""
    mot_de_passe = keyring.get_password(SERVICE_KEYRING, email_compte)
    if mot_de_passe:
        return mot_de_passe

    variable_env = "EMAIL_PASS_" + email_compte.replace("@", "_").replace(".", "_").upper()
    mot_de_passe = os.environ.get(variable_env) or os.environ.get("EMAIL_PASS")
    if mot_de_passe:
        return mot_de_passe

    raise RuntimeError(
        f"Aucun mot de passe trouvé pour {email_compte}. "
        f"Enregistrez-le avec : python main.py --set-password {email_compte}"
    )


def commande_set_password(email_compte: str):
    mot_de_passe = getpass.getpass(f"Mot de passe d'application pour {email_compte} : ")
    keyring.set_password(SERVICE_KEYRING, email_compte, mot_de_passe)
    print("Mot de passe enregistré de façon sécurisée dans le trousseau du système.")


def commande_lister_voix():
    for voix in lister_voix_disponibles():
        print(f"[{voix['index']}] {voix['nom']} — {voix['id']} ({voix['langues']})")


def main():
    analyseur = argparse.ArgumentParser(description="Notification vocale de nouveaux mails.")
    analyseur.add_argument("--config", default="config.yaml", help="Chemin du fichier de configuration.")
    analyseur.add_argument(
        "--set-password", metavar="EMAIL",
        help="Enregistre le mot de passe d'un compte dans le trousseau du système et quitte.",
    )
    analyseur.add_argument(
        "--lister-voix", action="store_true", help="Affiche les voix disponibles et quitte."
    )
    args = analyseur.parse_args()

    if args.set_password:
        commande_set_password(args.set_password)
        return

    if args.lister_voix:
        commande_lister_voix()
        return

    config = Configuration(args.config)
    configurer_logging(config.fichier_log)
    logger = logging.getLogger("main")

    if not config.comptes:
        logger.error("Aucun compte défini dans %s.", args.config)
        return

    historique = HistoriqueMails(config.historique_db)

    etat_pause = threading.Event()
    etat_dnd_manuel = threading.Event()
    etat_arret = threading.Event()

    threads = []
    for compte in config.comptes:
        try:
            mot_de_passe = obtenir_mot_de_passe(compte["email"])
        except RuntimeError as e:
            logger.error(str(e))
            continue

        thread = SurveillantCompte(
            compte, mot_de_passe, config, historique, etat_pause, etat_dnd_manuel, etat_arret
        )
        thread.start()
        threads.append(thread)

    if not threads:
        logger.error("Aucun compte n'a pu démarrer (mots de passe manquants).")
        return

    annoncer("L'application de notification vocale est démarrée.", config.voix)

    def arreter():
        etat_arret.set()

    icone = IconeBarreSysteme(etat_pause, etat_dnd_manuel, arreter)
    thread_icone = threading.Thread(target=icone.demarrer, daemon=True)
    thread_icone.start()

    try:
        while not etat_arret.is_set():
            time.sleep(1)
    except KeyboardInterrupt:
        etat_arret.set()

    logger.info("Arrêt de l'application.")


if __name__ == "__main__":
    main()
