# AI Patient Growth Clinic

Système d'acquisition patient automatisé pour cliniques esthétiques en France.

Ce repo contient deux couches complémentaires :
1. **Kit de lancement agence** — templates, offre, playbook, workflow n8n
2. **Pipeline agentique IA** — orchestrateur Python + agents spécialisés pilotés par LLM

---

## Structure du projet

```
/
├── .github/
│   └── workflows/
│       ├── validate.yml       # CI : valide JSON, structure, absence de secrets
│       └── agents.yml         # CI : lance le pipeline IA (workflow_dispatch)
│
├── prompts/                   # Prompts système pour chaque agent IA
│   ├── orchestrator.md
│   ├── scraper.md
│   ├── research.md
│   ├── enricher.md
│   ├── qualifier.md
│   └── outreach.md
│
├── config/
│   └── targets.json           # Cibles à traiter par le pipeline
│
├── src/
│   ├── run_orchestrator.py    # Point d'entrée principal du pipeline
│   ├── run_agent.py           # Exécuteur d'agent individuel
│   └── utils.py               # Fonctions utilitaires partagées
│
├── data/
│   ├── raw/                   # Sorties intermédiaires par agent (gitignored)
│   └── processed/             # Résultats fusionnés après pipeline (gitignored)
│
├── outputs/                   # Fichiers finaux JSON + CSV (gitignored)
│
├── docs/                      # Documentation business
│   ├── positioning.md
│   ├── offer.md
│   ├── prospecting-playbook.md
│   └── overlord-audit.md
│
├── configs/                   # Configuration business (agence, scoring)
│   ├── agency.json
│   └── niche-scorecard.json
│
├── scripts/                   # Templates d'outreach manuels
│   ├── cold-email.md
│   ├── dm-script.md
│   └── call-script.md
│
├── landing/
│   └── landing-copy.json      # Copy pour landing page Framer/Webflow
│
├── n8n/
│   └── patient-growth-intake-workflow.json   # Workflow n8n de qualification leads
│
└── requirements.txt
```

---

## Pipeline agentique — ordre d'exécution

```
scraper → research → enricher → qualifier → outreach → synthèse orchestrateur
```

| Agent | Rôle |
|-------|------|
| **scraper** | Collecte les données brutes de la cible (site, réseaux, contacts) |
| **research** | Analyse la présence digitale et la concurrence locale |
| **enricher** | Complète avec LTV estimée, budget, vitesse de décision |
| **qualifier** | Score le prospect sur 100 pts (HOT / WARM / COLD) |
| **outreach** | Génère les messages personnalisés (email, LinkedIn, Instagram) |

Chaque agent reçoit les données cumulées des agents précédents et retourne du JSON structuré.

---

## Lancer en local

### Prérequis

```bash
pip install -r requirements.txt
export OPENAI_API_KEY="sk-..."
```

### Configurer les cibles

Éditer `config/targets.json` avec les cliniques à prospecter.

### Lancer le pipeline complet

```bash
python src/run_orchestrator.py
```

### Lancer un agent individuel

```bash
python src/run_agent.py scraper \
  --input config/targets.json \
  --output data/raw/scraper_output.json
```

### Options

| Option | Description | Défaut |
|--------|-------------|--------|
| `--model` | Modèle OpenAI à utiliser | `gpt-4o-mini` |

---

## Lancer via GitHub Actions

1. Aller dans **Actions** → **Run AI Agent Pipeline**
2. Cliquer **Run workflow**
3. Choisir le modèle (optionnel, défaut : `gpt-4o-mini`)
4. Récupérer les outputs dans les **Artifacts** de la run

---

## Secrets requis

| Secret GitHub | Description |
|---------------|-------------|
| `OPENAI_API_KEY` | Clé API OpenAI (Settings → Secrets → Actions) |

---

## Outputs

| Chemin | Contenu |
|--------|---------|
| `data/raw/` | Sortie brute de chaque agent (par cible, horodatée) |
| `data/processed/` | Données fusionnées après pipeline complet |
| `outputs/pipeline_output_*.json` | Résultat final (JSON) |
| `outputs/pipeline_output_*.csv` | Résultat final (CSV, champs scalaires) |

---

## Stack no-code (kit agence)

| Outil | Usage |
|-------|-------|
| Framer / Webflow | Landing page |
| Meta Ads | Acquisition patient |
| Tally / Typeform | Formulaire qualifiant |
| n8n | Automatisation workflow leads |
| Calendly | Prise de RDV |
| Google Sheets / Airtable | CRM et reporting |
| WhatsApp Business API | Relances automatiques |

---

## Positionnement

> J'aide les cliniques esthétiques à générer plus de consultations qualifiées grâce à un système d'acquisition patient automatisé basé sur l'IA et la publicité Meta.

**Garantie** : 10 consultations qualifiées en 30 jours ou continuation gratuite.

---

## Points restants à améliorer

- [ ] Ajouter des tests unitaires pour `src/utils.py` et `src/run_agent.py`
- [ ] Tester le workflow n8n end-to-end avec de vrais leads
- [ ] Ajouter un canal de backup si Meta Ads est suspendu
- [ ] Documenter la conformité RGPD pour les données patient
- [ ] Ajouter un dashboard de monitoring des KPIs

