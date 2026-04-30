# -*- coding: utf-8 -*-
"""Genere les pages SEO villes pour le site marees-loire-atlantique."""
import os, re

CITIES = [
    {
        "slug": "marees-saint-nazaire",
        "port": "SAINT-NAZAIRE",
        "name": "Saint-Nazaire",
        "dept": "Loire-Atlantique (44)",
        "cp": "44600",
        "lat": "47.2736",
        "lon": "-2.2136",
        "desc": "Grand port industriel de Loire-Atlantique, Saint-Nazaire offre un marnage de vive-eau d'environ 5,2 m. Port de reference pour le departement du 44.",
        "marnage_ve": "5,2 m",
        "marnage_me": "2,1 m",
        "niveau": "3,15 m",
        "activites": "Peche a pied, plaisance, sous-marines",
        "plages": "Grande Plage, Plage de Villees Martin",
        "tips": "Le front de mer de Saint-Nazaire offre un acces facile aux rochers lors des grandes marees. Coefficient ideal >= 90 pour decouvrir les zones rocheuses.",
    },
    {
        "slug": "marees-le-croisic",
        "port": "LE-CROISIC",
        "name": "Le Croisic",
        "dept": "Loire-Atlantique (44)",
        "cp": "44490",
        "lat": "47.2927",
        "lon": "-2.5127",
        "desc": "Charmant port de peche de la presqu'ile guerandaise, Le Croisic est ideal pour la peche a pied et la plaisance. Marnage de vive-eau d'environ 5,0 m.",
        "marnage_ve": "5,0 m",
        "marnage_me": "2,0 m",
        "niveau": "3,03 m",
        "activites": "Peche a pied, voile, kayak, peche au lancer",
        "plages": "Plage de Port-Lin, Plage de la Govelle",
        "tips": "Les rochers de la cote sauvage se decouvrent magnifiquement lors des grandes marees. Attention aux remontees rapides avec coefficient >= 100.",
    },
    {
        "slug": "marees-pornic",
        "port": "PORNIC",
        "name": "Pornic",
        "dept": "Loire-Atlantique (44)",
        "cp": "44210",
        "lat": "47.1121",
        "lon": "-2.1048",
        "desc": "Station balneaire prisee de Loire-Atlantique, Pornic dispose d'un port de plaisance actif. Marnage de vive-eau d'environ 4,85 m, ideal pour la peche a pied.",
        "marnage_ve": "4,85 m",
        "marnage_me": "1,85 m",
        "niveau": "2,95 m",
        "activites": "Peche a pied, voile, baignade, randonnee cote",
        "plages": "Plage de la Source, Plage de Goviro, Plage du Birocheres",
        "tips": "La plage de Noirmoutier et les vasnieres de Pornic offrent palourdes et coques en abondance lors des marees de coefficient > 85.",
    },
    {
        "slug": "marees-la-turballe",
        "port": "LA-TURBALLE",
        "name": "La Turballe",
        "dept": "Loire-Atlantique (44)",
        "cp": "44420",
        "lat": "47.3500",
        "lon": "-2.5133",
        "desc": "Port de peche important du pays Guerandais, La Turballe accueille une flottille sardiniere. Marnage similaire au Croisic, ideal pour la peche a pied.",
        "marnage_ve": "5,0 m",
        "marnage_me": "1,9 m",
        "niveau": "3,04 m",
        "activites": "Peche a pied, peche embarquee, voile",
        "plages": "La Grande Plage, Le Pen Bron",
        "tips": "Les rochers du Pen Bron se decouvrent lors des basses mers de coefficient >= 80. Bonne zone pour les bigorneaux et crabes.",
    },
    {
        "slug": "marees-piriac-sur-mer",
        "port": "PIRIAC",
        "name": "Piriac-sur-Mer",
        "dept": "Loire-Atlantique (44)",
        "cp": "44420",
        "lat": "47.3800",
        "lon": "-2.5400",
        "desc": "Petit port breton aux maisons de granit, Piriac-sur-Mer est le point le plus au nord de la Loire-Atlantique. Conditions de maree identiques a La Turballe.",
        "marnage_ve": "5,0 m",
        "marnage_me": "1,9 m",
        "niveau": "3,04 m",
        "activites": "Peche a pied, voile, randonnee littorale",
        "plages": "Plage du Castelli, Plage de Loscolo",
        "tips": "Le sentier cotier de Piriac donne acces a de nombreux rochers decouverts en basse mer. Excellent spot pour palourdes et ormeaux.",
    },
    {
        "slug": "marees-prefailles",
        "port": "PREFAILLES",
        "name": "Prefailles",
        "dept": "Loire-Atlantique (44)",
        "cp": "44770",
        "lat": "47.1300",
        "lon": "-2.2100",
        "desc": "Village cotier face a l'estuaire de la Loire, Prefailles offre un acces direct a la pointe Saint-Gildas, lieu de forts courants lors des grandes marees.",
        "marnage_ve": "4,87 m",
        "marnage_me": "1,87 m",
        "niveau": "2,97 m",
        "activites": "Peche a pied, surf, kitesurf",
        "plages": "Grande Plage, Plage du Bois Soleil",
        "tips": "La pointe Saint-Gildas genere de forts courants lors des grandes marees. Ne jamais pecher seul dans cette zone avec coefficient >= 95.",
    },
    {
        "slug": "marees-saint-brevin-les-pins",
        "port": "SAINT-BREVIN",
        "name": "Saint-Brevin-les-Pins",
        "dept": "Loire-Atlantique (44)",
        "cp": "44250",
        "lat": "47.2300",
        "lon": "-2.1700",
        "desc": "Face a Saint-Nazaire de l'autre cote de l'estuaire, Saint-Brevin-les-Pins dispose de vastes plages de sable. Marnage legerement superieur a la moyenne du 44.",
        "marnage_ve": "5,1 m",
        "marnage_me": "2,0 m",
        "niveau": "3,10 m",
        "activites": "Peche a pied, baignade, surf, voile",
        "plages": "Plage des Rochelets, Plage de Mindin, Plage de La Courance",
        "tips": "Les vasnieres de Saint-Brevin sont riches en coques et palourdes. Verifiez le classement sanitaire DDPP avant toute recolte.",
    },
    {
        "slug": "marees-la-baule",
        "port": "LA-BAULE",
        "name": "La Baule-Escoublac",
        "dept": "Loire-Atlantique (44)",
        "cp": "44500",
        "lat": "47.2800",
        "lon": "-2.4000",
        "desc": "Celebre station balneaire de la Cote d'Amour, La Baule possede l'une des plus belles baies d'Europe. La grande plage de 9 km se decouvre progressivement a maree basse.",
        "marnage_ve": "5,0 m",
        "marnage_me": "1,9 m",
        "niveau": "3,00 m",
        "activites": "Baignade, voile, char a voile, peche a pied",
        "plages": "La Grande Plage (9 km), Plage Benodet",
        "tips": "La baie de La Baule est tres douce en pente. Le decouvrement est progressif sur plusieurs centaines de metres. Peche aux coques en periode de vive-eau.",
    },
    {
        "slug": "marees-paimboeuf",
        "port": "PAIMBOEUF",
        "name": "Paimboeuf",
        "dept": "Loire-Atlantique (44)",
        "cp": "44560",
        "lat": "47.2900",
        "lon": "-2.0200",
        "desc": "Port fluvial situe dans l'estuaire de la Loire, Paimboeuf subit l'influence combinee de la maree et du fleuve. Le marnage y est legerement superieur a l'embouchure.",
        "marnage_ve": "5,3 m",
        "marnage_me": "2,1 m",
        "niveau": "3,20 m",
        "activites": "Peche en estuaire, promenade, decouverte de la faune estuarienne",
        "plages": "Berges de l'estuaire",
        "tips": "Attention : l'estuaire de la Loire comporte des courants importants. La peche y est reglementee. Consultez la federation de peche locale.",
    },
    {
        "slug": "peche-a-pied",
        "port": "LE-CROISIC",
        "name": "Peche a pied en Loire-Atlantique",
        "dept": "Loire-Atlantique (44)",
        "cp": "44000",
        "lat": "47.2927",
        "lon": "-2.5127",
        "desc": "Guide complet pour la peche a pied en Loire-Atlantique : zones autorisees, tailles minimales, quotas, securite et meilleurs coefficients pour la recolte.",
        "marnage_ve": "5,0 m",
        "marnage_me": "2,0 m",
        "niveau": "3,03 m",
        "activites": "Palourdes, coques, moules, bigorneaux, ormeaux, crabes, crevettes",
        "plages": "Croisic, Piriac, Prefailles, La Baule, Saint-Brevin",
        "tips": "Les meilleurs coefficients pour la peche a pied en Loire-Atlantique sont entre 90 et 120. Privilegiez les basses mers diurnes pour la securite.",
    },
]

# Lire le contenu JS complet du site principal (pour inclusion)
with open("index.html", encoding="utf-8") as f:
    main_html = f.read()

# Extraire uniquement le bloc <script> principal (le gros JS de calcul)
js_match = re.search(r'<script>\s*// .*?CALCUL.*?</script>', main_html, re.DOTALL)
main_js = js_match.group(0) if js_match else ""

# Extraire le CSS principal
css_match = re.search(r'<style>(.*?)</style>', main_html, re.DOTALL)
main_css = css_match.group(1) if css_match else ""

# Template HTML pour chaque page ville
def make_page(city):
    is_peche = city["slug"] == "peche-a-pied"
    h1 = f"Marees a {city['name']}" if not is_peche else "Peche a pied en Loire-Atlantique"
    title = f"Marees {city['name']} 2026 – Horaires, Coefficients & Hauteurs | Loire-Atlantique"
    desc = city['desc']

    schema = f"""{{
  "@context": "https://schema.org",
  "@type": "Dataset",
  "name": "Horaires des marees a {city['name']}",
  "description": "{city['desc']}",
  "spatialCoverage": {{
    "@type": "Place",
    "name": "{city['name']}",
    "address": {{
      "@type": "PostalAddress",
      "addressLocality": "{city['name']}",
      "postalCode": "{city['cp']}",
      "addressRegion": "Loire-Atlantique",
      "addressCountry": "FR"
    }},
    "geo": {{
      "@type": "GeoCoordinates",
      "latitude": "{city['lat']}",
      "longitude": "{city['lon']}"
    }}
  }}
}}"""

    breadcrumb = f"""{{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {{"@type":"ListItem","position":1,"name":"Accueil","item":"https://marees-loire-atlantique.netlify.app/"}},
    {{"@type":"ListItem","position":2,"name":"{city['name']}","item":"https://marees-loire-atlantique.netlify.app/{city['slug']}/"}}
  ]
}}"""

    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>{title}</title>
<meta name="description" content="{desc}"/>
<meta name="keywords" content="marees {city['name'].lower()}, horaires marees {city['name'].lower()}, coefficient maree {city['name'].lower()}, peche a pied {city['name'].lower()}, basse mer {city['name'].lower()}, {city['dept'].lower()}"/>
<link rel="canonical" href="https://marees-loire-atlantique.netlify.app/{city['slug']}/"/>
<meta name="robots" content="index, follow"/>
<meta name="geo.region" content="FR-44"/>
<meta name="geo.placename" content="{city['name']}, {city['dept']}"/>
<meta property="og:type" content="website"/>
<meta property="og:title" content="{title}"/>
<meta property="og:description" content="{desc}"/>
<meta property="og:url" content="https://marees-loire-atlantique.netlify.app/{city['slug']}/"/>
<meta property="og:locale" content="fr_FR"/>
<meta property="og:site_name" content="Marees Loire-Atlantique"/>
<link rel="manifest" href="/manifest.json"/>
<meta name="theme-color" content="#1A6B8A"/>
<meta name="apple-mobile-web-app-capable" content="yes"/>
<meta name="apple-mobile-web-app-title" content="Marees 44"/>
<link rel="apple-touch-icon" href="/icons/icon-192.png"/>
<link rel="icon" type="image/png" sizes="32x32" href="/icons/favicon-32.png"/>
<script type="application/ld+json">{schema}</script>
<script type="application/ld+json">{breadcrumb}</script>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet"/>
<style>{main_css}</style>
</head>
<body>

<div class="ad-top">
  <div class="ad-slot ad-banner">
    Espace publicitaire 728x90 — Google AdSense / The Moneytizer
  </div>
</div>

<header>
  <div class="header-inner">
    <div class="logo">
      <span class="logo-wave">&#127754;</span>
      <div class="logo-text">
        <h1>Marees Loire-Atlantique</h1>
        <p>Horaires · Coefficients · Hauteurs d'eau</p>
      </div>
    </div>
    <nav class="header-nav">
      <a href="/">Accueil</a>
      <a href="#today">Aujourd'hui</a>
      <a href="#semaine">7 jours</a>
      <a href="/peche-a-pied/">Peche a pied</a>
    </nav>
  </div>
</header>

<div class="container">
  <div class="main-col">

    <!-- Fil d'Ariane -->
    <nav style="font-size:.75rem;color:var(--text-l);margin-bottom:-.2rem">
      <a href="/" style="color:var(--blue)">Accueil</a>
      <span style="margin:0 .4rem">›</span>
      <span>{city['name']}</span>
    </nav>

    <!-- Avertissement SHOM -->
    <div style="background:#FFF3CD;border:1px solid #F0A500;border-radius:8px;padding:.8rem 1rem;display:flex;gap:.7rem;align-items:flex-start">
      <span style="font-size:1.1rem;flex-shrink:0">&#9888;&#65039;</span>
      <p style="font-size:.76rem;color:#7A4F00;line-height:1.5">
        <strong>Donnees indicatives.</strong> Ces horaires sont calcules par methode harmonique et ne remplacent pas les publications officielles du
        <a href="https://maree.shom.fr" target="_blank" rel="noopener" style="color:#5A3A00;font-weight:700">SHOM (maree.shom.fr)</a>.
        Pour la navigation et la peche professionnelle, consultez toujours le SHOM avec une connexion active.
      </p>
    </div>

    <!-- En-tête ville -->
    <div style="background:var(--blue-l);border:1px solid var(--border);border-radius:12px;padding:1.4rem">
      <h1 style="font-size:1.25rem;font-weight:800;color:var(--blue-d);margin-bottom:.5rem">{h1}</h1>
      <p style="font-size:.82rem;color:var(--text-m);line-height:1.6;margin-bottom:.8rem">{city['desc']}</p>
      <div style="display:flex;gap:.6rem;flex-wrap:wrap">
        <span style="font-size:.72rem;background:white;border:1px solid var(--border);padding:.3rem .6rem;border-radius:5px;color:var(--text-m)">
          &#128205; {city['lat']} {city['lon']}
        </span>
        <span style="font-size:.72rem;background:white;border:1px solid var(--border);padding:.3rem .6rem;border-radius:5px;color:var(--text-m)">
          &#127754; Marnage VE ~{city['marnage_ve']}
        </span>
        <span style="font-size:.72rem;background:white;border:1px solid var(--border);padding:.3rem .6rem;border-radius:5px;color:var(--text-m)">
          &#128678; Activites : {city['activites']}
        </span>
      </div>
    </div>

    <!-- Sélecteur port + date -->
    <div class="port-bar">
      <label>Port :</label>
      <select class="port-select" id="portSelect">
        <optgroup label="-- Loire-Atlantique (44) --">
          <option value="SAINT-NAZAIRE"{' selected' if city['port']=='SAINT-NAZAIRE' else ''}>Saint-Nazaire</option>
          <option value="LE-CROISIC"{' selected' if city['port']=='LE-CROISIC' else ''}>Le Croisic</option>
          <option value="LA-BAULE"{' selected' if city['port']=='LA-BAULE' else ''}>La Baule-Escoublac</option>
          <option value="BATZ"{' selected' if city['port']=='BATZ' else ''}>Batz-sur-Mer</option>
          <option value="LE-POULIGUEN"{' selected' if city['port']=='LE-POULIGUEN' else ''}>Le Pouliguen</option>
          <option value="LA-TURBALLE"{' selected' if city['port']=='LA-TURBALLE' else ''}>La Turballe</option>
          <option value="PIRIAC"{' selected' if city['port']=='PIRIAC' else ''}>Piriac-sur-Mer</option>
          <option value="PORNIC"{' selected' if city['port']=='PORNIC' else ''}>Pornic</option>
          <option value="PREFAILLES"{' selected' if city['port']=='PREFAILLES' else ''}>Prefailles</option>
          <option value="SAINT-BREVIN"{' selected' if city['port']=='SAINT-BREVIN' else ''}>Saint-Brevin-les-Pins</option>
          <option value="PAIMBOEUF"{' selected' if city['port']=='PAIMBOEUF' else ''}>Paimboeuf</option>
          <option value="SAINT-GILDAS"{' selected' if city['port']=='SAINT-GILDAS' else ''}>Saint-Gildas (Pointe)</option>
        </optgroup>
        <optgroup label="-- Bretagne --">
          <option value="SAINT-MALO">Saint-Malo</option>
          <option value="BREST">Brest</option>
          <option value="LORIENT">Lorient</option>
        </optgroup>
        <optgroup label="-- Normandie --">
          <option value="CHERBOURG">Cherbourg</option>
          <option value="LE-HAVRE">Le Havre</option>
          <option value="GRANVILLE">Granville</option>
        </optgroup>
        <optgroup label="-- Atlantique Sud --">
          <option value="LA-ROCHELLE">La Rochelle</option>
          <option value="BORDEAUX">Bordeaux (Pauillac)</option>
        </optgroup>
      </select>
      <input type="date" class="date-input" id="dateInput"/>
      <button class="refresh-btn" onclick="loadTides()">&#128260; Actualiser</button>
    </div>

    <div class="today-card" id="today">
      <div class="today-header">
        <div>
          <div class="today-title" id="todayTitle">Marees du jour</div>
          <div class="today-date" id="todayDate">Chargement...</div>
        </div>
        <div class="coeff-badge" id="coeffBadge">Coeff. -</div>
      </div>
      <div class="today-tides" id="todayTides">
        <div style="grid-column:1/-1;padding:2rem;text-align:center;color:var(--text-l)">Chargement...</div>
      </div>
    </div>

    <div class="chart-card">
      <div class="chart-title">Courbe de maree - 24h</div>
      <canvas id="tideChart"></canvas>
      <div class="chart-legend">
        <div class="leg-item"><div class="leg-dot" style="background:var(--blue)"></div>Pleine mer</div>
        <div class="leg-item"><div class="leg-dot" style="background:var(--sea)"></div>Basse mer</div>
        <div class="leg-item"><div class="leg-dot" style="background:#E67E22"></div>Niveau actuel</div>
      </div>
    </div>

    <div class="ad-slot ad-rect">
      Espace publicitaire - Google AdSense / The Moneytizer
    </div>

    <!-- Info locale ville -->
    <div class="info-card">
      <h3>&#128204; Conseils pour {city['name']}</h3>
      <p>{city['tips']}</p>
      <p><strong>Plages et acces :</strong> {city['plages']}</p>
      <p><strong>Activites :</strong> {city['activites']}</p>
      <p style="margin-top:.5rem;font-size:.72rem;color:var(--blue-d)">
        <strong>&#9888; Securite :</strong> Verifiez toujours la meteo avant une sortie en mer ou en peche a pied.
        En cas d'urgence en mer : <strong>composez le 196</strong> (CROSS).
      </p>
    </div>

    <div class="week-card" id="semaine">
      <div class="week-header"><h2>&#128197; Marees sur 7 jours - {city['name']}</h2></div>
      <div id="weekTable"><div style="padding:2rem;text-align:center;color:var(--text-l)">Chargement...</div></div>
    </div>

    <!-- Liens vers autres ports du 44 -->
    <div style="background:var(--white);border:1px solid var(--border);border-radius:12px;padding:1.2rem">
      <h3 style="font-size:.88rem;font-weight:700;color:var(--text-m);margin-bottom:.8rem">
        &#127754; Autres ports de Loire-Atlantique
      </h3>
      <div style="display:flex;flex-wrap:wrap;gap:.4rem">
        <a href="/marees-saint-nazaire/" style="background:var(--blue-l);color:var(--blue-d);padding:.3rem .7rem;border-radius:5px;font-size:.76rem;font-weight:500;text-decoration:none">Saint-Nazaire</a>
        <a href="/marees-le-croisic/" style="background:var(--blue-l);color:var(--blue-d);padding:.3rem .7rem;border-radius:5px;font-size:.76rem;font-weight:500;text-decoration:none">Le Croisic</a>
        <a href="/marees-pornic/" style="background:var(--blue-l);color:var(--blue-d);padding:.3rem .7rem;border-radius:5px;font-size:.76rem;font-weight:500;text-decoration:none">Pornic</a>
        <a href="/marees-la-turballe/" style="background:var(--blue-l);color:var(--blue-d);padding:.3rem .7rem;border-radius:5px;font-size:.76rem;font-weight:500;text-decoration:none">La Turballe</a>
        <a href="/marees-piriac-sur-mer/" style="background:var(--blue-l);color:var(--blue-d);padding:.3rem .7rem;border-radius:5px;font-size:.76rem;font-weight:500;text-decoration:none">Piriac-sur-Mer</a>
        <a href="/marees-saint-brevin-les-pins/" style="background:var(--blue-l);color:var(--blue-d);padding:.3rem .7rem;border-radius:5px;font-size:.76rem;font-weight:500;text-decoration:none">Saint-Brevin</a>
        <a href="/marees-prefailles/" style="background:var(--blue-l);color:var(--blue-d);padding:.3rem .7rem;border-radius:5px;font-size:.76rem;font-weight:500;text-decoration:none">Prefailles</a>
        <a href="/marees-la-baule/" style="background:var(--blue-l);color:var(--blue-d);padding:.3rem .7rem;border-radius:5px;font-size:.76rem;font-weight:500;text-decoration:none">La Baule</a>
        <a href="/peche-a-pied/" style="background:var(--sea-l);color:#1A5C3A;padding:.3rem .7rem;border-radius:5px;font-size:.76rem;font-weight:600;text-decoration:none">Peche a pied 44</a>
      </div>
    </div>

  </div>

  <div class="side-col">
    <div class="ad-slot ad-square">
      Espace publicitaire<br/>300x250<br/>Google AdSense
    </div>
    <div class="coeff-card">
      <h3>Echelle des coefficients</h3>
      <div class="coeff-scale">
        <div class="cs-row"><span class="cs-label">Tres forte</span><div class="cs-bar" style="background:#0F4F6B;width:100%"></div><span class="cs-range">100-120</span></div>
        <div class="cs-row"><span class="cs-label">Vive-eau</span><div class="cs-bar" style="background:#1A6B8A;width:80%"></div><span class="cs-range">70-99</span></div>
        <div class="cs-row"><span class="cs-label">Moyenne</span><div class="cs-bar" style="background:#4AA8C4;width:58%"></div><span class="cs-range">45-69</span></div>
        <div class="cs-row"><span class="cs-label">Morte-eau</span><div class="cs-bar" style="background:#2A9D8F;width:35%"></div><span class="cs-range">20-44</span></div>
      </div>
    </div>
    <div class="port-info-card">
      <h3>Informations port</h3>
      <div id="portInfoRows"></div>
    </div>
    <div class="ad-slot ad-square">
      Espace publicitaire<br/>300x250<br/>Google AdSense
    </div>
  </div>
</div>

<footer>
  <p><strong>Marees Loire-Atlantique &amp; France</strong> - Calcul harmonique avec arguments astronomiques</p>
  <p>Saint-Nazaire · Le Croisic · Pornic · La Turballe · Piriac · Saint-Brevin · Paimboeuf · La Baule</p>
  <p style="font-size:.7rem;margin-top:.4rem">Donnees a titre indicatif. Consultez le <a href="https://maree.shom.fr" target="_blank">SHOM officiel</a> pour la navigation.</p>
</footer>

{main_js}
<script>
if ('serviceWorker' in navigator) navigator.serviceWorker.register('/service-worker.js').catch(function(){{}});
document.addEventListener('DOMContentLoaded', function() {{
  var t = new Date();
  document.getElementById('dateInput').value =
    t.getFullYear() + '-' + String(t.getMonth()+1).padStart(2,'0') + '-' + String(t.getDate()).padStart(2,'0');
  loadTides();
  window.addEventListener('resize', function() {{
    var pid = document.getElementById('portSelect').value;
    var dstr = document.getElementById('dateInput').value;
    renderChart(pid, dstr ? new Date(dstr+'T12:00:00') : new Date());
  }});
  setInterval(loadTides, 300000);
}});
document.getElementById('portSelect').addEventListener('change', loadTides);
document.getElementById('dateInput').addEventListener('change', loadTides);
</script>
</body>
</html>"""

# Générer toutes les pages
for city in CITIES:
    folder = city["slug"]
    os.makedirs(folder, exist_ok=True)
    html = make_page(city)
    path = os.path.join(folder, "index.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"OK {path} ({len(html)} bytes)")

print(f"\n{len(CITIES)} pages generees.")
