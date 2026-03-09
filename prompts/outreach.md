# Agent OUTREACH

## Rôle

Générer du contenu d'outreach personnalisé pour chaque clinique HOT et WARM.

## Entrée

Liste de cliniques qualifiées (HOT + WARM uniquement).

## Contenu à générer

### Email (canal principal)

- **Objet** : court, personnalisé, non-commercial
- **Corps** : 4-5 phrases max, une observation spécifique sur la clinique
- **CTA** : lien Calendly ou question ouverte
- **Template** : voir `scripts/cold-email.md`

### LinkedIn DM (canal secondaire)

- Message de connexion court (< 300 caractères)
- Message post-connexion avec valeur concrète
- Template : voir `scripts/dm-script.md`

### Instagram DM (canal tertiaire pour cliniques actives sur Instagram)

- Message court, ton informel
- Référence à un post récent si possible

## Règles de personnalisation

1. Mentionner le nom de la clinique et la ville
2. Inclure la note Google si > 4.0
3. Adapter le canal selon la présence digitale détectée
4. Ne pas envoyer les 3 canaux en même temps — espacer de 2 jours

## Variables disponibles

| Variable | Source |
|----------|--------|
| `{{clinique}}` | `name` |
| `{{ville}}` | `city` |
| `{{prenom}}` | `contact_name` (prénom) |
| `{{note_google}}` | `google_rating` |
| `{{acte_principal}}` | Déduit du `niche` |
| `{{lien_calendly}}` | Variable d'env `CALENDLY_URL` |

## Données ajoutées

| Champ | Type | Description |
|-------|------|-------------|
| `outreach_email_subject` | string | Objet de l'email personnalisé |
| `outreach_email_body` | string | Corps de l'email personnalisé |
| `outreach_linkedin_msg` | string | Message LinkedIn |
| `outreach_channel` | string | Canal recommandé en priorité |
| `outreach_status` | string | `ready` / `sent` / `replied` |

## Sortie

Liste avec contenu outreach en JSON et CSV dans `outputs/outreach_TIMESTAMP.{json,csv}`.
