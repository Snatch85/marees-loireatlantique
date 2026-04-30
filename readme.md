# Marées Loire-Atlantique & France

Calculateur de marées harmonique pour les ports de Loire-Atlantique et de France.  
Site en ligne : **https://marees-loireatlantique.fr**  
Hébergement : Netlify (compte berry.guihal@gmail.com)

---

## Structure du projet

```
index.html                    → Page principale (calculateur de marées)
assets/
  site.css                    → Feuille de style principale (toutes les pages)
  script.js                   → Calcul harmonique + rendu interface (page index)
  site.js                     → Injection header/nav/footer (sous-pages de contenu)
  tide-calculator.js          → Module calculateur (expérimental)

reglementation/
  index.html                  → Réglementation pêche à pied DDTM 44 (créée v3)

peche-a-pied/
  index.html                  → Guide pêche à pied Loire-Atlantique

mentions-legales/
  index.html                  → Mentions légales + politique cookies

guides/                       → Articles et guides pratiques
marees-[ville]/               → Pages par port avec marées intégrées

service-worker.js             → Cache offline (stratégie network-first)
manifest.json                 → Configuration PWA
netlify.toml                  → Headers cache + sécurité Netlify
ads.txt                       → Fichier ads.txt (Google AdSense)
robots.txt                    → Instructions crawlers
sitemap.xml                   → Plan du site

android/                      → Projet Capacitor pour APK Android
www/                          → Copie du site pour Capacitor (webDir)
icons/                        → Icônes PWA (favicon, icon-192, icon-512)
```

---

## Déploiement Netlify

```bash
cd "C:\Users\33629\Desktop\Claude Cooode\marees-loire"

# 1. Synchroniser www/ avec la racine
copy index.html www\index.html

# 2. Déployer (site ID spécifié pour éviter de déployer sur le mauvais site)
netlify deploy --prod --site da1d08a0-dd25-4f88-865f-8a09b328055e --message "description"
```

> ⚠️ Le dossier `www/` doit toujours être synchronisé avec la racine avant de déployer (utilisé par Capacitor Android).

---

## Google AdSense

- **Publisher ID** : `ca-pub-1465276904717454`
- Statut : en cours de validation (avril 2026)
- Le script auto-ads est présent dans `<head>` de `index.html` et de la page `/reglementation/`
- Les `<ins class="adsbygoogle">` sont en place avec `data-ad-slot="AUTO"`
- Une fois le compte validé : remplacer `data-ad-slot="AUTO"` par les vrais ID d'unités AdSense

---

## Algorithme de calcul des marées

### Méthode harmonique (Foreman 1977 / SHOM)

La hauteur d'eau à l'instant *t* pour un port P est calculée par :

```
h(t) = Z0 + Σ fᵢ · Aᵢ · cos(Vᵢ(t) + uᵢ - Gᵢ)
```

Où :
- `Z0` = niveau moyen (m au-dessus du zéro hydrographique)
- `Aᵢ` = amplitude de chaque constituant harmonique (m)
- `Gᵢ` = déphasage Greenwich (°)
- `Vᵢ(t)` = argument d'équilibre astronomique (J2000.0)
- `fᵢ`, `uᵢ` = corrections nodales (Schureman 1958)

### Constituants inclus
M2, S2, N2, K2, NU2, MU2, L2, T2, 2N2, K1, O1, P1, Q1, M4, MN4, MS4, M6, MK3, MO3, MM, MF

### Coefficient SHOM
Le coefficient est calculé à partir du **marnage prévu à Brest** (port de référence officiel SHOM) :
```
coeff = round(marnage_Brest / 6.10 × 100)
```
Référence : marnage de vive-eau à Brest = 6.10 m → coefficient 100.

### Fichiers concernés
- `assets/script.js` : fonctions `astroArgs()`, `equilibriumArgs()`, `nodalCorrections()`, `tideHeight()`, `calcCoeff()`

---

## Historique des modifications

### v3 — Avril 2026
- ✅ Suppression complète de The Moneytizer et InMobi CMP (refus TheMoneytizer)
- ✅ Intégration Google AdSense (`ca-pub-1465276904717454`) avec auto-ads
- ✅ Séparation CSS/JS en fichiers externes (`assets/site.css`, `assets/script.js`)
- ✅ Création page `/reglementation/` avec données DDTM 44 réelles (tailles légales, quotas, zones)
- ✅ Correction canonical URL → `https://marees-loireatlantique.fr/`
- ✅ Suppression duplication script InMobi dans `<head>`
- ✅ 3e vague SVG dans le header pour effet plus naturel
- ✅ Animation pulse sur le badge coefficient
- ✅ Lien `/reglementation/` dans la navigation principale
- ✅ Correction bug `var(--blue-d)` dans renderToday → `var(--o900)`
- ✅ `assets/site.js` nettoyé (plus de Moneytizer)

### v2 — Avril 2026
- ✅ Refonte design complète (palette marine lumineuse, vagues SVG animées)
- ✅ Navigation sticky avec dropdown menus
- ✅ Graphique canvas redesigné (nouveau dégradé bleu)
- ✅ Accessibilité WCAG AA (skip link, aria-labels, focus-visible)
- ✅ Correction bug déploiement Netlify (mauvais site ID)

### v1 — Avril 2026
- ✅ Correction du calcul des coefficients : passage à la méthode SHOM officielle (marnage à Brest)
- ✅ Recalibration des constantes harmoniques des ports Loire-Atlantique (gradient-descent vs maree.info)
- ✅ Ajout constituants harmoniques supplémentaires : NU2, MU2, L2, T2, 2N2, MN4, M6, MK3, MO3
- ✅ Site créé avec calculateur harmonique multi-ports

---

## APK Android

1. Installer Android Studio
2. Lancer `BUILD_APK.bat` (dans le dossier racine)
3. L'APK utilise Capacitor avec `www/` comme webDir

---

## Propriétaire

- **Nom** : Berry Yann
- **Email** : berry.guihal@gmail.com
- **Site** : https://marees-loireatlantique.fr
- **Statut** : Particulier (pas de société)

---

## Contacts utiles

- **DDTM 44** : 02 40 67 26 26 — loire-atlantique.gouv.fr
- **SHOM officiel** : maree.shom.fr
- **Urgences en mer** : CROSS Étel — 196 (ou VHF canal 16)
