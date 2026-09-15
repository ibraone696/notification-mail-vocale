"""Annonces vocales et notifications visuelles de bureau."""
from __future__ import annotations

import logging

import pyttsx3

logger = logging.getLogger(__name__)

try:
    from plyer import notification as plyer_notification
except Exception:  # plyer peut manquer de backend sur certains systèmes
    plyer_notification = None


def annoncer(texte: str, parametres_voix: dict | None = None):
    """Lit le texte à voix haute. Une nouvelle instance du moteur est créée à chaque
    appel : cela évite les blocages connus de pyttsx3 lors d'un usage prolongé."""
    parametres_voix = parametres_voix or {}
    try:
        engine = pyttsx3.init()

        vitesse = parametres_voix.get("vitesse")
        if vitesse:
            engine.setProperty("rate", vitesse)

        volume = parametres_voix.get("volume")
        if volume is not None:
            engine.setProperty("volume", volume)

        voix_id = parametres_voix.get("voix_id")
        if voix_id is not None:
            voix_disponibles = engine.getProperty("voices")
            try:
                engine.setProperty("voice", voix_disponibles[int(voix_id)].id)
            except (ValueError, IndexError, TypeError):
                # voix_id peut être directement un identifiant système (chaîne)
                engine.setProperty("voice", voix_id)

        engine.say(texte)
        engine.runAndWait()
        engine.stop()
    except Exception as e:
        logger.error("Erreur lors de la synthèse vocale : %s", e)


def notification_visuelle(titre: str, message: str, active: bool = True):
    """Affiche une notification desktop en complément de la voix.
    Échoue silencieusement si le système ne fournit pas de backend compatible."""
    if not active or plyer_notification is None:
        return
    try:
        plyer_notification.notify(title=titre, message=message, timeout=10)
    except Exception as e:
        logger.debug("Notification visuelle indisponible : %s", e)


def lister_voix_disponibles() -> list[dict]:
    """Utilitaire pour découvrir les voix installées (index, id, nom, langues)."""
    engine = pyttsx3.init()
    voix = engine.getProperty("voices")
    resultat = [
        {"index": i, "id": v.id, "nom": v.name, "langues": v.languages}
        for i, v in enumerate(voix)
    ]
    engine.stop()
    return resultat
