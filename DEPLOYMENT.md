# Guide de Déploiement - NeuroVet sur Hetzner (Version Simplifiée)

Ce guide décrit le déploiement simplifié de NeuroVet sur un serveur Hetzner en mode root.

> **Note**: Cette configuration est adaptée pour un serveur de développement/test. Pour une production critique, considérez la création d'un utilisateur dédié (voir version complète).

## Architecture de Déploiement

```
Internet
    ↓
Nginx (reverse proxy + SSL)
    ↓
Docker Compose
    ├── Frontend (React) - Port 3000
    ├── Backend (FastAPI) - Port 8000
    └── Database (MySQL) - Port 3306
```

## 📋 Prérequis

### Serveur Hetzner
- Ubuntu 22.04 LTS ou 24.04 LTS (recommandé)
- Minimum : 2 vCPU, 4GB RAM, 40GB SSD
- Recommandé : 4 vCPU, 8GB RAM, 80GB SSD
- Adresse IP publique

### Nom de Domaine
- Domaine configuré (ex: `neurovet.votredomaine.com`)
- Enregistrements DNS pointant vers votre serveur :
  - `A` record : `neurovet.votredomaine.com` → IP_DU_SERVEUR

### Autres
- Clé SSH configurée pour accès root
- Clé API OpenAI
- ID de l'assistant OpenAI configuré

---

## 🚀 Étape 1 : Configuration Initiale du Serveur

### 1.1 Connexion SSH

```bash
ssh root@VOTRE_IP_SERVEUR
```

### 1.2 Mise à Jour du Système

```bash
apt update && apt upgrade -y
```

### 1.3 Sécurisation SSH (Clés SSH uniquement)

**Important** : Assurez-vous d'avoir votre clé SSH fonctionnelle avant de désactiver l'authentification par mot de passe !

```bash
# Vérifier que votre clé SSH fonctionne
cat ~/.ssh/authorized_keys

# Éditer la configuration SSH
nano /etc/ssh/sshd_config
```

**Modifiez ces lignes** :
```
# Désactiver l'authentification par mot de passe
PasswordAuthentication no
PubkeyAuthentication yes

# Désactiver root login par mot de passe (mais autoriser par clé)
PermitRootLogin prohibit-password

# Désactiver l'authentification vide
PermitEmptyPasswords no

# Désactiver le challenge-response
ChallengeResponseAuthentication no
```

```bash
# Redémarrer SSH
systemctl restart sshd

# ⚠️ NE FERMEZ PAS votre session actuelle !
# Testez dans un NOUVEAU terminal :
ssh root@VOTRE_IP_SERVEUR
```

### 1.4 Installation de Fail2Ban

```bash
# Installer Fail2Ban
apt install fail2ban -y

# Créer la configuration locale
cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local

# Éditer la configuration
nano /etc/fail2ban/jail.local
```

**Configuration minimale** (section `[sshd]`) :
```ini
[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
bantime = 3600
findtime = 600
```

```bash
# Démarrer et activer Fail2Ban
systemctl enable fail2ban
systemctl start fail2ban

# Vérifier le statut
fail2ban-client status
fail2ban-client status sshd
```

### 1.5 Configuration du Firewall

```bash
# Installer UFW
apt install ufw -y

# Configurer les règles
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow http
ufw allow https

# ⚠️ Important : vérifiez que SSH est autorisé avant d'activer !
ufw --dry-run enable  # Test sans activer

# Activer le firewall
ufw enable

# Vérifier le statut
ufw status verbose
```

---

## 🐳 Étape 2 : Installation de Docker

### 2.1 Installation de Docker

```bash
# Installer les dépendances
apt install apt-transport-https ca-certificates curl software-properties-common -y

# Ajouter la clé GPG Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Ajouter le repository Docker
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

# Installer Docker
apt update
apt install docker-ce docker-ce-cli containerd.io -y

# Vérifier l'installation
docker --version
docker run hello-world
```

### 2.2 Installation de Docker Compose

```bash
# Télécharger Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Rendre exécutable
chmod +x /usr/local/bin/docker-compose

# Vérifier l'installation
docker-compose --version
```

---

## 📦 Étape 3 : Déploiement de l'Application

### 3.1 Cloner le Repository

```bash
# Installer git si nécessaire
apt install git -y

# Créer le dossier de déploiement
mkdir -p /opt/apps
cd /opt/apps

# Cloner le repository
git clone https://github.com/VOTRE_USERNAME/neurolocalizer-v2.git
cd neurolocalizer-v2
```

### 3.2 Configuration des Variables d'Environnement

```bash
# Copier le fichier d'exemple
cp .env.production.example .env

# Éditer le fichier .env
nano .env
```

**Contenu du `.env` minimal** :

```env
# OpenAI Configuration
OPENAI_API_KEY=sk-votre-clé-api-openai
OPENAI_ASSISTANT_ID=asst_votre_assistant_id
OPENAI_MODEL=gpt-4o
TEMPERATURE=0.3
MAX_TOKENS=2000

# Database Configuration
DATABASE_URL=mysql+aiomysql://neurovet:VOTRE_MOT_DE_PASSE_SECURISE@db:3306/neurovet_db

# Application Settings
SQL_ECHO=false

# Frontend
REACT_APP_API_URL=https://neurovet.votredomaine.com
```

**Générer un mot de passe sécurisé** :
```bash
openssl rand -base64 32
```

### 3.3 Modifier docker-compose.yml pour Production

```bash
nano docker-compose.yml
```

Modifiez les mots de passe MySQL :

```yaml
services:
  db:
    environment:
      MYSQL_ROOT_PASSWORD: VOTRE_MOT_DE_PASSE_ROOT_SECURISE
      MYSQL_DATABASE: neurovet_db
      MYSQL_USER: neurovet
      MYSQL_PASSWORD: VOTRE_MOT_DE_PASSE_SECURISE  # Même que dans .env
```

### 3.4 Build et Lancement des Services

```bash
# Build les images
docker-compose build

# Démarrer les services
docker-compose up -d

# Vérifier les services
docker-compose ps

# Voir les logs
docker-compose logs -f
```

### 3.5 Initialiser la Base de Données

```bash
# Attendre que MySQL soit prêt (30 secondes)
sleep 30

# Lancer les migrations
docker-compose exec backend uv run alembic upgrade head

# Vérifier la base de données
docker-compose exec backend uv run python -c "from src.infrastructure.database import database; print('DB OK')"
```

---

## 🌐 Étape 4 : Configuration de Nginx

### 4.1 Installation de Nginx

```bash
apt install nginx -y
```

### 4.2 Configuration du Site

```bash
nano /etc/nginx/sites-available/neurovet
```

**Contenu du fichier** (remplacez `neurovet.votredomaine.com` par votre domaine) :

```nginx
# Configuration HTTP (temporaire, avant SSL)
server {
    listen 80;
    server_name neurovet.votredomaine.com;

    # Logs
    access_log /var/log/nginx/neurovet_access.log;
    error_log /var/log/nginx/neurovet_error.log;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts pour les requêtes AI
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://localhost:8000/health;
        access_log off;
    }
}
```

### 4.3 Activer le Site

```bash
# Créer le lien symbolique
ln -s /etc/nginx/sites-available/neurovet /etc/nginx/sites-enabled/

# Supprimer le site par défaut
rm /etc/nginx/sites-enabled/default

# Tester la configuration
nginx -t

# Redémarrer Nginx
systemctl restart nginx

# Vérifier le statut
systemctl status nginx
```

---

## 🔒 Étape 5 : Configuration SSL avec Let's Encrypt

### 5.1 Installation de Certbot

```bash
apt install certbot python3-certbot-nginx -y
```

### 5.2 Obtenir le Certificat SSL

```bash
# Obtenir et installer le certificat
certbot --nginx -d neurovet.votredomaine.com

# Suivre les instructions interactives
# - Entrer votre email
# - Accepter les conditions
# - Choisir de rediriger HTTP vers HTTPS (recommandé)
```

### 5.3 Test de Renouvellement Automatique

```bash
# Tester le renouvellement
certbot renew --dry-run

# Le renouvellement automatique est configuré via systemd timer
systemctl status certbot.timer
```

### 5.4 Vérifier la Configuration

```bash
# Tester HTTPS
curl -I https://neurovet.votredomaine.com

# Vérifier les certificats
certbot certificates
```

---

## 📊 Étape 6 : Monitoring et Logs

### 6.1 Logs Docker

```bash
# Voir tous les logs
docker-compose logs -f

# Logs backend uniquement
docker-compose logs -f backend

# Logs avec limite
docker-compose logs --tail=100 -f backend
```

### 6.2 Logs Nginx

```bash
# Access logs
tail -f /var/log/nginx/neurovet_access.log

# Error logs
tail -f /var/log/nginx/neurovet_error.log
```

### 6.3 Monitoring des Ressources

```bash
# Statistiques Docker
docker stats

# Espace disque
df -h

# Mémoire
free -h

# Processus
apt install htop -y
htop
```

### 6.4 Script de Health Check

```bash
cd /opt/apps/neurolocalizer-v2

# Vérifier l'état de l'application
./scripts/health-check.sh neurovet.votredomaine.com
```

---

## 💾 Étape 7 : Backup de la Base de Données

### 7.1 Backup Manuel

```bash
cd /opt/apps/neurolocalizer-v2

# Exécuter le backup
./scripts/backup-db.sh
```

### 7.2 Automatiser avec Cron

```bash
# Éditer crontab root
crontab -e

# Ajouter cette ligne pour backup quotidien à 2h du matin
0 2 * * * /opt/apps/neurolocalizer-v2/scripts/backup-db.sh >> /var/log/neurovet-backup.log 2>&1
```

### 7.3 Restaurer un Backup

```bash
cd /opt/apps/neurolocalizer-v2

# Restaurer depuis un backup
./scripts/restore-db.sh /root/backups/neurovet_backup_YYYYMMDD_HHMMSS.sql.gz
```

---

## 🔄 Étape 8 : Mise à Jour de l'Application

### 8.1 Mise à Jour Simple

```bash
cd /opt/apps/neurolocalizer-v2

# Exécuter le script de mise à jour
./scripts/update-app.sh

# Vérifier les logs
docker-compose logs -f
```

### 8.2 Mise à Jour Manuelle

```bash
cd /opt/apps/neurolocalizer-v2

# Pull les changements
git pull origin main

# Rebuild et redémarrer
docker-compose down
docker-compose build
docker-compose up -d

# Migrations
docker-compose exec backend uv run alembic upgrade head
```

---

## 🔧 Étape 9 : Maintenance

### 9.1 Commandes Utiles

```bash
# Redémarrer tous les services
docker-compose restart

# Redémarrer un service spécifique
docker-compose restart backend

# Voir les logs en temps réel
docker-compose logs -f backend

# Accéder à un conteneur
docker-compose exec backend bash
docker-compose exec db mysql -u neurovet -p

# Vérifier l'utilisation des ressources
docker stats
```

### 9.2 Nettoyage Docker

```bash
# Supprimer les images inutilisées
docker image prune -a

# Nettoyage complet (attention aux volumes)
docker system prune -a
```

### 9.3 Vérification Fail2Ban

```bash
# Voir les bannissements
fail2ban-client status sshd

# Débannir une IP
fail2ban-client set sshd unbanip ADRESSE_IP

# Logs fail2ban
tail -f /var/log/fail2ban.log
```

---

## 🚨 Dépannage

### Services ne démarrent pas

```bash
# Vérifier les logs
cd /opt/apps/neurolocalizer-v2
docker-compose logs

# Vérifier les ports occupés
netstat -tulpn | grep -E '3000|8000|3306'

# Reconstruire complètement
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

### Problèmes de Base de Données

```bash
# Accéder au conteneur MySQL
docker-compose exec db mysql -u root -p

# Vérifier les tables
SHOW DATABASES;
USE neurovet_db;
SHOW TABLES;
```

### Problèmes SSL

```bash
# Vérifier les certificats
certbot certificates

# Renouveler manuellement
certbot renew

# Tester la configuration nginx
nginx -t
```

### Connexion SSH Bloquée

Si vous êtes bloqué par Fail2Ban ou SSH :

1. **Depuis la console Hetzner Cloud** :
   - Connectez-vous au panneau Hetzner
   - Utilisez la console web pour accéder au serveur
   - Débannissez votre IP : `fail2ban-client set sshd unbanip VOTRE_IP`

2. **Réinitialiser Fail2Ban** :
   ```bash
   systemctl stop fail2ban
   rm /var/lib/fail2ban/fail2ban.sqlite3
   systemctl start fail2ban
   ```

---

## 📋 Checklist Post-Déploiement

- [ ] SSH sécurisé (clés uniquement, pas de mot de passe)
- [ ] Fail2Ban installé et actif
- [ ] Firewall UFW activé (SSH, HTTP, HTTPS)
- [ ] Services Docker démarrés (frontend, backend, database)
- [ ] Base de données initialisée avec migrations
- [ ] Nginx configuré et redirection HTTP → HTTPS
- [ ] SSL Let's Encrypt configuré et valide
- [ ] Domaine accessible : `https://neurovet.votredomaine.com`
- [ ] API accessible : `https://neurovet.votredomaine.com/api/v1/health`
- [ ] Backup automatique configuré (cron)
- [ ] Variables d'environnement configurées
- [ ] Tests de l'application réussis

---

## 🔐 Résumé Sécurité

### ✅ Sécurité Activée
- SSH par clés uniquement (PasswordAuthentication: no)
- Fail2Ban contre les attaques brute-force
- Firewall UFW (ports SSH, HTTP, HTTPS uniquement)
- SSL/TLS avec Let's Encrypt
- Nginx en reverse proxy

### ⚠️ Pour Production Renforcée
Si vous passez en production réelle :
- [ ] Créer un utilisateur dédié non-root
- [ ] Changer le port SSH (ex: 2222)
- [ ] Limiter SSH à des IPs spécifiques
- [ ] Configurer des alertes de monitoring
- [ ] Mettre en place une stratégie de backup externe (S3, etc.)
- [ ] Activer des logs centralisés
- [ ] Configurer un WAF (Web Application Firewall)

---

## 📞 Commandes Rapides

```bash
# Status général
cd /opt/apps/neurolocalizer-v2
./scripts/health-check.sh neurovet.votredomaine.com

# Voir les logs
docker-compose logs -f

# Redémarrer l'app
docker-compose restart

# Mettre à jour
./scripts/update-app.sh

# Backup
./scripts/backup-db.sh

# Vérifier Fail2Ban
fail2ban-client status sshd
```

---

**🎉 Félicitations ! Votre application NeuroVet est maintenant déployée de manière simplifiée et sécurisée.**

Pour toute question, consultez les logs ou utilisez le script de health check.
