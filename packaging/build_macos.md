# macOS — créer l'application et le démarrage automatique

## 1. Prérequis
```bash
pip install -r requirements.txt
pip install pyinstaller
```

## 2. Construire l'application
Depuis le dossier du projet (celui contenant `main.py`) :
```bash
pyinstaller packaging/notification_mail_vocale.spec
```
Vous obtenez `dist/NotificationMailVocale.app`. Le fichier `.spec` fourni est déjà
configuré pour cacher l'icône du Dock (`LSUIElement`) : l'app ne vit que dans la
barre de menus, comme une vraie app "menu bar".

## 3. Installer et configurer
Déplacez `NotificationMailVocale.app` dans `/Applications`.
Placez votre `config.yaml` à côté du binaire réel :
```
/Applications/NotificationMailVocale.app/Contents/MacOS/config.yaml
```
Enregistrez le mot de passe dans le Trousseau macOS (une seule fois, en ligne de
commande, car cela nécessite une confirmation interactive) :
```bash
/Applications/NotificationMailVocale.app/Contents/MacOS/NotificationMailVocale --set-password ib.saleh696@gmail.com
```
macOS vous demandera d'autoriser l'accès au Trousseau : acceptez ("Toujours autoriser").

## 4. Démarrage automatique à l'ouverture de session
Créez un fichier LaunchAgent :

`~/Library/LaunchAgents/com.exemple.notificationmailvocale.plist` :
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.exemple.notificationmailvocale</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Applications/NotificationMailVocale.app/Contents/MacOS/NotificationMailVocale</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
</dict>
</plist>
```

Puis activez-le :
```bash
launchctl load ~/Library/LaunchAgents/com.exemple.notificationmailvocale.plist
```

## Notes macOS
- La synthèse vocale utilise NSSpeechSynthesizer, native — pas de dépendance
  supplémentaire.
- Au premier lancement, macOS (Gatekeeper) bloquera probablement l'app car elle
  n'est pas signée/notariée. Clic droit → Ouvrir, une seule fois, pour l'autoriser.
- Pour une distribution à d'autres utilisateurs (pas seulement vous), il faudrait
  idéalement signer et notarier l'app avec un compte développeur Apple — sinon
  chaque personne doit faire le clic droit → Ouvrir.
