# AI Patient Growth Clinic

Système complet d'acquisition patient automatisé pour cliniques esthétiques en France.

Ce repo combine un **kit de lancement d'agence** (offre, scripts, n8n) et un **pipeline agentique Python** capable de prospecter, qualifier et préparer l'outreach de manière automatisée.

---

## Structure du projet

```
.
├── .github/workflows/
│   ├── agents.yml          # Pipeline agentique — lancé automatiquement
│   └── validate.yml        # Validation JSON + structure du repo
│
├── config/
│   └── targets.json        # Cibles : villes, niches, paramètres
│
├── configs/
│   ├── agency.json         # Configuration business
│   └── niche-scorecard.json # Grille de scoring des prospects
│
├── prompts/
│   ├── orchestrator.md     # Prompt orchestrateur
│   ├── scraper.md          # Prompt agent scraper
│   ├── research.md         # Prompt agent research
│   ├── enricher.md         # Prompt agent enricher
│   ├── qualifier.md        # Prompt agent qualifier
│   └── outreach.md         # Prompt agent outreach
│
├── src/
│   ├── run_orchestrator.py # Point d'entrée — lance le pipeline complet
│   ├── run_agent.py        # Lance un agent individuel + logique de chaque agent
│   └── utils.py            # Fonctions partagées (I/O, logging, chemins)
│
├── data/
│   ├── raw/                # Données brutes (scraping + research)
│   └── processed/          # Données enrichies et qualifiées
│
├── outputs/                # Résultats finaux (outreach prêt à envoyer)
│
├── tests/
│   └── test_pipeline.py    # Tests pytest du pipeline
│
├── docs/                   # Positionnement, offre, playbook
├── scripts/                # Templates email, DM, call
├── landing/                # Copy landing page
├── n8n/                    # Workflow n8n de qualification lead
└── requirements.txt
```

---

## Objectif du projet

> Générer des consultations qualifiées pour les cliniques esthétiques françaises grâce à un système d'acquisition patient automatisé basé sur l'IA.

### Ce que fait le pipeline

1. **SCRAPER** — Collecte les cliniques esthétiques dans les villes cibles
2. **RESEARCH** — Analyse leur présence digitale (site, Meta Ads, Instagram)
3. **ENRICHER** — Trouve les contacts décideurs (praticien ou directeur)
4. **QUALIFIER** — Score chaque clinique (0-100) et la classe HOT / WARM / COLD
5. **OUTREACH** — Génère des emails et messages LinkedIn personnalisés

---

## Lancer en local

### Prérequis

```bash
python -m pip install -r requirements.txt
```

### Pipeline complet

```bash
python src/run_orchestrator.py
```

Les fichiers de sortie sont générés dans `data/` et `outputs/` avec un horodatage.

### Agent individuel

```bash
# Scraper uniquement
python src/run_agent.py scraper --output data/raw/clinics.json

# Qualifier un fichier enrichi
python src/run_agent.py qualifier --input data/processed/clinics_enriched.json

# Générer l'outreach
python src/run_agent.py outreach --input data/processed/clinics_qualified.json
```

### Tests

```bash
python -m pytest tests/ -v
```

---

## Lancer via GitHub Actions

Le workflow `.github/workflows/agents.yml` se déclenche :

- **Automatiquement** à chaque push sur `main` (si `src/`, `config/` ou `prompts/` sont modifiés)
- **Manuellement** depuis l'onglet *Actions* → *Run Agent Pipeline* → *Run workflow*
- **Planifié** chaque lundi à 06:00 UTC

Les résultats sont disponibles dans l'onglet **Artifacts** du run GitHub Actions (conservés 30 jours).

---

## Configuration des cibles

Modifier `config/targets.json` pour ajuster :

```json
{
  "cities": ["Paris", "Lyon", "Marseille", ...],
  "niches": ["clinique esthétique", "médecine esthétique", ...],
  "max_clinics_per_city": 10,
  "qualification_threshold": 50
}
```

---

## Où mettre les secrets

Les secrets sont à configurer dans **GitHub → Settings → Secrets and variables → Actions** :

| Secret | Description | Requis |
|--------|-------------|--------|
| `OPENAI_API_KEY` | Clé API OpenAI pour les agents LLM | Optionnel |
| `CALENDLY_URL` | Lien Calendly pour le booking | Optionnel |

Pour un run en local, créer un fichier `.env` (ignoré par git) :

```
OPENAI_API_KEY=sk-...
CALENDLY_URL=https://calendly.com/votre-lien
```

---

## Où récupérer les outputs

| Dossier | Contenu |
|---------|---------|
| `data/raw/` | Données brutes du scraping et de la recherche |
| `data/processed/` | Cliniques enrichies et qualifiées (JSON + CSV) |
| `outputs/` | Outreach prêt à envoyer (JSON + CSV) + résumé du run |

Le fichier `outputs/summary_TIMESTAMP.json` contient les métriques clés de chaque run.

---

## Connecter les vrais scrapers et APIs

Les agents sont structurés pour être facilement enrichis. Chaque agent contient un commentaire `--- stub: replace with real API call ---` indiquant où brancher :

- **SCRAPER** : Google Places API, Doctolib, Pages Jaunes
- **RESEARCH** : Meta Ad Library API, requests HTTP, Instagram API
- **ENRICHER** : Hunter.io, Apollo.io, LinkedIn Sales Navigator
- **QUALIFIER** : Utilise déjà `configs/niche-scorecard.json` — modifier les poids sans toucher au code

---

## Kit de lancement agence (no-code)

Les dossiers suivants constituent le kit opérationnel de l'agence :

| Dossier / Fichier | Contenu |
|-------------------|---------|
| `docs/positioning.md` | Niche, ICP, offre, promesse |
| `docs/offer.md` | Offre high-ticket avec tarifs et garanties |
| `docs/prospecting-playbook.md` | Plan de prospection sprint 14 jours |
| `scripts/cold-email.md` | Séquence email 3 messages |
| `scripts/dm-script.md` | Scripts DM LinkedIn et Instagram |
| `scripts/call-script.md` | Script call découverte 15 min |
| `landing/landing-copy.json` | Copy complète pour la landing page |
| `n8n/patient-growth-intake-workflow.json` | Workflow n8n de qualification leads |
| `configs/agency.json` | Configuration business complète |
| `configs/niche-scorecard.json` | Grille de scoring avec poids et seuils |

---

## Stack

**Pipeline agentique** : Python 3.11+, pytest

**No-code opérationnel** : n8n, Framer/Webflow, Meta Ads, Calendly, Google Sheets, WhatsApp Business API

---

## Positionnement

> J'aide les cliniques esthétiques à générer plus de consultations qualifiées grâce à un système d'acquisition patient automatisé basé sur l'IA et la publicité Meta.

---

## Points d'amélioration futurs

- [ ] Brancher le SCRAPER sur Google Places API
- [ ] Brancher le RESEARCH sur Meta Ad Library API
- [ ] Brancher l'ENRICHER sur Hunter.io ou Apollo.io
- [ ] Activer les agents LLM via `OPENAI_API_KEY` pour personnaliser l'outreach
- [ ] Ajouter un export direct vers Google Sheets ou Airtable
- [ ] Documenter la conformité RGPD pour les données collectées
- [ ] Tester le workflow n8n end-to-end avec de vrais leads
