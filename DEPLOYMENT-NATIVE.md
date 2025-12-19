# Guide de Déploiement Natif - NeuroVet sur Hetzner (Sans Docker)

Ce guide décrit le déploiement de NeuroVet sur un serveur Hetzner **sans Docker**, avec MySQL et Nginx installés directement sur le système.

> **Note**: Docker/Docker Compose reste disponible pour le développement local. Cette configuration est pour la production.

## Architecture de Déploiement

```
Internet
    ↓
Nginx (Port 80/443)
    ├── Frontend (React build statique)
    └── Reverse Proxy → Backend
              ↓
    Backend (FastAPI + Gunicorn)
    Service systemd (Port 8000)
              ↓
    MySQL (Port 3306)
    Service systemd
```

## 📋 Prérequis

### Serveur Hetzner
- Ubuntu 22.04 LTS ou 24.04 LTS (recommandé)
- Minimum : 2 vCPU, 4GB RAM, 40GB SSD
- Recommandé : 4 vCPU, 8GB RAM, 80GB SSD
- Adresse IP publique

### Nom de Domaine
- Domaine configuré (ex: `neurovet.votredomaine.com`)
- DNS A record : `neurovet.votredomaine.com` → IP_SERVEUR

### Autres
- Clé SSH configurée
- Clé API OpenAI
- ID Assistant OpenAI

---

## 🚀 Étape 1 : Configuration Initiale du Serveur

### 1.1 Connexion et Mise à Jour

```bash
ssh root@VOTRE_IP_SERVEUR
apt update && apt upgrade -y
```

### 1.2 Sécurisation SSH

```bash
# Éditer la configuration SSH
nano /etc/ssh/sshd_config
```

**Configuration recommandée** :
```
PasswordAuthentication no
PubkeyAuthentication yes
PermitRootLogin prohibit-password
PermitEmptyPasswords no
```

```bash
# Redémarrer SSH (⚠️ testez dans une autre session avant !)
systemctl restart sshd
```

### 1.3 Fail2Ban et Firewall

```bash
# Installer Fail2Ban
apt install fail2ban -y
systemctl enable fail2ban
systemctl start fail2ban

# Configurer UFW
apt install ufw -y
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow http
ufw allow https
ufw enable
```

---

## 🗄️ Étape 2 : Installation de MySQL

### 2.1 Installer MySQL Server

```bash
apt install mysql-server -y
```

### 2.2 Sécuriser MySQL

```bash
# Lancer le script de sécurisation
mysql_secure_installation
```

**Réponses recommandées** :
- Validate Password Component: `Y`
- Password Level: `2` (STRONG)
- Remove anonymous users: `Y`
- Disallow root login remotely: `Y`
- Remove test database: `Y`
- Reload privilege tables: `Y`

### 2.3 Créer la Base de Données et l'Utilisateur

```bash
# Se connecter à MySQL
mysql -u root -p
```

**Dans MySQL** :
```sql
-- Créer la base de données
CREATE DATABASE neurovet_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Créer l'utilisateur (⚠️ utilisez un mot de passe fort !)
CREATE USER 'neurovet'@'localhost' IDENTIFIED BY 'VOTRE_MOT_DE_PASSE_SECURISE';

-- Donner les privilèges
GRANT ALL PRIVILEGES ON neurovet_db.* TO 'neurovet'@'localhost';

-- Appliquer les changements
FLUSH PRIVILEGES;

-- Vérifier
SHOW DATABASES;
SELECT User, Host FROM mysql.user WHERE User = 'neurovet';

-- Quitter
EXIT;
```

### 2.4 Tester la Connexion

```bash
mysql -u neurovet -p neurovet_db
# Entrez le mot de passe, puis EXIT
```

---

## 🐍 Étape 3 : Installation du Backend

### 3.1 Installer Python 3.12 et uv

```bash
# Installer les dépendances
apt install software-properties-common -y

# Ajouter le PPA deadsnakes (pour Python 3.12)
add-apt-repository ppa:deadsnakes/ppa -y
apt update

# Installer Python 3.12
apt install python3.12 python3.12-venv python3.12-dev -y

# Vérifier l'installation
python3.12 --version

# Créer un alias (optionnel)
update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.12 1

# Installer uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Activer uv dans le shell actuel
source $HOME/.cargo/env

# Vérifier
uv --version
```

### 3.2 Cloner le Projet

```bash
# Installer git
apt install git -y

# Créer le dossier
mkdir -p /var/www/neurovet
cd /var/wwww/neurovet

# Cloner le repository
git clone https://github.com/VOTRE_USERNAME/neurolocalizer-v2.git
cd neurolocalizer-v2/backend
```

### 3.3 Configuration de l'Environnement

```bash
# Créer le fichier .env
nano /var/www/neurovet/.env
```

**Contenu du `.env`** :
```env
# OpenAI Configuration
OPENAI_API_KEY=sk-votre-clé-api-openai
OPENAI_ASSISTANT_ID=asst_votre_assistant_id
OPENAI_MODEL=gpt-4o
TEMPERATURE=0.3
MAX_TOKENS=2000

# Database Configuration (connexion locale)
DATABASE_URL=mysql+aiomysql://neurovet:VOTRE_MOT_DE_PASSE@localhost:3306/neurovet_db

# Application Settings
SQL_ECHO=false
ENVIRONMENT=production
```

### 3.4 Installer les Dépendances

```bash
cd /var/www/neurovet/backend

# Synchroniser les dépendances avec uv
uv sync

# Vérifier que tout est installé
uv run python -c "import fastapi; import openai; print('Dependencies OK')"
```

### 3.5 Lancer les Migrations

```bash
cd /var/www/neurovet/backend

# Lancer les migrations Alembic
uv run alembic upgrade head

# Vérifier la base de données
mysql -u neurovet -p neurovet_db -e "SHOW TABLES;"
```

### 3.6 Tester le Backend

```bash
cd /var/www/neurovet/backend

# Tester en mode dev
uv run uvicorn src.main:app --host 0.0.0.0 --port 8000

# Dans un autre terminal, tester :
curl http://localhost:8000/
curl http://localhost:8000/api/v1/health

# Arrêter avec Ctrl+C
```

### 3.7 Créer le Service Systemd pour le Backend

```bash
nano /etc/systemd/system/neurovet-backend.service
```

**Contenu du service** :
```ini
[Unit]
Description=NeuroVet Backend API
After=network.target mysql.service
Requires=mysql.service

[Service]
Type=notify
User=root
WorkingDirectory=/var/www/neurovet/backend
Environment="PATH=/root/.cargo/bin:/var/www/neurovet/backend/.venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
EnvironmentFile=/var/www/neurovet/.env

# Commande de démarrage avec Gunicorn
ExecStart=/root/.cargo/bin/uv run gunicorn src.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --access-logfile /var/log/neurovet/access.log \
    --error-logfile /var/log/neurovet/error.log \
    --log-level info

# Redémarrage automatique
Restart=always
RestartSec=10

# Limites de sécurité
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

### 3.8 Installer Gunicorn et Démarrer le Service

```bash
# Installer Gunicorn dans le projet
cd /var/www/neurovet/backend
uv add gunicorn

# Créer le dossier de logs
mkdir -p /var/log/neurovet

# Recharger systemd
systemctl daemon-reload

# Démarrer le service
systemctl start neurovet-backend

# Vérifier le statut
systemctl status neurovet-backend

# Activer au démarrage
systemctl enable neurovet-backend

# Voir les logs
journalctl -u neurovet-backend -f
```

---

## ⚛️ Étape 4 : Installation du Frontend

### 4.1 Installer Node.js

```bash
# Installer Node.js 20.x (LTS)
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt install nodejs -y

# Vérifier
node --version
npm --version
```

### 4.2 Builder le Frontend

```bash
cd /var/www/neurovet/frontend

# Créer le fichier .env pour le build
nano .env.production
```

**Contenu de `.env.production`** :
```env
REACT_APP_API_URL=https://neurovet.votredomaine.com
```

```bash
# Installer les dépendances
npm install

# Builder pour la production
npm run build

# Le dossier build/ contient les fichiers statiques
ls -lh build/
```

---

## 🌐 Étape 5 : Configuration de Nginx

### 5.1 Installer Nginx

```bash
apt install nginx -y
```

### 5.2 Configuration du Site

```bash
nano /etc/nginx/sites-available/neurovet
```

**Contenu complet** :
```nginx
# Configuration HTTP (avant SSL)
server {
    listen 80;
    server_name neurovet.votredomaine.com;

    # Logs
    access_log /var/log/nginx/neurovet_access.log;
    error_log /var/log/nginx/neurovet_error.log;

    # Root pour les fichiers statiques du frontend
    root /var/www/neurovet/frontend/build;
    index index.html;

    # Headers de sécurité
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Backend API - Reverse Proxy
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts pour les requêtes AI longues
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }

    # Health check (sans logs)
    location = /health {
        proxy_pass http://localhost:8000/health;
        access_log off;
    }

    # Frontend - React Router (SPA)
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Cache pour les assets statiques
    location /static {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Fichiers JavaScript et CSS
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Security: bloquer les fichiers cachés
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }
}
```

### 5.3 Activer le Site

```bash
# Créer le lien symbolique
ln -s /etc/nginx/sites-available/neurovet /etc/nginx/sites-enabled/

# Supprimer le site par défaut
rm -f /etc/nginx/sites-enabled/default

# Tester la configuration
nginx -t

# Redémarrer Nginx
systemctl restart nginx

# Vérifier
systemctl status nginx
```

### 5.4 Tester en HTTP (temporaire)

```bash
# Si DNS configuré
curl http://neurovet.votredomaine.com/api/v1/health

# Ou depuis votre machine locale
# Ouvrir dans un navigateur : http://neurovet.votredomaine.com
```

---

## 🔒 Étape 6 : Configuration SSL avec Let's Encrypt

### 6.1 Installer Certbot

```bash
apt install certbot python3-certbot-nginx -y
```

### 6.2 Obtenir le Certificat SSL

```bash
# Obtenir et installer le certificat
certbot --nginx -d neurovet.votredomaine.com

# Suivre les instructions
# - Email
# - Accepter les conditions
# - Redirection HTTP → HTTPS (recommandé)
```

### 6.3 Vérifier SSL

```bash
# Tester le certificat
certbot certificates

# Tester le renouvellement
certbot renew --dry-run

# Vérifier depuis le navigateur
curl -I https://neurovet.votredomaine.com
```

### 6.4 Configuration Finale de Nginx (Après SSL)

Nginx a été automatiquement modifié par Certbot. Vérifiez :

```bash
nano /etc/nginx/sites-available/neurovet
```

Devrait maintenant avoir :
- Redirection HTTP → HTTPS sur port 80
- Configuration HTTPS sur port 443
- Certificats SSL configurés

---

## 📊 Étape 7 : Monitoring et Logs

### 7.1 Logs Backend

```bash
# Logs systemd
journalctl -u neurovet-backend -f

# Logs applicatifs
tail -f /var/log/neurovet/access.log
tail -f /var/log/neurovet/error.log
```

### 7.2 Logs Nginx

```bash
tail -f /var/log/nginx/neurovet_access.log
tail -f /var/log/nginx/neurovet_error.log
```

### 7.3 Logs MySQL

```bash
tail -f /var/log/mysql/error.log
```

### 7.4 Monitoring Ressources

```bash
# Processus
htop

# Backend
systemctl status neurovet-backend

# MySQL
systemctl status mysql

# Nginx
systemctl status nginx

# Espace disque
df -h

# Mémoire
free -h
```

---

## 💾 Étape 8 : Backup de la Base de Données

### 8.1 Script de Backup Natif

```bash
nano /usr/local/bin/backup-neurovet-db.sh
```

**Contenu** :
```bash
#!/bin/bash

# Configuration
BACKUP_DIR="/root/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="neurovet_backup_$DATE.sql"
DB_USER="neurovet"
DB_NAME="neurovet_db"
DB_PASSWORD="VOTRE_MOT_DE_PASSE"

# Créer le dossier
mkdir -p "$BACKUP_DIR"

echo "🔄 Creating database backup..."

# Créer le backup
mysqldump -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" > "$BACKUP_DIR/$BACKUP_FILE"

if [ $? -eq 0 ]; then
    # Compresser
    gzip "$BACKUP_DIR/$BACKUP_FILE"
    echo "✅ Backup created: $BACKUP_FILE.gz"

    # Garder seulement les 7 derniers
    find "$BACKUP_DIR" -name "neurovet_backup_*.sql.gz" -mtime +7 -delete

    # Liste des backups
    echo "📦 Available backups:"
    ls -lh "$BACKUP_DIR"/neurovet_backup_*.sql.gz
else
    echo "❌ Backup failed!"
    exit 1
fi
```

```bash
# Rendre exécutable
mkdir -p /usr/local/bin
chmod +x /usr/local/bin/backup-neurovet-db.sh

# Tester
/usr/local/bin/backup-neurovet-db.sh
```

### 8.2 Automatiser avec Cron

```bash
crontab -e

# Ajouter pour backup quotidien à 2h
0 2 * * * /usr/local/bin/backup-neurovet-db.sh >> /var/log/neurovet-backup.log 2>&1
```

### 8.3 Restaurer un Backup

```bash
# Décompresser
gunzip /root/backups/neurovet_backup_YYYYMMDD_HHMMSS.sql.gz

# Restaurer
mysql -u neurovet -p neurovet_db < /root/backups/neurovet_backup_YYYYMMDD_HHMMSS.sql
```

---

## 🔄 Étape 9 : Mise à Jour de l'Application

### 9.1 Script de Mise à Jour

```bash
nano /usr/local/bin/update-neurovet.sh
```

**Contenu** :
```bash
#!/bin/bash

cd /var/www/neurovet

echo "📥 Pulling latest changes..."
git pull origin main

echo "🔧 Backend: Installing dependencies..."
cd backend
uv sync

echo "🔄 Backend: Running migrations..."
uv run alembic upgrade head

echo "⚛️  Frontend: Building..."
cd ../frontend
npm install
npm run build

echo "🔄 Restarting backend service..."
systemctl restart neurovet-backend

echo "🔄 Reloading Nginx..."
systemctl reload nginx

echo "✅ Update complete!"
systemctl status neurovet-backend
```

```bash
chmod +x /usr/local/bin/update-neurovet.sh
```

### 9.2 Mettre à Jour

```bash
/usr/local/bin/update-neurovet.sh
```

---

## 🔧 Étape 10 : Maintenance

### 10.1 Redémarrer les Services

```bash
# Backend
systemctl restart neurovet-backend

# MySQL
systemctl restart mysql

# Nginx
systemctl restart nginx

# Tous
systemctl restart neurovet-backend mysql nginx
```

### 10.2 Vérifier les Services

```bash
# Status de tous les services
systemctl status neurovet-backend mysql nginx

# Ports écoutés
netstat -tulpn | grep -E '8000|3306|80|443'

# Processus
ps aux | grep -E 'gunicorn|mysql|nginx'
```

### 10.3 Logs en Temps Réel

```bash
# Tout voir en même temps
tail -f /var/log/neurovet/error.log /var/log/nginx/neurovet_error.log /var/log/mysql/error.log
```

---

## 🚨 Dépannage

### Backend ne démarre pas

```bash
# Voir les logs détaillés
journalctl -u neurovet-backend -n 100 --no-pager

# Tester manuellement
cd /var/www/neurovet/backend
uv run uvicorn src.main:app --host 0.0.0.0 --port 8000

# Vérifier les permissions
ls -la /var/www/neurovet/backend
```

### Problèmes de Base de Données

```bash
# Tester la connexion
mysql -u neurovet -p neurovet_db

# Voir les tables
mysql -u neurovet -p neurovet_db -e "SHOW TABLES;"

# Logs MySQL
tail -50 /var/log/mysql/error.log
```

### Problèmes Nginx

```bash
# Tester la configuration
nginx -t

# Recharger
systemctl reload nginx

# Logs
tail -f /var/log/nginx/neurovet_error.log
```

### Frontend ne s'affiche pas

```bash
# Vérifier que le build existe
ls -la /var/www/neurovet/frontend/build/

# Rebuild
cd /var/www/neurovet/frontend
npm run build

# Vérifier les permissions
chmod -R 755 /var/www/neurovet/frontend/build
```

---

## 📋 Checklist Post-Déploiement

- [ ] MySQL installé et base de données créée
- [ ] Backend service systemd actif
- [ ] Frontend buildé et servi par Nginx
- [ ] Nginx configuré (reverse proxy + static files)
- [ ] SSL Let's Encrypt configuré
- [ ] Domaine accessible en HTTPS
- [ ] API health check : `https://neurovet.votredomaine.com/api/v1/health`
- [ ] Backup automatique configuré (cron)
- [ ] SSH sécurisé + Fail2Ban
- [ ] Firewall UFW actif
- [ ] Logs accessibles et monitoring en place

---

## 📞 Commandes Rapides

```bash
# Status général
systemctl status neurovet-backend mysql nginx

# Logs en temps réel
journalctl -u neurovet-backend -f

# Redémarrer tout
systemctl restart neurovet-backend nginx

# Backup
/usr/local/bin/backup-neurovet-db.sh

# Mise à jour
/usr/local/bin/update-neurovet.sh

# Vérifier les processus
ps aux | grep -E 'gunicorn|mysql|nginx'
```

---

## 🔐 Résumé Architecture

```
Production (Sans Docker)
├── MySQL (systemd)
│   └── Port 3306 (localhost)
├── Backend (systemd + gunicorn)
│   └── Port 8000 (localhost)
├── Frontend (statique)
│   └── /var/www/neurovet/frontend/build/
└── Nginx
    ├── Port 80/443 (public)
    ├── Serveur statique (frontend)
    └── Reverse proxy (backend API)
```

---

**🎉 Félicitations ! Votre application NeuroVet est déployée nativement sans Docker.**

Pour le développement local, continuez d'utiliser Docker Compose avec `make dev`.
