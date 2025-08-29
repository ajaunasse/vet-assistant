# NeuroVet - Assistant Diagnostique Neurologique Vétérinaire

Assistant IA spécialisé en neurologie vétérinaire canine pour aider les vétérinaires dans l'analyse diagnostique des troubles neurologiques chez le chien.

## 🚀 Fonctionnalités

- **Chat Interface**: Interface conversationnelle simple pour décrire les symptômes
- **Analyse Spécialisée**: IA entraînée sur la neurologie vétérinaire canine
- **Évaluations Structurées**: Localisation neuroanatomique, diagnostics différentiels, recommandations thérapeutiques
- **Architecture Propre**: Backend FastAPI avec architecture en couches
- **Interface Moderne**: Frontend React avec TypeScript

## 🏗️ Architecture

### Backend (FastAPI)
```
backend/
├── src/
│   ├── domain/              # Logique métier
│   │   ├── entities/        # Entités du domaine
│   │   ├── interfaces/      # Interfaces
│   │   └── services/        # Services métier
│   ├── infrastructure/      # Couche infrastructure
│   │   └── ai/             # Service OpenAI
│   ├── presentation/        # Couche présentation
│   │   └── api/            # Routes FastAPI
│   └── main.py             # Point d'entrée
├── requirements.txt
└── .env.example
```

### Frontend (React + TypeScript)
```
frontend/
├── src/
│   ├── components/         # Composants React
│   ├── services/          # Services API
│   ├── styles/           # Styles CSS
│   └── types/           # Types TypeScript
├── package.json
└── tsconfig.json
```

## 🛠️ Installation et Configuration

### Prérequis
- **Option 1 (Docker - Recommandé)**: Docker et Docker Compose
- **Option 2 (Local)**: Python 3.13+, Node.js 18+, MySQL 8.0+, [uv package manager](https://github.com/astral-sh/uv)
- Clé API OpenAI

## 🐳 Démarrage avec Docker (Recommandé)

### Démarrage rapide
```bash
# Cloner et configurer
git clone <repository>
cd neurolocalizer-v2

# Configurer les variables d'environnement
cp .env.example .env
# Éditer .env avec votre clé OpenAI

# Démarrer tous les services
chmod +x scripts/docker-start.sh
./scripts/docker-start.sh
```

### Services disponibles
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000  
- **API Documentation**: http://localhost:8000/docs
- **MySQL Database**: localhost:3306

### Gestion Docker
```bash
# Arrêter les services
./scripts/docker-stop.sh

# Supprimer toutes les données (base de données incluse)
docker-compose down -v

# Voir les logs
docker-compose logs -f [service_name]
```

## 💻 Installation Locale (Alternative)

### Backend Setup (with uv)

1. **Install uv (if not already installed):**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. **Setup dependencies:**
```bash
cd backend
uv sync
```

3. **Configuration:**
```bash
cp .env.example .env
# Éditer .env et ajouter votre clé OpenAI
```

4. **Lancer le serveur:**
```bash
cd src
uv run python main.py
```

Or use the convenience script:
```bash
./start_backend.sh
```

Le backend sera accessible sur `http://localhost:8000`

### Frontend Setup

1. **Installer les dépendances:**
```bash
cd frontend
npm install
```

2. **Lancer l'application:**
```bash
npm start
```

L'interface sera accessible sur `http://localhost:3000`

## 🔑 Configuration

### Variables d'environnement (.env)
```
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_ASSISTANT_ID=asst_CeppEgcYMIPQWfTAQUH2xyFp
OPENAI_MODEL=gpt-4-turbo-preview
TEMPERATURE=0.3
MAX_TOKENS=2000
```

**Note:** Le système utilise votre assistant OpenAI personnalisé si `OPENAI_ASSISTANT_ID` est configuré, sinon il utilise l'API Chat Completions standard.

## 🧠 IA Agent - Dr. NeuroVet

L'assistant utilise un prompt spécialisé qui inclut:

### Expertise
- Neuroanatomie et physiologie canine
- Troubles neurologiques courants (épilepsie, IVDD, syndrome vestibulaire)
- Méthodes de diagnostic neurologique
- Recommandations thérapeutiques evidence-based

### Capacités Diagnostiques
- **Localisation neuroanatomique** précise
- **Diagnostics différentiels** hiérarchisés par probabilité
- **Examens recommandés** adaptés au cas clinique
- **Approche thérapeutique** structurée
- **Évaluation pronostique** réaliste

### Format de Réponse
```json
{
  "assessment": "Résumé clinique",
  "localization": "Localisation neuroanatomique",
  "differentials": [
    {
      "condition": "Nom pathologie", 
      "probability": "haute/moyenne/faible", 
      "rationale": "Justification"
    }
  ],
  "diagnostics": ["Examen 1", "Examen 2"],
  "treatment": "Recommandations thérapeutiques",
  "prognosis": "Pronostic réaliste",
  "questions": ["Question clarifiante"],
  "confidence_level": "haute/moyenne/faible"
}
```

## 🔐 Sécurité et Usage

- **Usage Vétérinaire Uniquement**: Destiné aux vétérinaires diplômés
- **Aide Diagnostique**: Ne remplace pas l'examen clinique
- **Confidentialité**: Aucune donnée stockée de façon persistante
- **Déontologie**: Rappels constants sur l'importance de l'examen clinique

## 🧪 Tests

### Backend
```bash
cd backend
uv run pytest
```

### Frontend  
```bash
cd frontend
npm test
```

## 📝 Utilisation

1. **Ouvrir l'interface** sur `http://localhost:3000`
2. **Décrire les symptômes** observés chez le patient canin
3. **Recevoir l'évaluation** structurée de Dr. NeuroVet
4. **Affiner le diagnostic** en répondant aux questions clarifiantes

## 🤝 Contribution

Ce projet est destiné à l'usage vétérinaire professionnel. Pour toute suggestion d'amélioration, veuillez créer une issue.

## 📄 License

Usage strictement vétérinaire. Ne pas utiliser sans formation appropriée en médecine vétérinaire.