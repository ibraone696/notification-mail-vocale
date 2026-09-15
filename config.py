"""Gestion de la configuration de l'application (fichier YAML)."""
from __future__ import annotations

import datetime as dt
import logging
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)


class Configuration:
    """Charge et expose les paramètres du fichier config.yaml."""

    def __init__(self, chemin_config: str | Path):
        self.chemin_config = Path(chemin_config)
        if not self.chemin_config.exists():
            raise FileNotFoundError(
                f"Fichier de configuration introuvable : {self.chemin_config}. "
                "Copiez config.example.yaml vers config.yaml et adaptez-le."
            )
        with open(self.chemin_config, "r", encoding="utf-8") as f:
            self.donnees: dict[str, Any] = yaml.safe_load(f) or {}

    # ------------------------------------------------------------------
    # Comptes
    # ------------------------------------------------------------------
    @property
    def comptes(self) -> list[dict]:
        return self.donnees.get("comptes", [])

    # ------------------------------------------------------------------
    # Paramètres généraux
    # ------------------------------------------------------------------
    @property
    def intervalle_secours(self) -> int:
        return self.donnees.get("parametres", {}).get("intervalle_secours_secondes", 60)

    @property
    def historique_db(self) -> str:
        return self.donnees.get("parametres", {}).get("historique_db", "historique_mails.db")

    @property
    def fichier_log(self) -> str:
        return self.donnees.get("parametres", {}).get("fichier_log", "notification_mail.log")

    # ------------------------------------------------------------------
    # Voix
    # ------------------------------------------------------------------
    @property
    def voix(self) -> dict:
        return self.donnees.get("voix", {})

    # ------------------------------------------------------------------
    # Filtres
    # ------------------------------------------------------------------
    @property
    def expediteurs_vip(self) -> list[str]:
        return [e.lower() for e in self.donnees.get("filtres", {}).get("expediteurs_vip", [])]

    @property
    def expediteurs_ignores(self) -> list[str]:
        return [e.lower() for e in self.donnees.get("filtres", {}).get("expediteurs_ignores", [])]

    @property
    def mots_cles_ignores(self) -> list[str]:
        return [m.lower() for m in self.donnees.get("filtres", {}).get("mots_cles_ignores", [])]

    # ------------------------------------------------------------------
    # Annonce
    # ------------------------------------------------------------------
    @property
    def lire_extrait_corps(self) -> bool:
        return self.donnees.get("annonce", {}).get("lire_extrait_corps", False)

    @property
    def longueur_extrait(self) -> int:
        return self.donnees.get("annonce", {}).get("longueur_extrait", 100)

    # ------------------------------------------------------------------
    # Ne pas déranger
    # ------------------------------------------------------------------
    def ne_pas_deranger_actif(self, vip: bool = False) -> bool:
        """Retourne True si on est actuellement en période de silence programmée."""
        cfg = self.donnees.get("ne_pas_deranger", {})
        if not cfg.get("actif", False):
            return False
        if vip and cfg.get("vip_bypass", True):
            return False

        maintenant = dt.datetime.now().time()
        debut = dt.datetime.strptime(cfg.get("heure_debut", "22:00"), "%H:%M").time()
        fin = dt.datetime.strptime(cfg.get("heure_fin", "07:00"), "%H:%M").time()

        if debut <= fin:
            return debut <= maintenant <= fin
        # Plage qui traverse minuit (ex : 22:00 -> 07:00)
        return maintenant >= debut or maintenant <= fin

    @property
    def notification_visuelle_active(self) -> bool:
        return self.donnees.get("notification_visuelle", {}).get("active", True)
