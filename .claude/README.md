# Configuration de l'Assistant OpenAI pour NeuroVet

Ce dossier contient les fichiers de configuration pour l'assistant OpenAI Dr. NeuroVet.

## Fichiers

1. **openai-assistant-prompt.txt** : Instructions complètes pour l'assistant
2. **openai-assistant-schema.json** : Schéma JSON de la réponse structurée

## Configuration sur OpenAI Platform

### 1. Créer ou Modifier votre Assistant

Accédez à [OpenAI Platform - Assistants](https://platform.openai.com/assistants)

### 2. Paramètres de Base

- **Name**: Dr. NeuroVet
- **Model**: `gpt-4o` (recommandé) ou `gpt-4-turbo`
- **Instructions**: Copier tout le contenu de `openai-assistant-prompt.txt`

### 3. Paramètres Avancés

**Temperature**: `0.3`
- Valeur basse pour un comportement plus déterministe et cohérent
- Important pour un contexte médical

**Top P**: Laisser par défaut (`1.0`)
- Ne pas modifier en même temps que temperature

### 4. Response Format

Sélectionner **"JSON mode"** et configurer le schéma:

1. Activer "Structured Outputs" ou "JSON Schema"
2. Copier tout le contenu de `openai-assistant-schema.json`
3. Coller dans l'éditeur de schéma

Le schéma définit la structure de réponse attendue avec les champs obligatoires et optionnels.

### 5. Récupérer l'Assistant ID

Une fois l'assistant créé/modifié:
1. Copier l'Assistant ID (format: `asst_xxxxxxxxxxxxx`)
2. Ajouter dans votre fichier `.env`:
   ```
   OPENAI_ASSISTANT_ID=asst_xxxxxxxxxxxxx
   ```

## Structure de la Réponse

L'assistant renvoie toujours un JSON avec cette structure:

```json
{
  "status": "processed" | "completed",
  "assessment": "Évaluation neurologique...",
  "patient_data": {
    "race": "Berger Allemand",
    "age": "7 ans",
    "sexe": "mâle castré",
    "symptomes": ["symptôme 1", "symptôme 2"],
    "examens": ["examen 1", "examen 2"],
    "historique": "Contexte et évolution...",
    "traitement_actuel": "Traitement en cours..."
  },
  "question": "Question de suivi...",
  "localization": "Moelle épinière T3-L3",
  "differentials": [
    {
      "condition": "Hernie discale",
      "probability": "haute",
      "rationale": "Justification..."
    }
  ],
  "diagnostics": ["IRM médullaire", "Examen neurologique complet"],
  "treatment": "Recommandations thérapeutiques...",
  "prognosis": "Pronostic...",
  "confidence_level": "haute" | "moyenne" | "faible"
}
```

### Champs Obligatoires
- `status`: Indique la phase (collecte ou diagnostic final)
- `assessment`: Message principal de l'évaluation
- `patient_data`: Données patient structurées (objet)

### Champs Optionnels
Selon la phase et les informations disponibles:
- `question`: Pour collecter plus d'informations (phase "processed")
- `localization`, `differentials`, `diagnostics`, `treatment`, `prognosis`: Pour le diagnostic final (phase "completed")
- `confidence_level`: Niveau de confiance

## Workflow des Données Patient

1. **Backend → AI**: Les données patient existantes sont envoyées en préfixe de chaque message
2. **AI → Backend**: L'AI renvoie un objet `patient_data` complet avec toutes les infos collectées
3. **Backend**: Parse et intègre les nouvelles données dans la session
4. **Cycle**: Les données mises à jour sont renvoyées au prochain message

Ce cycle permet à l'AI de progressivement construire un dossier patient complet au fil de la conversation.

## Test de Configuration

Après configuration, testez avec une conversation simple:

**Message utilisateur**:
```
Bonjour, j'ai un Berger Allemand mâle de 7 ans qui présente une ataxie du train postérieur depuis 3 jours.
```

**Réponse attendue**:
- `status`: "processed"
- `patient_data` doit contenir les infos extraites (race, âge, sexe, symptômes)
- `question`: Une question pour collecter plus d'informations
- Autres champs optionnels selon le contexte

## Dépannage

### L'assistant ne renvoie pas de JSON structuré
- Vérifier que "JSON mode" est activé
- Vérifier que le schéma est correctement collé
- S'assurer que le model supporte structured outputs (gpt-4o recommandé)

### Les patient_data ne sont pas extraits
- Vérifier les instructions dans le prompt
- S'assurer que le schéma patient_data est correct (type: object)
- Regarder les logs backend pour voir ce qui est reçu

### Erreurs de validation du schéma
- Vérifier que tous les champs required sont présents dans la réponse
- S'assurer que les enums matchent exactement (ex: "haute", "moyenne", "faible")

## Mise à Jour

Pour mettre à jour l'assistant:
1. Modifier les fichiers dans ce dossier
2. Copier les modifications sur OpenAI Platform
3. Tester en local
4. Commit les changements dans le repo
