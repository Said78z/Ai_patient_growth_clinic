# SCRAPER — Collecte de données publiques sur des cliniques cibles

Collecte uniquement des informations **publiquement disponibles** sur des cliniques :

| Champ | Description |
|---|---|
| `nom` | Nom de la structure |
| `site` | Site web |
| `ville` | Ville |
| `pays` | Pays |
| `type` | Type d'établissement |
| `specialites` | Spécialités visibles publiquement |
| `contact_url` | Page contact publique |
| `telephone` | Téléphone professionnel public |
| `email_public` | Email générique public si affiché |
| `linkedin` | Présence LinkedIn ou autre réseau professionnel public |
| `source` | URL source des données |

---

## Installation

```bash
pip install -r scraper/requirements.txt
```

---

## Utilisation

### Depuis un fichier de cibles JSON

```bash
python -m scraper.main --targets scraper/targets.example.json --output output/clinics
```

### Depuis des URLs en ligne de commande

```bash
python -m scraper.main --sites https://ma-clinique.fr https://autre-clinique.fr \
    --output output/clinics
```

### Options

```
--targets FILE     Fichier JSON de cibles (voir targets.example.json)
--sites URL [URL …] Un ou plusieurs URLs directs
--output PREFIX    Préfixe des fichiers de sortie (défaut: output/clinics)
--format {json,csv,both}  Format de sortie (défaut: both)
--delay SECONDS    Délai poli entre requêtes (défaut: 1.5 s)
--verbose / -v     Activer les logs de debug
```

---

## Format du fichier de cibles (`targets.json`)

```json
[
  {
    "nom": "Clinique Exemple Paris",
    "site": "https://example-clinic.fr",
    "ville": "Paris",
    "pays": "France",
    "type": "Clinique esthétique",
    "source": "https://example-clinic.fr"
  }
]
```

Seul le champ `site` est obligatoire. Tous les autres champs sont optionnels et
servent à pré-remplir les données sans requête HTTP supplémentaire. Si un champ
est fourni dans les cibles, il **prend la priorité** sur la valeur extraite du site.

---

## Format de sortie JSON

```json
[
  {
    "nom": "",
    "site": "",
    "ville": "",
    "pays": "",
    "type": "",
    "specialites": [],
    "contact_url": "",
    "telephone": "",
    "email_public": "",
    "linkedin": "",
    "source": ""
  }
]
```

---

## Politique de collecte

- ✅ Données **publiquement accessibles** uniquement (pages web indexables)
- ✅ Numéros de téléphone **professionnels** affichés publiquement
- ✅ Emails **génériques** (contact@, info@…) explicitement publiés à usage pro
- ❌ Pas de données privées, sensibles ou non publiques
- ❌ Pas d'emails personnels non explicitement publiés à usage professionnel
- ❌ Pas de contournement de robots.txt ou de protections anti-scraping

---

## Lancer les tests

```bash
pip install pytest
python -m pytest tests/test_scraper.py -v
```
