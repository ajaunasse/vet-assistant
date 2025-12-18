# Guide de Déploiement NeuroVet

Deux modes de déploiement sont disponibles selon vos besoins.

## 📦 Choix du Mode de Déploiement

### Mode 1 : Docker (Développement/Test Rapide)
**Fichier** : `DEPLOYMENT.md`

✅ **Avantages** :
- Installation rapide
- Isolation complète
- Facile à reproduire
- Bon pour dev/staging

❌ **Inconvénients** :
- Overhead Docker
- Plus de ressources nécessaires
- Complexité supplémentaire

**Quand utiliser** : Développement local, staging, tests

---

### Mode 2 : Native (Production Optimisée)
**Fichier** : `DEPLOYMENT-NATIVE.md` ⭐ **RECOMMANDÉ POUR PRODUCTION**

✅ **Avantages** :
- Performances optimales
- Moins de ressources
- Contrôle total
- Logs natifs systemd
- Plus simple en production

❌ **Inconvénients** :
- Configuration plus longue
- Dépendances système à gérer

**Quand utiliser** : Production, serveur dédié

---

## 🚀 Démarrage Rapide

### Pour le Développement Local

```bash
# Utiliser Docker Compose
make dev
```

### Pour la Production

**Option Native (Recommandée)** :
```bash
# Suivre le guide complet
cat DEPLOYMENT-NATIVE.md

# Résumé rapide :
# 1. MySQL natif
# 2. Backend avec systemd + Gunicorn
# 3. Frontend build statique sur Nginx
# 4. SSL avec Let's Encrypt
```

---

## 📊 Comparaison Détaillée

| Aspect | Docker | Native |
|--------|--------|--------|
| **Installation** | 30 min | 45 min |
| **RAM** | ~2GB | ~1GB |
| **CPU** | Overhead Docker | Direct |
| **Logs** | `docker-compose logs` | `journalctl` |
| **Monitoring** | Docker stats | systemd + htop |
| **Updates** | Rebuild images | Pull + restart |
| **Backup** | Script Docker | mysqldump natif |
| **SSL** | Certbot externe | Certbot direct |
| **Simplicité** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Performance** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Production** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

---

## 📁 Structure des Fichiers

```
.
├── DEPLOYMENT.md              # Guide Docker (dev/staging)
├── DEPLOYMENT-NATIVE.md       # Guide Native (production) ⭐
├── DEPLOYMENT-README.md       # Ce fichier
├── docker-compose.yml         # Config Docker (dev)
├── nginx.conf.example         # Config Nginx (pour les deux)
├── .env.production.example    # Variables d'env
└── scripts/
    ├── backup-db.sh                    # Backup Docker
    ├── backup-neurovet-native.sh       # Backup Native
    ├── update-app.sh                   # Update Docker
    ├── update-neurovet-native.sh       # Update Native
    ├── health-check.sh                 # Health Docker
    └── health-check-native.sh          # Health Native
```

---

## 🛠️ Scripts Disponibles

### Pour Docker (Développement/Staging)

```bash
./scripts/backup-db.sh           # Backup base de données
./scripts/restore-db.sh          # Restaurer backup
./scripts/update-app.sh          # Mettre à jour l'app
./scripts/health-check.sh        # Vérifier la santé
```

### Pour Native (Production)

```bash
/opt/scripts/backup-neurovet-native.sh    # Backup DB
/opt/scripts/update-neurovet-native.sh    # Update app
/opt/scripts/health-check-native.sh       # Health check
```

---

## 📚 Guides Complets

### 1️⃣ Déploiement Docker
👉 **Lire** : `DEPLOYMENT.md`

**Résumé des étapes** :
1. Installation Docker + Docker Compose
2. Configuration `.env`
3. `docker-compose up -d`
4. Nginx reverse proxy
5. SSL Let's Encrypt
6. Backups automatiques

---

### 2️⃣ Déploiement Native ⭐
👉 **Lire** : `DEPLOYMENT-NATIVE.md`

**Résumé des étapes** :
1. Installation MySQL natif
2. Installation Python 3.12 + uv
3. Backend avec systemd service
4. Frontend React build sur Nginx
5. SSL Let's Encrypt
6. Backups + monitoring

---

## 🔐 Sécurité (Les Deux Modes)

✅ SSH par clés uniquement
✅ Fail2Ban actif
✅ Firewall UFW (SSH, HTTP, HTTPS)
✅ SSL/TLS Let's Encrypt
✅ Nginx hardening

---

## 🆘 Support

### Problème Docker ?
- Logs : `docker-compose logs -f`
- Rebuild : `docker-compose build --no-cache`
- Health : `./scripts/health-check.sh`

### Problème Native ?
- Logs : `journalctl -u neurovet-backend -f`
- Status : `systemctl status neurovet-backend mysql nginx`
- Health : `/opt/scripts/health-check-native.sh`

---

## 💡 Recommandations

### Développement Local
```bash
# Utiliser Docker pour simplicité
make dev
```

### Staging/Test
```bash
# Docker acceptable
# Suivre DEPLOYMENT.md
```

### Production
```bash
# Native recommandé pour performances
# Suivre DEPLOYMENT-NATIVE.md ⭐
```

---

## 📞 Commandes Essentielles

### Docker Mode
```bash
cd /opt/apps/neurolocalizer-v2
docker-compose ps                      # Status
docker-compose logs -f backend         # Logs
docker-compose restart                 # Restart
./scripts/health-check.sh domain.com   # Health
```

### Native Mode
```bash
systemctl status neurovet-backend      # Status backend
systemctl status mysql nginx           # Status services
journalctl -u neurovet-backend -f      # Logs
/opt/scripts/health-check-native.sh    # Health
```

---

**Choisissez le mode adapté à votre usage et suivez le guide correspondant !**
