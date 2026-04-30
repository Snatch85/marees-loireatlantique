/* ── Injection header + nav sur toutes les pages de contenu ── */
(function() {
  // Google AdSense (auto-ads activées après validation)
  var _ads = document.createElement('script');
  _ads.async = true;
  _ads.src = 'https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-1465276904717454';
  _ads.crossOrigin = 'anonymous';
  document.head.appendChild(_ads);


  // 1. Injecter le CSS
  var link = document.createElement('link');
  link.rel = 'stylesheet';
  link.href = '/assets/site.css';
  document.head.insertBefore(link, document.head.firstChild);

  // 2. Header HTML
  var headerHTML = `
<header class="site-header">
  <div class="site-header-inner">
    <a href="/" class="site-logo">
      <span class="site-logo-wave">🌊</span>
      <div class="site-logo-text">
        <h2>Marées Loire-Atlantique</h2>
        <p>Horaires · Coefficients · Hauteurs d'eau</p>
      </div>
    </a>
    <a href="/" class="site-header-btn">← Calculateur de marées</a>
  </div>
</header>
<nav class="site-nav" aria-label="Navigation principale">
  <div class="site-nav-inner">
    <div class="site-nav-item">
      <a href="/marees/" class="has-drop">🌊 Marées</a>
      <div class="site-nav-drop">
        <span class="drop-section">Par port</span>
        <a href="/marees/saint-nazaire/">Saint-Nazaire (référence)</a>
        <a href="/marees/la-baule/">La Baule / Le Pouliguen</a>
        <a href="/marees/le-croisic/">Le Croisic</a>
        <a href="/marees/la-turballe/">La Turballe</a>
        <a href="/marees/piriac-sur-mer/">Piriac-sur-Mer</a>
        <a href="/marees/pornic/">Pornic</a>
        <a href="/marees/noirmoutier/">Noirmoutier</a>
        <a href="/marees/passage-du-gois/">Passage du Gois ⚠️</a>
      </div>
    </div>
    <div class="site-nav-item">
      <a href="/securite-mer/" class="has-drop">⛑️ Sécurité</a>
      <div class="site-nav-drop">
        <span class="drop-section">Urgences</span>
        <a href="/securite-mer/urgences-mer/">MAYDAY / PAN PAN</a>
        <a href="/securite-mer/cross-etel/">CROSS Étel — 196</a>
        <a href="/securite-mer/avant-appareiller/">Checklist avant de partir</a>
        <span class="drop-section">Équipements</span>
        <a href="/securite-mer/gilets-sauvetage/">Gilets de sauvetage 150N</a>
        <a href="/securite-mer/epirb-balise/">Balises EPIRB / PLB</a>
        <span class="drop-section">Risques</span>
        <a href="/securite-mer/hypothermie/">Hypothermie en mer</a>
        <a href="/securite-mer/enfants-bateau/">Enfants à bord</a>
        <a href="/securite-mer/nuit/">Navigation de nuit</a>
        <a href="/securite-mer/brouillard/">Navigation par brouillard</a>
      </div>
    </div>
    <div class="site-nav-item">
      <a href="/guides/" class="has-drop">📖 Guides</a>
      <div class="site-nav-drop">
        <span class="drop-section">Comprendre les marées</span>
        <a href="/guides/quest-ce-que-la-maree/">Qu'est-ce que la marée ?</a>
        <a href="/guides/coefficient-maree/">Le coefficient de marée</a>
        <a href="/guides/lire-horaire-maree/">Lire un horaire de marée</a>
        <a href="/guides/grandes-marees-mortes-eaux/">Grandes marées et mortes-eaux</a>
        <a href="/guides/atlantique-vs-mediterranee/">Atlantique vs Méditerranée</a>
        <span class="drop-section">Pratique & sécurité</span>
        <a href="/guides/calendrier-grandes-marees/">Calendrier grandes marées 2026</a>
        <a href="/guides/marees-activites-nautiques/">Marée et activités nautiques</a>
        <a href="/guides/marees-securite/">Sécurité en bord de mer</a>
        <a href="/guides/marees-meteo/">Marées et météo</a>
        <a href="/guides/glossaire-marees/">Glossaire des marées</a>
        <span class="drop-section">Navigation & plaisance</span>
        <a href="/guides/debutant-plaisance/">Débutant en plaisance</a>
        <a href="/guides/permis-bateau/">Permis bateau côtier</a>
        <a href="/guides/vhf-radio/">Radio VHF marine</a>
        <a href="/guides/maree-et-navigation/">Marées et courants</a>
        <a href="/guides/mouillages/">Mouillages Loire-Atlantique</a>
        <a href="/guides/chenal-saint-nazaire/">Chenal de Saint-Nazaire</a>
        <a href="/guides/ile-de-noirmoutier/">Île de Noirmoutier en bateau</a>
        <a href="/guides/remorquage/">Remorquage en mer</a>
      </div>
    </div>
    <div class="site-nav-item">
      <a href="/ports-plaisance/" class="has-drop">⚓ Ports plaisance</a>
      <div class="site-nav-drop">
        <span class="drop-section">Ports</span>
        <a href="/ports-plaisance/le-croisic/">Le Croisic</a>
        <a href="/ports-plaisance/la-turballe/">La Turballe</a>
        <a href="/ports-plaisance/piriac-sur-mer/">Piriac-sur-Mer</a>
        <a href="/ports-plaisance/pornic/">Pornic</a>
        <a href="/ports-plaisance/noirmoutier/">Noirmoutier</a>
        <a href="/ports-plaisance/saint-nazaire/">Saint-Nazaire</a>
        <span class="drop-section">Informations pratiques</span>
        <a href="/ports-plaisance/tarifs-anneau/">Tarifs annuels 2025</a>
        <a href="/ports-plaisance/escales-visiteurs/">Escales visiteurs</a>
        <a href="/ports-plaisance/carburant-marin/">Carburant marin</a>
        <a href="/ports-plaisance/hivernage/">Hivernage</a>
      </div>
    </div>
    <div class="site-nav-item">
      <a href="/ports-peche/" class="has-drop">🐟 Ports de pêche</a>
      <div class="site-nav-drop">
        <a href="/ports-peche/la-turballe/">La Turballe — sardine</a>
        <a href="/ports-peche/le-croisic/">Le Croisic — homard</a>
        <a href="/ports-peche/noirmoutier/">Noirmoutier — palourdes</a>
        <a href="/ports-peche/piriac/">Piriac — artisanal</a>
        <a href="/ports-peche/saint-nazaire/">Saint-Nazaire — estuaire</a>
      </div>
    </div>
    <div class="site-nav-item">
      <a href="/meteo-marine/" class="has-drop">🌬️ Météo marine</a>
      <div class="site-nav-drop">
        <a href="/meteo-marine/saint-nazaire/">Saint-Nazaire</a>
        <a href="/meteo-marine/le-croisic/">Le Croisic</a>
        <a href="/meteo-marine/pornic/">Pornic</a>
      </div>
    </div>
    <div class="site-nav-item">
      <a href="/reglementation/">📋 Réglementation</a>
    </div>
    <div class="site-nav-item">
      <a href="/peche-a-pied/" class="has-drop">🦪 Pêche à pied</a>
      <div class="site-nav-drop">
        <span class="drop-section">Spots</span>
        <a href="/peche-a-pied/bourgneuf-en-retz/">Bourgneuf-en-Retz</a>
        <a href="/peche-a-pied/saint-michel-chef-chef/">Saint-Michel-Chef-Chef</a>
        <span class="drop-section">Espèces & réglementation</span>
        <a href="/peche-a-pied/especes/huitres/">Huîtres sauvages</a>
        <a href="/peche-a-pied/qualite-eau/">Qualité de l'eau</a>
      </div>
    </div>
  </div>
</nav>`;

  // 3. Footer HTML
  var footerHTML = `
<footer style="background:linear-gradient(135deg,#003F72,#002850);color:rgba(255,255,255,.6);text-align:center;padding:2rem 1.5rem;font-size:.77rem;line-height:1.9">
  <span style="font-size:1.2rem;display:block;margin-bottom:.5rem;opacity:.4">〰️</span>
  <p><strong style="color:#fff">Marées Loire-Atlantique &amp; France</strong></p>
  <p style="margin-top:.3rem;opacity:.75;font-size:.73rem">Données indicatives — méthode harmonique SHOM</p>
  <p style="margin-top:.6rem;font-size:.73rem">
    Consultez le <a href="https://maree.shom.fr" target="_blank" rel="noopener" style="color:#90E0EF;font-weight:500">SHOM officiel</a> pour la navigation.
    Urgence en mer : <strong style="color:#fff">196</strong> (CROSS Étel) | VHF canal 16
  </p>
  <p style="margin-top:.7rem;font-size:.73rem">
    <a href="/" style="color:#90E0EF">🌊 Calculateur de marées</a> ·
    <a href="/peche-a-pied/" style="color:#90E0EF">🦪 Pêche à pied</a> ·
    <a href="/reglementation/" style="color:#90E0EF">📋 Réglementation</a> ·
    <a href="/mentions-legales/" style="color:#90E0EF">Mentions légales</a>
  </p>
</footer>`;

  // 4. Wrapper l'article dans .page-wrap + injecter layout
  document.addEventListener('DOMContentLoaded', function() {
    var body = document.body;

    // Appliquer fond de page
    body.style.background = '#EEF6FB';
    body.style.margin = '0';

    // Injecter header en premier
    var headerDiv = document.createElement('div');
    headerDiv.innerHTML = headerHTML;
    body.insertBefore(headerDiv, body.firstChild);

    // Chercher le contenu principal (article ou main)
    var content = body.querySelector('article') || body.querySelector('main#main-content');

    if (content && !content.closest('.page-wrap')) {
      var wrap = document.createElement('div');
      wrap.className = 'page-wrap';

      // Pub en haut du contenu
      var adTop = document.createElement('div');
      adTop.className = 'ad-wrap';
      adTop.innerHTML =
        '<span class="ad-label">Publicité</span>' +
        '<ins class="adsbygoogle" style="display:block" ' +
        'data-ad-client="ca-pub-1465276904717454" ' +
        'data-ad-slot="AUTO" data-ad-format="auto" ' +
        'data-full-width-responsive="true"></ins>';

      content.parentNode.insertBefore(wrap, content);
      wrap.appendChild(adTop);
      wrap.appendChild(content);

      // Pub en bas du contenu
      var adBot = document.createElement('div');
      adBot.className = 'ad-wrap';
      adBot.style.marginTop = '1.5rem';
      adBot.innerHTML =
        '<span class="ad-label">Publicité</span>' +
        '<ins class="adsbygoogle" style="display:block" ' +
        'data-ad-client="ca-pub-1465276904717454" ' +
        'data-ad-slot="AUTO" data-ad-format="auto" ' +
        'data-full-width-responsive="true"></ins>';
      wrap.appendChild(adBot);
    }

    // Injecter footer
    var footerDiv = document.createElement('div');
    footerDiv.innerHTML = footerHTML;
    body.appendChild(footerDiv);

    // Lien actif dans la nav
    var path = window.location.pathname;
    var navLinks = document.querySelectorAll('.site-nav-item > a');
    navLinks.forEach(function(link) {
      var href = link.getAttribute('href') || '';
      if (href !== '/' && path.startsWith(href.replace(/\/$/, ''))) {
        link.style.background = 'var(--o50)';
        link.style.color = 'var(--o700)';
        link.style.fontWeight = '700';
      }
    });
  });
})();
