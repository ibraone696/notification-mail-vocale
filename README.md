# Notification mail vocale

Surveille une ou plusieurs boîtes mail IMAP et annonce les nouveaux messages à voix
haute, avec notification visuelle, filtres, mode "ne pas déranger" et icône dans la
barre système.

## Fonctionnalités

- **IMAP IDLE** : notification quasi instantanée dès l'arrivée d'un mail (bascule
  automatiquement sur du polling si le serveur ne supporte pas IDLE).
- **Multi-comptes** : chaque compte est surveillé dans son propre thread.
- **Mot de passe sécurisé** : stocké dans le trousseau du système (jamais en clair).
- **Historique anti-doublons** (SQLite) : un mail n'est jamais annoncé deux fois,
  même après un redémarrage.
- **Icône dans la barre système** : pause des notifications, bascule "ne pas
  déranger", et quitter.
- **Mode "ne pas déranger" programmé** (ex. 22h–7h), avec passage forcé pour les
  expéditeurs VIP.
- **Filtres** : liste d'expéditeurs ignorés, mots-clés à ignorer dans le sujet,
  liste VIP annoncée en priorité.
- **Extrait du corps du mail** lu à voix haute (optionnel).
- **Notification visuelle desktop** en complément de la voix.
- **Logs** avec rotation automatique des fichiers.

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

1. Copiez le fichier d'exemple :
   ```bash
   cp config.example.yaml config.yaml
   ```
2. Modifiez `config.yaml` : adresse(s) mail, serveur IMAP, filtres, voix, horaires
   de silence, etc. (chaque option est commentée dans le fichier).
3. Enregistrez le mot de passe (mot de passe d'application, pas votre mot de passe
   habituel — Gmail exige la validation en deux étapes) :
   ```bash
   python main.py --set-password votre_email@gmail.com
   ```
   Le mot de passe est stocké dans le trousseau du système, jamais dans un fichier.

   *Alternative sans trousseau (ex. serveur headless)* : définissez une variable
   d'environnement `EMAIL_PASS_VOTRE_EMAIL_GMAIL_COM` (ou `EMAIL_PASS` si un seul
   compte).

## Utilisation

```bash
python main.py
```

Autres commandes utiles :

```bash
# Lister les voix de synthèse disponibles sur votre système
python main.py --lister-voix

# Utiliser un fichier de configuration différent
python main.py --config mon_config.yaml
```

L'icône dans la barre système permet de mettre les notifications en pause ou de
forcer le mode "ne pas déranger" sans fermer l'application.

## Notes

- `marquer_comme_lu: false` (par défaut) préserve le statut "non lu" de vos mails
  dans votre boîte de réception — la déduplication est assurée par l'historique
  SQLite, pas par le drapeau IMAP `\Seen`.
- Les fichiers `historique_mails.db` et `notification_mail.log` sont créés
  automatiquement au premier lancement.
