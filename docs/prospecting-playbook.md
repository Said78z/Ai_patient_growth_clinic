# Playbook Prospection — Sprint 14 Jours

## Objectif

Signer **1 client** en 14 jours en partant de zéro.

## KPIs du sprint

| Métrique | Cible |
|----------|-------|
| Prospects scrapés | 500 |
| Messages envoyés / jour | 100 |
| Taux de réponse | 5-10% |
| Calls bookés | 10 |
| Propositions envoyées | 5 |
| Clients signés | 1 |

---

## Jour 1–2 : Préparation

### Actions
- [ ] Finaliser la landing page (Framer/Webflow)
- [ ] Tester le workflow n8n de bout en bout
- [ ] Préparer les templates email/DM
- [ ] Créer la liste de scraping (sources ci-dessous)
- [ ] Configurer l'outil d'envoi (Lemlist / Instantly / manual)

### Sources de prospects
1. **Google Maps** — "clinique esthétique [ville]", "médecine esthétique [ville]"
2. **Doctolib** — praticiens listés en esthétique
3. **Pages Jaunes** — catégorie médecine esthétique
4. **LinkedIn** — médecins esthétiques, directeurs de clinique
5. **Instagram** — cliniques avec présence active

### Données à collecter
- Nom de la clinique
- Ville
- Nom du praticien / décideur
- Email (si disponible)
- LinkedIn (si disponible)
- Instagram (si disponible)
- Site web
- Note Google (signal de qualité)

---

## Jour 3–7 : Prospection intensive

### Canal 1 : Cold Email
- **Volume** : 50-100 emails/jour
- **Séquence** : 3 emails sur 7 jours
- **Template** : voir `scripts/cold-email.md`

### Canal 2 : LinkedIn DM
- **Volume** : 20-30 DM/jour
- **Approche** : connexion + message personnalisé
- **Template** : voir `scripts/dm-script.md`

### Canal 3 : Instagram DM
- **Volume** : 20-30 DM/jour
- **Approche** : engagement sur posts + DM
- **Cible** : cliniques avec 1K-50K followers

### Règles d'engagement
1. **Personnaliser chaque message** — mentionner la ville, le nom, un détail spécifique
2. **Pas de pitch en premier message** — apporter de la valeur d'abord
3. **Follow-up systématique** — relancer à J+3 et J+7
4. **Tracker tout** — chaque envoi, chaque réponse dans le CRM (Google Sheets)

---

## Jour 8–10 : Calls découverte

### Avant le call
- Rechercher la clinique (site, Google, Instagram, avis)
- Préparer 3 observations spécifiques
- Avoir le script prêt (voir `scripts/call-script.md`)

### Structure du call (15 min)
1. **Introduction** (2 min) — qui on est, pourquoi on appelle
2. **Découverte** (5 min) — questions sur leur acquisition actuelle
3. **Diagnostic** (3 min) — ce qui manque, ce qui se perd
4. **Proposition** (3 min) — présenter le système
5. **Next step** (2 min) — booker l'audit gratuit

### Questions clés
- "Comment vos patients vous trouvent-ils aujourd'hui ?"
- "Combien de nouvelles consultations par mois ?"
- "Vous faites de la pub en ligne actuellement ?"
- "Quel est votre acte le plus rentable ?"
- "Si vous pouviez avoir 10 consultations qualifiées de plus par mois, ça changerait quoi ?"

---

## Jour 11–12 : Propositions

### Format de proposition
1. Résumé du diagnostic (personnalisé)
2. Système proposé (adapté à leur cas)
3. Timeline de mise en place
4. Tarification
5. Garantie
6. Témoignages / études de cas (si disponibles)

### Envoi
- Email avec PDF + lien Calendly pour le call de closing
- Follow-up à J+1 par WhatsApp/SMS

---

## Jour 13–14 : Closing

### Objectifs
- Convertir au moins 1 proposition en client signé
- Collecter le paiement setup
- Planifier le kick-off

### Tactiques de closing
- **Urgence** : "On prend 3 cliniques max par ville pour éviter la concurrence"
- **Social proof** : "On lance avec une offre de lancement, prix normal = +50%"
- **Risque zéro** : "10 consultations ou on continue gratuitement"
- **Facilité** : "On a besoin de 30 min de votre temps pour le kick-off, on gère le reste"

---

## Tracking

### Google Sheets — Colonnes
| Colonne | Description |
|---------|-------------|
| Clinique | Nom |
| Ville | Localisation |
| Contact | Nom du décideur |
| Canal | Email / LinkedIn / Instagram |
| Date 1er contact | Date |
| Statut | Envoyé / Répondu / Call / Proposition / Signé / Perdu |
| Notes | Détails conversation |
| Next action | Prochaine étape + date |

### Revue quotidienne (15 min)
- Combien envoyés ?
- Combien de réponses ?
- Combien de calls bookés ?
- Quels messages marchent / ne marchent pas ?
- Ajuster les templates si taux de réponse < 3%
