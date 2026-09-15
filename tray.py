"""Icône dans la barre système avec menu (pause, ne-pas-déranger manuel, quitter)."""
from __future__ import annotations

import logging
import threading

logger = logging.getLogger(__name__)

try:
    import pystray
    from PIL import Image, ImageDraw
except Exception:
    pystray = None


def _generer_icone():
    """Dessine une petite icône (enveloppe) sans dépendre d'un fichier image externe."""
    taille = 64
    image = Image.new("RGBA", (taille, taille), (0, 0, 0, 0))
    dessin = ImageDraw.Draw(image)
    dessin.rectangle([4, 12, 60, 52], fill=(41, 128, 185, 255), outline=(255, 255, 255, 255), width=2)
    dessin.polygon([(4, 12), (32, 34), (60, 12)], fill=(255, 255, 255, 255))
    return image


class IconeBarreSysteme:
    """Encapsule l'icône système. À lancer dans son propre thread (bloquant)."""

    def __init__(self, etat_pause: threading.Event, etat_dnd_manuel: threading.Event, callback_quitter):
        self.etat_pause = etat_pause
        self.etat_dnd_manuel = etat_dnd_manuel
        self.callback_quitter = callback_quitter
        self._icone = None

    def _basculer_pause(self, icon, item):
        if self.etat_pause.is_set():
            self.etat_pause.clear()
            logger.info("Notifications vocales réactivées depuis la barre système.")
        else:
            self.etat_pause.set()
            logger.info("Notifications vocales mises en pause depuis la barre système.")

    def _basculer_dnd(self, icon, item):
        if self.etat_dnd_manuel.is_set():
            self.etat_dnd_manuel.clear()
        else:
            self.etat_dnd_manuel.set()

    def _quitter(self, icon, item):
        self.callback_quitter()
        icon.stop()

    def demarrer(self):
        if pystray is None:
            logger.warning(
                "pystray/Pillow non disponibles : pas d'icône dans la barre système, "
                "mais le script continue de fonctionner normalement en arrière-plan."
            )
            return

        menu = pystray.Menu(
            pystray.MenuItem(
                "Pause notifications",
                self._basculer_pause,
                checked=lambda item: self.etat_pause.is_set(),
            ),
            pystray.MenuItem(
                "Ne pas déranger (manuel)",
                self._basculer_dnd,
                checked=lambda item: self.etat_dnd_manuel.is_set(),
            ),
            pystray.MenuItem("Quitter", self._quitter),
        )
        self._icone = pystray.Icon(
            "notification_mail", _generer_icone(), "Notification mail vocale", menu
        )
        # .run() est bloquant : appelé depuis un thread dédié par main.py
        self._icone.run()
