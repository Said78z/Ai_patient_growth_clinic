# Ai_patient_growth_clinic

Starter repo pour lancer une agence **AI Patient Growth System** ciblant les cliniques esthétiques en France.

## Structure
- `docs/positioning.md` : niche, offre, ICP, promesse
- `docs/offer.md` : offre high-ticket prête à vendre
- `docs/prospecting-playbook.md` : plan 14 jours
- `scripts/qualifier-prompt.md` : prompt agent IA QUALIFIER (scoring commercial)
- `scripts/` : cold email, DM, script call
- `configs/qualifier.json` : critères et seuils de scoring cliniques
- `configs/qualifier-output.schema.json` : schéma JSON de validation des sorties QUALIFIER
- `configs/agency.json` : configuration business
- `configs/niche-scorecard.json` : scoring de niche
- `data/clinics-qualified.json` : exemples de cliniques scorées
- `landing/landing-copy.json` : copy prête pour landing page
- `n8n/qualifier-workflow.json` : workflow n8n QUALIFIER (scoring IA + Google Sheets)
- `n8n/patient-growth-intake-workflow.json` : workflow n8n de qualification lead

## QUALIFIER — Scoring Commercial Cliniques

L'agent **QUALIFIER** score chaque clinique de 0 à 100 et la classe en segment `HOT`, `WARM` ou `COLD` pour prioriser la prospection.

### Critères (total 100 pts)

| Critère | Poids | Description |
|---|---|---|
| Présence digitale | 20 pts | Site, Google Maps, avis, réseaux sociaux, pubs |
| Site exploitable | 20 pts | Pages soins, CTA, formulaire, prise de RDV |
| Signaux de croissance | 20 pts | Pubs Meta récentes, nouveau soin, second site |
| Clarté du positionnement | 15 pts | Spécialisation, message différenciant, tarifs |
| Facilité de contact | 15 pts | Email direct, WhatsApp, formulaire, LinkedIn |
| Complexité des besoins | 10 pts | Multi-sites, concurrence forte, gamme étendue |

### Segments

| Segment | Score | Priorité contact |
|---|---|---|
| **HOT** | 70 – 100 | haute |
| **WARM** | 40 – 69 | moyenne |
| **COLD** | 0 – 39 | basse |

### Format de sortie

```json
{
  "nom": "Nom de la clinique",
  "score": 84,
  "segment": "HOT",
  "raisons": [
    "Site web moderne avec prise de RDV et pages soins détaillées",
    "Publicités Meta actives détectées"
  ],
  "priorite_contact": "haute"
}
```

### Utilisation avec n8n

1. Importer `n8n/qualifier-workflow.json` dans votre instance n8n.
2. Configurer la variable `QUALIFIER_SHEET_ID` avec l'ID de votre Google Sheet.
3. Connecter un credential OpenAI valide au nœud **IA — QUALIFIER Score**.
4. Envoyer une requête POST au webhook `/qualifier` avec les données de la clinique :

```json
{
  "clinic_name": "Clinique Éclat Paris",
  "city": "Paris 16e",
  "website_url": "https://eclat-paris.fr",
  "google_reviews_count": 312,
  "google_rating": 4.8,
  "meta_ads_active": "oui",
  "services_description": "Botox, fillers, laser",
  "contact_email": "contact@eclat-paris.fr"
}
```

## Positionnement
> J'aide les cliniques esthétiques à générer plus de consultations qualifiées grâce à un système d'acquisition patient automatisé basé sur l'IA et la publicité Meta.

## Stack minimale
- Framer / Webflow
- Meta Ads
- Tally / Typeform
- n8n
- Calendly
- Google Sheets / Airtable
- WhatsApp / email / SMS provider

## Sprint 14 jours
1. Lancer landing
2. Scraper 500 prospects
3. Envoyer 100 messages / jour
4. Prendre 10 calls
5. Signer 1 client
