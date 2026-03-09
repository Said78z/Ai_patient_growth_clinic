# Agent SCRAPER

## Rôle

Collecter les données brutes des cliniques esthétiques en France à partir des sources publiques.

## Entrée

Configuration `config/targets.json` :
- `cities` : liste de villes cibles
- `niches` : types de cliniques à chercher
- `max_clinics_per_city` : nombre maximum de résultats par ville

## Sources à interroger (ordre de priorité)

1. **Google Maps / Places API** — `"clinique esthétique [ville]"`
2. **Doctolib** — praticiens en médecine esthétique par ville
3. **Pages Jaunes** — catégorie médecine esthétique
4. **Google My Business** — avis, horaires, contacts

## Données à collecter

| Champ | Description | Obligatoire |
|-------|-------------|-------------|
| `name` | Nom de la clinique | ✅ |
| `city` | Ville | ✅ |
| `niche` | Type de clinique | ✅ |
| `address` | Adresse complète | ❌ |
| `phone` | Téléphone | ❌ |
| `website` | URL du site web | ❌ |
| `google_rating` | Note Google (1-5) | ❌ |
| `google_reviews` | Nombre d'avis Google | ❌ |
| `source` | Source de la donnée | ✅ |
| `status` | Statut de traitement | ✅ |

## Règles

- Dédupliquer par nom + ville
- Ignorer les cliniques fermées ou en cessation d'activité
- Valider que le téléphone est au format français
- Tronquer si `max_clinics_per_city` est atteint

## Sortie

Liste de cliniques au format JSON, sauvegardée dans `data/raw/clinics_TIMESTAMP.json`.
