# Windows — créer l'exécutable et le démarrage automatique

## 1. Prérequis
```powershell
pip install -r requirements.txt
pip install pyinstaller
```

## 2. Construire l'exécutable
Depuis le dossier du projet (celui contenant `main.py`) :
```powershell
pyinstaller packaging\notification_mail_vocale.spec
```
L'exécutable est généré dans `dist\NotificationMailVocale\NotificationMailVocale.exe`
(ou `dist\NotificationMailVocale.exe` selon la version de PyInstaller).

## 3. Préparer le dossier de distribution
Copiez à côté de l'exécutable :
- `config.yaml` (votre configuration, pas l'exemple)

Le mot de passe reste dans le trousseau Windows (Gestionnaire d'identification) —
enregistrez-le une fois avec l'exécutable lui-même :
```powershell
NotificationMailVocale.exe --set-password ib.saleh696@gmail.com
```
(la première exécution avec `--set-password` peut s'ouvrir dans une console ;
c'est normal, c'est le seul cas où une fenêtre apparaît)

## 4. Démarrage automatique à l'ouverture de session
Le plus simple : créer un raccourci vers l'exécutable dans le dossier de démarrage.

```powershell
$dossierDemarrage = [Environment]::GetFolderPath('Startup')
$wshell = New-Object -ComObject WScript.Shell
$raccourci = $wshell.CreateShortcut("$dossierDemarrage\NotificationMailVocale.lnk")
$raccourci.TargetPath = "C:\Chemin\Vers\dist\NotificationMailVocale\NotificationMailVocale.exe"
$raccourci.WorkingDirectory = "C:\Chemin\Vers\dist\NotificationMailVocale"
$raccourci.Save()
```

Adaptez le chemin. L'application démarrera silencieusement (sans console) à chaque
connexion, avec son icône dans la barre système (zone de notification).

## Notes Windows
- La synthèse vocale utilise SAPI5, déjà installé nativement — aucune dépendance
  supplémentaire.
- Le trousseau utilise le Gestionnaire d'identification Windows (Credential Manager).
- Un antivirus peut parfois signaler à tort un exécutable PyInstaller ; c'est un faux
  positif classique lié au packaging, pas au code lui-même.
