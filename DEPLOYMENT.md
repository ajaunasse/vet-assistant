# Guide de Déploiement - NeuroVet sur Hetzner

Ce guide décrit le déploiement complet de NeuroVet sur un serveur Hetzner.

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
  - `A` record (optionnel) : `api.neurovet.votredomaine.com` → IP_DU_SERVEUR

### Autres
- Clé SSH pour accès sécurisé
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

### 1.3 Créer un Utilisateur Non-Root

```bash
# Créer utilisateur
adduser neurovet

# Ajouter aux sudoers
usermod -aG sudo neurovet

# Copier les clés SSH
rsync --archive --chown=neurovet:neurovet ~/.ssh /home/neurovet

# Se connecter avec le nouvel utilisateur
su - neurovet
```

### 1.4 Configuration du Firewall

```bash
# Installer UFW
sudo apt install ufw -y

# Configurer les règles
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow https

# Activer le firewall
sudo ufw enable

# Vérifier le statut
sudo ufw status
```

---

## 🐳 Étape 2 : Installation de Docker

### 2.1 Installation de Docker

```bash
# Installer les dépendances
sudo apt install apt-transport-https ca-certificates curl software-properties-common -y

# Ajouter la clé GPG Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Ajouter le repository Docker
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Installer Docker
sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io -y

# Ajouter l'utilisateur au groupe docker
sudo usermod -aG docker $USER

# Appliquer les changements (ou se déconnecter/reconnecter)
newgrp docker

# Vérifier l'installation
docker --version
```

### 2.2 Installation de Docker Compose

```bash
# Télécharger Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Rendre exécutable
sudo chmod +x /usr/local/bin/docker-compose

# Vérifier l'installation
docker-compose --version
```

---

## 📦 Étape 3 : Déploiement de l'Application

### 3.1 Cloner le Repository

```bash
# Installer git si nécessaire
sudo apt install git -y

# Créer le dossier de déploiement
mkdir -p ~/apps
cd ~/apps

# Cloner le repository
git clone https://github.com/VOTRE_USERNAME/neurolocalizer-v2.git
cd neurolocalizer-v2
```

### 3.2 Configuration des Variables d'Environnement

```bash
# Copier le fichier d'exemple
cp .env.example .env

# Éditer le fichier .env
nano .env
```

**Contenu du `.env` de production** :

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

# Frontend (si nécessaire)
REACT_APP_API_URL=https://neurovet.votredomaine.com
```

**⚠️ IMPORTANT** : Changez le mot de passe MySQL !

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
      MYSQL_PASSWORD: VOTRE_MOT_DE_PASSE_SECURISE
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
make migrate-up

# Ou manuellement
docker-compose exec backend uv run alembic upgrade head

# Vérifier la base de données
make db-check
```

---

## 🌐 Étape 4 : Configuration de Nginx

### 4.1 Installation de Nginx

```bash
sudo apt install nginx -y
```

### 4.2 Configuration du Site

```bash
sudo nano /etc/nginx/sites-available/neurovet
```

**Contenu du fichier** :

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

        # Timeouts pour les requêtes AI (peuvent être longues)
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
sudo ln -s /etc/nginx/sites-available/neurovet /etc/nginx/sites-enabled/

# Supprimer le site par défaut
sudo rm /etc/nginx/sites-enabled/default

# Tester la configuration
sudo nginx -t

# Redémarrer Nginx
sudo systemctl restart nginx

# Vérifier le statut
sudo systemctl status nginx
```

---

## 🔒 Étape 5 : Configuration SSL avec Let's Encrypt

### 5.1 Installation de Certbot

```bash
sudo apt install certbot python3-certbot-nginx -y
```

### 5.2 Obtenir le Certificat SSL

```bash
# Obtenir et installer le certificat
sudo certbot --nginx -d neurovet.votredomaine.com

# Suivre les instructions interactives
# - Entrer votre email
# - Accepter les conditions
# - Choisir de rediriger HTTP vers HTTPS (recommandé)
```

### 5.3 Test de Renouvellement Automatique

```bash
# Tester le renouvellement
sudo certbot renew --dry-run

# Le renouvellement automatique est configuré via systemd timer
sudo systemctl status certbot.timer
```

### 5.4 Configuration Nginx Finale (Après SSL)

Le fichier sera automatiquement modifié par Certbot. Vérifiez :

```bash
sudo nano /etc/nginx/sites-available/neurovet
```

Il devrait maintenant avoir une section HTTPS sur le port 443.

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
sudo tail -f /var/log/nginx/neurovet_access.log

# Error logs
sudo tail -f /var/log/nginx/neurovet_error.log
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
htop  # (installer avec: sudo apt install htop)
```

---

## 💾 Étape 7 : Backup de la Base de Données

### 7.1 Script de Backup Automatique

```bash
# Créer le dossier de backups
mkdir -p ~/backups

# Créer le script de backup
nano ~/backups/backup-db.sh
```

**Contenu du script** :

```bash
#!/bin/bash

# Configuration
BACKUP_DIR="/home/neurovet/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="neurovet_backup_$DATE.sql"
MYSQL_PASSWORD="VOTRE_MOT_DE_PASSE_SECURISE"

# Créer le backup
cd /home/neurovet/apps/neurolocalizer-v2
docker-compose exec -T db mysqldump -u neurovet -p$MYSQL_PASSWORD neurovet_db > $BACKUP_DIR/$BACKUP_FILE

# Compresser
gzip $BACKUP_DIR/$BACKUP_FILE

# Garder seulement les 7 derniers backups
find $BACKUP_DIR -name "neurovet_backup_*.sql.gz" -mtime +7 -delete

echo "Backup créé : $BACKUP_FILE.gz"
```

```bash
# Rendre exécutable
chmod +x ~/backups/backup-db.sh

# Tester le script
~/backups/backup-db.sh
```

### 7.2 Automatiser avec Cron

```bash
# Éditer crontab
crontab -e

# Ajouter cette ligne pour backup quotidien à 2h du matin
0 2 * * * /home/neurovet/backups/backup-db.sh >> /home/neurovet/backups/backup.log 2>&1
```

### 7.3 Restaurer un Backup

```bash
# Décompresser le backup
gunzip ~/backups/neurovet_backup_YYYYMMDD_HHMMSS.sql.gz

# Restaurer dans la base de données
cd ~/apps/neurolocalizer-v2
docker-compose exec -T db mysql -u neurovet -pVOTRE_MOT_DE_PASSE neurovet_db < ~/backups/neurovet_backup_YYYYMMDD_HHMMSS.sql
```

---

## 🔄 Étape 8 : Mise à Jour de l'Application

### 8.1 Script de Mise à Jour

```bash
# Créer le script
nano ~/update-neurovet.sh
```

**Contenu du script** :

```bash
#!/bin/bash

cd /home/neurovet/apps/neurolocalizer-v2

echo "📥 Pulling latest changes..."
git pull origin main

echo "🛑 Stopping services..."
docker-compose down

echo "🔨 Building new images..."
docker-compose build

echo "🚀 Starting services..."
docker-compose up -d

echo "⏳ Waiting for database..."
sleep 10

echo "🔄 Running migrations..."
docker-compose exec backend uv run alembic upgrade head

echo "✅ Update complete!"
docker-compose ps
```

```bash
# Rendre exécutable
chmod +x ~/update-neurovet.sh
```

### 8.2 Mettre à Jour

```bash
# Exécuter le script
~/update-neurovet.sh

# Vérifier les logs
cd ~/apps/neurolocalizer-v2
docker-compose logs -f
```

---

## 🔧 Étape 9 : Maintenance

### 9.1 Redémarrage des Services

```bash
cd ~/apps/neurolocalizer-v2

# Redémarrer tous les services
docker-compose restart

# Redémarrer un service spécifique
docker-compose restart backend
```

### 9.2 Nettoyage Docker

```bash
# Supprimer les images inutilisées
docker image prune -a

# Supprimer les volumes inutilisés
docker volume prune

# Nettoyage complet
docker system prune -a --volumes
```

### 9.3 Vérification de Santé

```bash
# Test endpoint health
curl https://neurovet.votredomaine.com/api/v1/health

# Test depuis l'extérieur
curl -I https://neurovet.votredomaine.com
```

---

## 🚨 Dépannage

### Services ne démarrent pas

```bash
# Vérifier les logs
docker-compose logs

# Vérifier les ports occupés
sudo netstat -tulpn | grep -E '3000|8000|3306'

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
sudo certbot certificates

# Renouveler manuellement
sudo certbot renew

# Tester la configuration nginx
sudo nginx -t
```

### Logs d'Erreur

```bash
# Backend
docker-compose logs backend | grep ERROR

# Nginx
sudo tail -100 /var/log/nginx/neurovet_error.log

# Système
sudo journalctl -xe
```

---

## 📋 Checklist Post-Déploiement

- [ ] Services Docker démarrés (frontend, backend, database)
- [ ] Base de données initialisée avec migrations
- [ ] Nginx configuré et redirection HTTP → HTTPS
- [ ] SSL Let's Encrypt configuré et valide
- [ ] Domaine accessible : `https://neurovet.votredomaine.com`
- [ ] API accessible : `https://neurovet.votredomaine.com/api/v1/health`
- [ ] Backup automatique configuré
- [ ] Monitoring en place
- [ ] Variables d'environnement sécurisées
- [ ] Firewall UFW activé
- [ ] Tests de l'application réussis

---

## 🔐 Sécurité Supplémentaire (Optionnel)

### Fail2Ban pour Protection SSH

```bash
sudo apt install fail2ban -y
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### Limiter l'Accès SSH par IP (si IP fixe)

```bash
sudo nano /etc/ssh/sshd_config

# Ajouter
AllowUsers neurovet@VOTRE_IP_FIXE

# Redémarrer SSH
sudo systemctl restart sshd
```

---

## 📞 Support et Ressources

- Documentation Docker Compose : https://docs.docker.com/compose/
- Let's Encrypt : https://letsencrypt.org/
- Nginx : https://nginx.org/en/docs/
- Hetzner Docs : https://docs.hetzner.com/

---

**🎉 Félicitations ! Votre application NeuroVet est maintenant déployée en production.**
