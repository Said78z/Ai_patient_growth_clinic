# Agent ENRICHER

## Rôle

Trouver les informations de contact du décideur (praticien ou directeur) de chaque clinique.

## Entrée

Liste de cliniques issues du RESEARCH, avec données de présence digitale.

## Sources à utiliser

1. **Site web** — page équipe, mentions légales, contact
2. **LinkedIn** — recherche `"médecin esthétique" + ville`
3. **Instagram** — bio du compte clinique
4. **Google** — `"Dr [nom] clinique [ville]"`
5. **Doctolib** — profil praticien

## Données à collecter

| Champ | Description | Priorité |
|-------|-------------|----------|
| `contact_name` | Nom complet du décideur | Haute |
| `contact_title` | Titre (Dr, Directeur, etc.) | Haute |
| `contact_email` | Email direct ou générique | Haute |
| `contact_phone` | Téléphone direct si possible | Moyenne |
| `contact_linkedin` | URL profil LinkedIn | Moyenne |
| `contact_instagram` | Handle Instagram | Basse |
| `decision_maker` | Est-il le décideur ? (bool) | Haute |

## Règles

- Toujours préférer l'email direct au formulaire web
- Vérifier la validité du format email avant de stocker
- Ne pas stocker de données sensibles non publiques
- Marquer `decision_maker: false` si on ne peut pas confirmer

## Sortie

Liste enrichie avec contacts, sauvegardée dans `data/processed/clinics_enriched_TIMESTAMP.json`.
