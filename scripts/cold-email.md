# Templates Cold Email

## Séquence 3 emails — Cliniques Esthétiques

---

### Email 1 — Premier contact (J+0)

**Objet :** {{clinique}} — une observation sur votre acquisition patient

**Corps :**

Bonjour {{prenom}},

J'ai regardé la présence en ligne de {{clinique}} à {{ville}} et j'ai remarqué quelque chose :

Vos avis Google sont excellents ({{note_google}}/5), mais votre visibilité digitale ne reflète pas la qualité de votre travail.

Concrètement, les patients qui cherchent "{{acte_principal}} {{ville}}" sur Google ou Meta ne vous trouvent probablement pas en premier.

On a mis en place un système d'acquisition patient automatisé pour des cliniques esthétiques similaires. Résultat : 10+ consultations qualifiées par mois en moins de 30 jours.

Est-ce que ça vaudrait 15 minutes de votre temps pour voir si c'est applicable à {{clinique}} ?

Bonne journée,
{{signature}}

---

### Email 2 — Relance valeur (J+3)

**Objet :** Re: {{clinique}} — une observation sur votre acquisition patient

**Corps :**

Bonjour {{prenom}},

Je me permets de revenir vers vous avec un point concret :

En analysant votre zone ({{ville}}), j'ai identifié que {{nombre_concurrents}} cliniques font déjà de la publicité Meta pour capter vos patients potentiels.

Ça ne veut pas dire que c'est trop tard — au contraire. La majorité de ces pubs sont mal ciblées et ne qualifient pas les leads correctement.

Un système bien calibré peut vous positionner devant en quelques jours.

Si le sujet vous intéresse, je peux vous faire un audit rapide gratuit de votre situation digitale.

{{signature}}

---

### Email 3 — Dernière relance (J+7)

**Objet :** Dernier message — {{clinique}}

**Corps :**

Bonjour {{prenom}},

Dernier message, promis.

Je comprends que le quotidien d'une clinique ne laisse pas beaucoup de temps pour le marketing digital. C'est exactement pour ça que notre système est 100% automatisé — on s'occupe de tout, vous ne faites que les consultations.

Si c'est le bon moment : un call de 15 min → {{lien_calendly}}
Si ce n'est pas le moment : pas de souci, je ne relancerai plus.

Bonne continuation,
{{signature}}

---

## Variables à personnaliser

| Variable | Source |
|----------|--------|
| `{{clinique}}` | Nom de la clinique (scraping) |
| `{{prenom}}` | Prénom du praticien |
| `{{ville}}` | Ville de la clinique |
| `{{note_google}}` | Note Google Maps |
| `{{acte_principal}}` | Acte le plus mis en avant |
| `{{nombre_concurrents}}` | Nombre de concurrents avec ads Meta dans la zone |
| `{{lien_calendly}}` | Lien Calendly personnel |
| `{{signature}}` | Signature email complète |

## Règles

- Ne jamais envoyer plus de 50 emails/jour par boîte
- Utiliser un domaine secondaire pour le cold email
- Warm-up du domaine pendant 2 semaines avant le lancement
- Vérifier les emails avant envoi (Neverbounce, ZeroBounce)
- Tracker les ouvertures et clics
- Arrêter la séquence dès qu'il y a une réponse (positive ou négative)
