# Construire le .exe Windows sans avoir de PC Windows

Cette méthode utilise **GitHub Actions** : GitHub met à disposition gratuitement
une machine Windows dans le cloud le temps de la construction (quelques minutes),
puis vous récupérez l'exécutable en téléchargement. Aucune installation locale de
Windows n'est nécessaire.

## 1. Créer un dépôt GitHub
Si vous n'en avez pas déjà un :
1. Allez sur https://github.com/new
2. Donnez un nom au dépôt (ex. `notification-mail-vocale`)
3. Laissez-le public ou privé (les deux fonctionnent, Actions est gratuit dans les
   deux cas pour un compte personnel, avec des minutes gratuites chaque mois)

## 2. Envoyer tous les fichiers du projet sur GitHub
Depuis le dossier contenant `main.py`, `config.py`, `packaging/`, etc. :
```bash
git init
git add .
git commit -m "Premier envoi du projet"
git branch -M main
git remote add origin https://github.com/VOTRE_NOM_UTILISATEUR/notification-mail-vocale.git
git push -u origin main
```

**Important** : n'ajoutez jamais `config.yaml` (avec vos vrais réglages) ni aucun
mot de passe au dépôt. Ajoutez un fichier `.gitignore` :
```
config.yaml
*.db
*.log
dist/
build/
__pycache__/
```

## 3. Lancer la construction
Le fichier `.github/workflows/build-windows.yml` (déjà fourni) déclenche
automatiquement la construction dès que vous poussez du code sur `main`.

Vous pouvez aussi la déclencher manuellement :
1. Ouvrez votre dépôt sur github.com
2. Onglet **Actions**
3. Cliquez sur le workflow **"Construire l'exécutable Windows"**
4. Bouton **"Run workflow"**

## 4. Télécharger l'exécutable
Une fois le workflow terminé (icône verte ✓, quelques minutes) :
1. Cliquez sur l'exécution terminée
2. En bas de page, section **Artifacts**
3. Téléchargez **NotificationMailVocale-Windows** (fichier .zip)
4. Dézippez sur votre machine Windows (ou celle de la personne qui l'utilisera)

Le dossier contient `NotificationMailVocale.exe`, prêt à l'emploi. Suivez ensuite
les étapes 3 et 4 de `build_windows.md` (mot de passe + démarrage automatique).

## Alternative : demander à quelqu'un avec un PC Windows
Si vous préférez éviter GitHub, vous pouvez aussi simplement envoyer tout le
dossier du projet à quelqu'un possédant un PC Windows, et lui faire suivre les
3 commandes de `build_windows.md` (installation des dépendances, `pyinstaller`,
c'est tout — 5 minutes).
