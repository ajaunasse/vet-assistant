# Scripts de Maintenance NeuroVet

Ce dossier contient des scripts utilitaires pour la gestion et la maintenance de l'application NeuroVet.

## 📜 Scripts Disponibles

### 🗄️ backup-db.sh
Crée un backup de la base de données MySQL.

**Usage:**
```bash
./scripts/backup-db.sh
```

**Fonctionnalités:**
- Crée un dump SQL de la base de données
- Compresse automatiquement le backup (gzip)
- Sauvegarde dans `~/backups/`
- Nettoie les backups de plus de 7 jours
- Nom du fichier: `neurovet_backup_YYYYMMDD_HHMMSS.sql.gz`

**Automatisation avec cron:**
```bash
# Backup quotidien à 2h du matin
crontab -e
# Ajouter:
0 2 * * * /home/neurovet/apps/neurolocalizer-v2/scripts/backup-db.sh >> /home/neurovet/backups/backup.log 2>&1
```

---

### ♻️ restore-db.sh
Restaure la base de données depuis un backup.

**Usage:**
```bash
./scripts/restore-db.sh <backup_file.sql.gz>

# Exemple
./scripts/restore-db.sh ~/backups/neurovet_backup_20241218_140000.sql.gz
```

**Fonctionnalités:**
- Liste les backups disponibles si aucun fichier spécifié
- Demande confirmation avant restauration
- Décompresse et restaure automatiquement
- Nettoyage des fichiers temporaires

**⚠️ Attention:** La restauration écrase les données actuelles !

---

### 🔄 update-app.sh
Met à jour l'application avec les dernières modifications du repository.

**Usage:**
```bash
./scripts/update-app.sh [branch_name]

# Mise à jour depuis main (par défaut)
./scripts/update-app.sh

# Mise à jour depuis une branche spécifique
./scripts/update-app.sh develop
```

**Fonctionnalités:**
- Crée automatiquement un backup de la base de données
- Pull les dernières modifications git
- Rebuild les images Docker
- Redémarre les services
- Lance les migrations de base de données
- Affiche le statut final

**Processus complet:**
1. Backup automatique de la DB
2. Git pull
3. Docker rebuild
4. Services restart
5. Database migrations
6. Health check

---

### 🏥 health-check.sh
Vérifie l'état de santé de l'application et de l'infrastructure.

**Usage:**
```bash
# Local (par défaut)
./scripts/health-check.sh

# Production avec domaine
./scripts/health-check.sh neurovet.votredomaine.com
```

**Vérifications effectuées:**
- ✅ État des conteneurs Docker
- ✅ Connectivité Backend API
- ✅ Connectivité Frontend
- ✅ Connection MySQL
- ✅ Espace disque disponible
- ✅ Utilisation mémoire
- ✅ Erreurs récentes dans les logs
- ✅ Configuration des variables d'environnement

**Monitoring automatique:**
```bash
# Vérification toutes les heures
crontab -e
# Ajouter:
0 * * * * /home/neurovet/apps/neurolocalizer-v2/scripts/health-check.sh neurovet.votredomaine.com >> /var/log/neurovet-health.log 2>&1
```

---

## 🚀 Scripts de Déploiement Existants

### docker-start.sh
Démarre tous les services Docker.

### docker-stop.sh
Arrête tous les services Docker.

### init_db.py
Initialise la structure de la base de données (deprecated, utiliser Alembic).

### setup-dev.sh
Configure l'environnement de développement.

---

## 📋 Checklist d'Utilisation

### Développement Local
```bash
# Démarrer
make dev

# Health check
./scripts/health-check.sh
```

### Production
```bash
# Premier déploiement
# (Suivre DEPLOYMENT.md)

# Backup quotidien
./scripts/backup-db.sh

# Mise à jour
./scripts/update-app.sh

# Monitoring
./scripts/health-check.sh neurovet.votredomaine.com
```

---

## 🔧 Personnalisation

### Modifier les Mots de Passe

Dans les scripts de backup/restore, changez:
```bash
# backup-db.sh ligne ~16
-u neurovet -pneurovet_pass

# Remplacer par votre mot de passe production
-u neurovet -pVOTRE_MOT_DE_PASSE
```

### Modifier la Rétention des Backups

Dans `backup-db.sh`, modifier la ligne:
```bash
# Garder 7 jours (par défaut)
find "$BACKUP_DIR" -name "neurovet_backup_*.sql.gz" -mtime +7 -delete

# Pour garder 30 jours
find "$BACKUP_DIR" -name "neurovet_backup_*.sql.gz" -mtime +30 -delete
```

---

## 🐛 Dépannage

### Script ne s'exécute pas
```bash
# Vérifier les permissions
ls -l scripts/*.sh

# Rendre exécutable si nécessaire
chmod +x scripts/*.sh
```

### Erreur "docker-compose not found"
```bash
# Vérifier l'installation Docker Compose
docker-compose --version

# Ou utiliser la commande moderne
docker compose --version
```

### Backup échoue
```bash
# Vérifier que les conteneurs sont démarrés
docker-compose ps

# Vérifier les logs MySQL
docker-compose logs db

# Tester manuellement
docker-compose exec db mysqladmin ping -h localhost
```

---

## 📚 Ressources

- [DEPLOYMENT.md](../DEPLOYMENT.md) - Guide de déploiement complet
- [CLAUDE.md](../CLAUDE.md) - Documentation développeur
- [Makefile](../Makefile) - Commandes Docker disponibles

---

**Note:** Ces scripts sont conçus pour un environnement de production basé sur Docker Compose. Adaptez les chemins et configurations selon votre infrastructure.
