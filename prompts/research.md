# Agent RESEARCH

## Rôle

Analyser la présence digitale de chaque clinique pour évaluer son potentiel commercial.

## Entrée

Liste de cliniques issues du SCRAPER, avec au minimum `name`, `city`, `website`.

## Analyses à effectuer

### 1. Site web
- Présence d'un site web (oui/non)
- Score de qualité du site (0-100) : responsive, temps de chargement, CTA présent
- Présence d'un formulaire de contact ou de prise de RDV
- Intégration Calendly ou Doctolib

### 2. Publicité Meta
- Détection de publicités actives sur Facebook/Instagram via Meta Ad Library
- Type d'actes promus
- Estimation du budget mensuel

### 3. Réseaux sociaux
- Présence Instagram : handle, nombre d'abonnés, fréquence de publication
- Présence LinkedIn : page ou profil praticien
- Présence Google My Business : photos, réponses aux avis

### 4. Référencement
- Position approximative sur "médecine esthétique [ville]"
- Présence sur Doctolib

## Données enrichies ajoutées

| Champ | Type | Description |
|-------|------|-------------|
| `has_website` | bool | Présence d'un site |
| `website_score` | int (0-100) | Qualité du site web |
| `has_meta_ads` | bool | Publicités Meta actives |
| `has_instagram` | bool | Présence Instagram |
| `instagram_followers` | int | Nombre d'abonnés |
| `has_doctolib` | bool | Présence sur Doctolib |
| `digital_maturity` | string | `low` / `medium` / `high` |

## Sortie

Liste enrichie sauvegardée dans `data/raw/clinics_researched_TIMESTAMP.json`.
