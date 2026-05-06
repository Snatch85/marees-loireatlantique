/**
 * moon-widget.js
 * Widget Phase Lunaire — marees-loireatlantique.fr
 * Calcul astronomique harmonique (J2000.0) — aucune dépendance externe
 */

(function () {
  'use strict';

  /* ─── Constantes astronomiques ─────────────────────────────────────── */
  const SYNODIC   = 29.530588853;                              // période synodique (jours)
  const REF_MS    = new Date('2000-01-06T18:14:00Z').getTime(); // nouvelle lune de référence J2000

  /* ─── Calcul de l'âge lunaire ────────────────────────────────────────
     Retourne l'âge en jours depuis la dernière nouvelle lune (0 – 29.53)
  ──────────────────────────────────────────────────────────────────── */
  function getMoonAge(date) {
    const daysSince = (date.getTime() - REF_MS) / 86400000;
    return ((daysSince % SYNODIC) + SYNODIC) % SYNODIC;
  }

  /* ─── Informations sur la phase actuelle ─────────────────────────── */
  function getMoonInfo(age) {
    const phase = age / SYNODIC;
    const illum = Math.round((1 - Math.cos(2 * Math.PI * phase)) / 2 * 100);
    const defs = [
      [0,     1.85,  'Nouvelle Lune'],
      [1.85,  7.38,  'Premier Croissant'],
      [7.38,  9.22,  'Premier Quartier'],
      [9.22,  14.76, 'Gibbeuse Croissante'],
      [14.76, 16.61, 'Pleine Lune'],
      [16.61, 22.15, 'Gibbeuse Décroissante'],
      [22.15, 23.99, 'Dernier Quartier'],
      [23.99, 99,    'Dernier Croissant'],
    ];
    const match = defs.find(([mn, mx]) => age >= mn && age < mx) || defs[0];
    return { name: match[2], illum };
  }

  /* ─── Prochaine occurrence d'une phase (en jours depuis nouvelle lune) */
  function nextPhaseDate(now, targetDays) {
    const cur = getMoonAge(now);
    let diff = targetDays - cur;
    if (diff <= 0) diff += SYNODIC;
    return new Date(now.getTime() + diff * 86400000);
  }

  function fmtDate(d) {
    return d.toLocaleDateString('fr-FR', { day: 'numeric', month: 'long' });
  }

  /* ─── Canvas : sphère 3D ─────────────────────────────────────────── */
  function drawSphere(ctx, cx, cy, r) {
    /* gradient de base — highlight décalé haut-gauche pour l'effet 3D */
    const g = ctx.createRadialGradient(
      cx - r * 0.3, cy - r * 0.35, r * 0.05,
      cx + r * 0.1, cy + r * 0.1,  r * 1.1
    );
    g.addColorStop(0,    '#fffff5');
    g.addColorStop(0.2,  '#f0e8c8');
    g.addColorStop(0.45, '#d8c898');
    g.addColorStop(0.7,  '#b09878');
    g.addColorStop(0.88, '#887050');
    g.addColorStop(1,    '#483820');
    ctx.beginPath();
    ctx.arc(cx, cy, r, 0, Math.PI * 2);
    ctx.fillStyle = g;
    ctx.fill();

    /* cratères [dx, dy, rayon_relatif] */
    [
      [0.2,  -0.1,  0.12],
      [-0.3,  0.2,  0.09],
      [0.1,   0.35, 0.07],
      [-0.15,-0.3,  0.06],
      [0.35,  0.15, 0.05],
      [-0.05, 0.05, 0.035],
    ].forEach(([dx, dy, cr]) => {
      const cg = ctx.createRadialGradient(
        cx + dx * r * 0.9, cy + dy * r * 0.9, 0,
        cx + dx * r,        cy + dy * r,        cr * r
      );
      cg.addColorStop(0,   'rgba(40,24,8,0.28)');
      cg.addColorStop(0.5, 'rgba(30,18,5,0.12)');
      cg.addColorStop(1,   'rgba(0,0,0,0)');
      ctx.beginPath();
      ctx.arc(cx + dx * r, cy + dy * r, cr * r, 0, Math.PI * 2);
      ctx.fillStyle = cg;
      ctx.fill();
    });

    /* assombrissement des bords pour renforcer l'effet sphère */
    const eg = ctx.createRadialGradient(cx, cy, r * 0.62, cx, cy, r);
    eg.addColorStop(0, 'rgba(0,0,0,0)');
    eg.addColorStop(1, 'rgba(0,0,0,0.5)');
    ctx.beginPath();
    ctx.arc(cx, cy, r, 0, Math.PI * 2);
    ctx.fillStyle = eg;
    ctx.fill();
  }

  /* ─── Canvas : ombre de phase (terminateur elliptique) ───────────── */
  function drawShadow(ctx, cx, cy, r, phase) {
    const PI = Math.PI;
    const xs = Math.cos(2 * PI * phase);   // -1 (pleine lune) → 1 (nouvelle lune)
    const ax = Math.abs(xs);
    const waxing = phase < 0.5;

    ctx.save();
    ctx.beginPath();
    ctx.arc(cx, cy, r, 0, PI * 2);
    ctx.clip();
    ctx.fillStyle = 'rgba(3,8,22,0.94)';

    if (phase < 0.02 || phase > 0.98) {
      /* nouvelle lune : disque entier sombre */
      ctx.fillRect(cx - r, cy - r, r * 2, r * 2);
    } else if (phase > 0.48 && phase < 0.52) {
      /* pleine lune : pas d'ombre */
    } else {
      ctx.beginPath();
      if (waxing) {
        if (xs >= 0) {
          /* nouvelle → 1er quartier : ombre couvre la quasi-totalité */
          ctx.arc(cx, cy, r, 1.5 * PI, 0.5 * PI, true);
          ctx.ellipse(cx, cy, xs * r, r, 0, 0.5 * PI, 1.5 * PI, true);
        } else {
          /* 1er quartier → pleine : mince croissant sombre à gauche */
          ctx.arc(cx, cy, r, 1.5 * PI, 0.5 * PI, true);
          ctx.ellipse(cx, cy, ax * r, r, 0, 0.5 * PI, 1.5 * PI, false);
        }
      } else {
        if (xs <= 0) {
          /* pleine → dernier quartier : mince croissant sombre à droite */
          ctx.arc(cx, cy, r, 1.5 * PI, 0.5 * PI, false);
          ctx.ellipse(cx, cy, ax * r, r, 0, 0.5 * PI, 1.5 * PI, true);
        } else {
          /* dernier quartier → nouvelle : ombre couvre la quasi-totalité */
          ctx.arc(cx, cy, r, 1.5 * PI, 0.5 * PI, false);
          ctx.ellipse(cx, cy, xs * r, r, 0, 0.5 * PI, 1.5 * PI, false);
        }
      }
      ctx.closePath();
      ctx.fill();
    }
    ctx.restore();
  }

  /* ─── Dessine une lune sur un <canvas> ───────────────────────────── */
  function paintMoon(canvas, moonAge) {
    const ctx = canvas.getContext('2d');
    const w = canvas.width, h = canvas.height;
    const cx = w / 2, cy = h / 2;
    const pad = Math.max(2, Math.floor(w / 20));
    const r = Math.min(w, h) / 2 - pad;
    ctx.clearRect(0, 0, w, h);
    drawSphere(ctx, cx, cy, r);
    drawShadow(ctx, cx, cy, r, moonAge / SYNODIC);
  }

  /* ─── Construit la rangée du cycle lunaire (8 mini-lunes) ─────────── */
  function buildCycleRow(now, moonAge) {
    const start = now.getTime() - moonAge * 86400000;
    const offsets = [
      [0,     'N. Lune'],
      [3.69,  'Crois.'],
      [7.38,  '1er Q.'],
      [11.07, 'Gibb.+'],
      [14.77, 'P. Lune'],
      [18.46, 'Gibb.-'],
      [22.15, 'Der. Q.'],
      [25.84, 'Décr.'],
    ];
    const container = document.getElementById('mw-cycle-row');
    if (!container) return;
    container.innerHTML = '';

    offsets.forEach(([off, label], i) => {
      const nextOff = offsets[i + 1] ? offsets[i + 1][0] : SYNODIC;
      const active  = moonAge >= off && moonAge < nextOff;
      const phDate  = new Date(start + off * 86400000);

      const card = document.createElement('div');
      card.className = 'mw-phase-card' + (active ? ' mw-phase-card--active' : '');

      const cvs = document.createElement('canvas');
      cvs.width = 36; cvs.height = 36;
      cvs.className = 'mw-mini-moon';
      card.appendChild(cvs);

      const lbl = document.createElement('div');
      lbl.className = 'mw-phase-label';
      lbl.textContent = label;
      card.appendChild(lbl);

      const dt = document.createElement('div');
      dt.className = 'mw-phase-date';
      dt.textContent = phDate.toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' });
      card.appendChild(dt);

      container.appendChild(card);
      paintMoon(cvs, off);
    });
  }

  /* ─── Message d'influence sur les marées ─────────────────────────── */
  function setTideInfo(phaseName) {
    const infoEl = document.getElementById('mw-tide-info');
    const tagEl  = document.getElementById('mw-tide-tag');
    if (!infoEl || !tagEl) return;

    const isSyzygy    = phaseName === 'Nouvelle Lune' || phaseName === 'Pleine Lune';
    const isQuadrature = phaseName === 'Premier Quartier' || phaseName === 'Dernier Quartier';
    const isWaxing    = phaseName.includes('Croissant') || phaseName.includes('Croissante');

    let text, tagLabel, tagClass;

    if (isSyzygy) {
      text     = 'Syzygie Lune-Soleil — <strong>grandes vives-eaux</strong>. Coefficients maximaux (90-120). Conditions idéales pour la pêche à pied en Loire-Atlantique.';
      tagLabel = '⚡ Grandes vives-eaux';
      tagClass = 'mw-tag--danger';
    } else if (isQuadrature) {
      text     = 'Lune en quadrature — <strong>mortes-eaux</strong>. Coefficients au minimum (20-45). Faible amplitude de marée cette semaine.';
      tagLabel = '💤 Mortes-eaux';
      tagClass = 'mw-tag--neutral';
    } else if (isWaxing) {
      text     = 'Phase croissante — les forces de marée <strong>augmentent progressivement</strong>. Les coefficients montent vers les prochaines vives-eaux.';
      tagLabel = '↗ Vives-eaux en approche';
      tagClass = 'mw-tag--warning';
    } else {
      text     = 'Phase décroissante — les forces de marée <strong>diminuent progressivement</strong>. Les coefficients descendent vers les mortes-eaux.';
      tagLabel = '↘ Vers les mortes-eaux';
      tagClass = 'mw-tag--neutral';
    }

    infoEl.innerHTML = text;
    tagEl.textContent = tagLabel;
    tagEl.className = 'mw-tag ' + tagClass;
  }

  /* ─── Point d'entrée principal ───────────────────────────────────── */
  function initMoonWidget() {
    const now     = new Date();
    const moonAge = getMoonAge(now);
    const { name, illum } = getMoonInfo(moonAge);

    const mainCanvas = document.getElementById('mw-canvas');
    if (mainCanvas) paintMoon(mainCanvas, moonAge);

    const el = (id) => document.getElementById(id);
    if (el('mw-phase-name'))  el('mw-phase-name').textContent  = name;
    if (el('mw-illum'))       el('mw-illum').textContent       = illum;
    if (el('mw-age'))         el('mw-age').textContent         = moonAge.toFixed(1);
    if (el('mw-next-full'))   el('mw-next-full').textContent   = fmtDate(nextPhaseDate(now, SYNODIC / 2));
    if (el('mw-next-new'))    el('mw-next-new').textContent    = fmtDate(nextPhaseDate(now, 0));

    buildCycleRow(now, moonAge);
    setTideInfo(name);
  }

  /* ─── Auto-init au chargement de la page ─────────────────────────── */
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initMoonWidget);
  } else {
    initMoonWidget();
  }

  /* Export pour appel manuel si besoin */
  window.initMoonWidget = initMoonWidget;

})();
