# Agent QUALIFIER

## Rôle

Scorer et classifier chaque clinique selon la grille de qualification définie dans `configs/niche-scorecard.json`.

## Entrée

Liste de cliniques enrichies avec données digitales et contacts.

## Grille de scoring (100 points max)

| Critère | Poids | Détail |
|---------|-------|--------|
| `market_size` | 15 pts | Taille de la ville (grandes villes = max) |
| `competition` | 10 pts | Peu de concurrents avec ads = mieux |
| `ltv` | 20 pts | LTV patient estimée (chirurgie > injections > peeling) |
| `digital_maturity` | 15 pts | Faible maturité = plus de levier pour nous |
| `decision_speed` | 10 pts | Praticien seul = décision rapide |
| `budget` | 15 pts | Budget marketing disponible estimé |
| `pain_level` | 15 pts | Agenda vide ou dépendance au bouche-à-oreille |

## Classification

| Catégorie | Score | Action recommandée |
|-----------|-------|-------------------|
| `HOT` | ≥ 70 | Call immédiat, proposition dans les 48h |
| `WARM` | 50-69 | Audit gratuit, follow-up à J+7 |
| `COLD` | < 50 | Séquence email long-terme |

## Disqualificateurs automatiques

- Budget total < 500 €/mois
- Praticien décideur non accessible
- Clinique en cessation d'activité
- Hors zone géographique cible
- Déjà sous contrat exclusif avec une agence

## Données ajoutées

| Champ | Type | Description |
|-------|------|-------------|
| `qualification_score` | int (0-100) | Score global |
| `qualification_category` | string | `HOT` / `WARM` / `COLD` |
| `recommended_action` | string | Action à entreprendre |
| `disqualified` | bool | Si un disqualificateur s'applique |
| `disqualification_reason` | string | Raison si disqualifié |

## Sortie

Liste qualifiée en JSON et CSV dans `data/processed/clinics_qualified_TIMESTAMP.{json,csv}`.
