# Projet : Marées Loire-Atlantique

## Sites Netlify — IDs CRITIQUES

| Site | ID Netlify | URL |
|------|-----------|-----|
| **Marées Loire-Atlantique** | `da1d08a0-dd25-4f88-865f-8a09b328055e` | https://marees-loireatlantique.fr |
| **Nuits Blanches Tapis Rouge** | `53ef17d6-b403-402e-8abe-682ac56d49da` | https://nuits-blanches-tapis-rouge.com |

⚠️ **TOUJOURS utiliser `--site <ID>` explicitement** pour éviter tout déploiement croisé.

---

## Déploiement — Site marées

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
Set-Location "C:\Users\33629\Desktop\Claude Cooode\marees-loire"

# 1. Synchroniser www/ avec la racine
copy index.html www\index.html

# 2. Déployer
netlify deploy --prod --site da1d08a0-dd25-4f88-865f-8a09b328055e --message "description"
```

## Déploiement — Site livre (si besoin)

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
Set-Location "C:\Users\33629\Desktop\Claude Cooode\nuits-blanches-site"
netlify deploy --prod --site 53ef17d6-b403-402e-8abe-682ac56d49da --message "description"
```

---

## Publicité — Google AdSense

- **Publisher ID** : `ca-pub-1465276904717454`
- Statut : en cours de validation (avril 2026)
- The Moneytizer : **supprimé** (refus catégorique de leur part)
- Une fois validé : remplacer `data-ad-slot="AUTO"` par les vrais IDs dans `index.html` et `reglementation/index.html`

---

## Structure du projet

```
index.html              → page principale (calculateur marées)
assets/
  site.css              → CSS global (toutes pages)
  script.js             → calcul harmonique + interface (page index)
  site.js               → injection header/nav/footer (sous-pages)
reglementation/         → réglementation DDTM 44 (tailles légales, quotas)
peche-a-pied/           → guide pêche à pied
guides/                 → articles SEO
  coefficient-maree/    → guide coefficient (touristes débutants)
  spots-peche-pied-loire-atlantique/  → meilleurs spots de pêche
mentions-legales/       → mentions légales + cookies
marees-[ville]/         → pages par port
netlify.toml            → headers cache + sécurité
ads.txt                 → Google AdSense
service-worker.js       → cache offline (network-first)
manifest.json           → PWA
android/                → projet Capacitor APK
www/                    → copie du site pour Capacitor (toujours sync avec racine)
```

---

## Propriétaire

- **Nom** : Berry Yann
- **Email** : berry.guihal@gmail.com
- **Site** : https://marees-loireatlantique.fr
- **Statut** : Particulier (pas de société)

---

## Articles à écrire (en cours)

- [x] Guide coefficient de marée (touristes débutants)
- [x] Meilleurs spots pêche à pied Loire-Atlantique
- [ ] Calendrier grandes marées 2026
- [ ] Sécurité en bord de mer
- [ ] Guide marées Saint-Nazaire
