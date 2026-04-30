/* ── Injection header + nav sur toutes les pages de contenu ── */
(function() {
  // ── The Moneytizer — CMP InMobi + pub ──
  (function() {
    var host = "www.themoneytizer.com";
    var el = document.createElement('script');
    var first = document.getElementsByTagName('script')[0];
    el.async = true;
    el.type = 'text/javascript';
    el.src = 'https://cmp.inmobi.com/choice/6Fv0cGNfc_bw8/' + host + '/choice.js?tag_version=V3';
    first.parentNode.insertBefore(el, first);
  })();
  var _tmn = document.createElement('script');
  _tmn.async = true;
  _tmn.src = '//cdn.themoneytizer.com/tags/140420/gen.js';
  document.head.appendChild(_tmn);

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
<footer class="site-footer">
  <p>© 2025 marees-loireatlantique.fr — Données indicatives basées sur la méthode harmonique SHOM.<br>
  Consultez toujours le <a href="https://maree.shom.fr" target="_blank">SHOM officiel</a> pour la navigation.
  Urgence en mer : <strong style="color:#fff">196</strong> (CROSS Étel) | VHF canal 16</p>
</footer>`;

  // 4. Wrapper l'article dans .page-wrap
  document.addEventListener('DOMContentLoaded', function() {
    var body = document.body;
    var article = body.querySelector('article');

    // Injecter header avant tout
    var headerDiv = document.createElement('div');
    headerDiv.innerHTML = headerHTML;
    body.insertBefore(headerDiv, body.firstChild);

    // Wrapper article
    if (article) {
      var wrap = document.createElement('div');
      wrap.className = 'page-wrap';
      article.parentNode.insertBefore(wrap, article);
      wrap.appendChild(article);
    }

    // Injecter footer
    var footerDiv = document.createElement('div');
    footerDiv.innerHTML = footerHTML;
    body.appendChild(footerDiv);

    // Marquer le lien actif dans la nav
    var path = window.location.pathname;
    var navLinks = document.querySelectorAll('.site-nav-item > a');
    navLinks.forEach(function(link) {
      if (path.startsWith(link.getAttribute('href').replace(/\/$/, ''))) {
        link.style.background = 'rgba(255,255,255,.22)';
        link.style.color = '#fff';
      }
    });
  });
})();
