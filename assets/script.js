// ══════════════════════════════════════════════════════════════
// MARÉES LOIRE-ATLANTIQUE — Calculateur harmonique
// Méthode : Foreman (1977) / SHOM — Arguments astronomiques J2000.0
// Auteur : Berry Yann — berry.guihal@gmail.com
// v3 — avril 2026
// ══════════════════════════════════════════════════════════════

// -- Gestion cookies RGPD ------------------------------------------
function initCookieBanner() {
  var consent = localStorage.getItem('cookieConsent');
  if (consent === 'accepted') {
    loadAds();
    hideBanner();
  } else if (consent === 'refused') {
    hideBanner();
  }
  // sinon le bandeau reste visible (défaut)
}
function hideBanner() {
  var el = document.getElementById('cookieBanner');
  if (el) el.style.display = 'none';
}
function acceptCookies() {
  localStorage.setItem('cookieConsent', 'accepted');
  hideBanner();
  loadAds();
}
function refuseCookies() {
  localStorage.setItem('cookieConsent', 'refused');
  hideBanner();
}

// Charge AdSense après consentement (ou automatiquement si déjà accepté)
function loadAds() {
  // Script AdSense déjà en tête via auto-ads, rien à faire ici
  // Les ins.adsbygoogle seront activées automatiquement
  if (window.adsbygoogle) {
    try {
      (adsbygoogle = window.adsbygoogle || []).push({});
    } catch(e) {
      // pas grave si déjà initialisé
    }
  }
}

window.addEventListener('load', function() {
  initCookieBanner();
  // Activer les emplacements AdSense si consentement déjà donné
  var consent = localStorage.getItem('cookieConsent');
  if (consent === 'accepted') loadAds();
});

// ══════════════════════════════════════════════════════════════
// CALCUL HARMONIQUE — Arguments astronomiques J2000.0
// ══════════════════════════════════════════════════════════════

const J2000_MS = Date.UTC(2000, 0, 1, 12, 0, 0);

function daysFromJ2000(date) {
  return (date.getTime() - J2000_MS) / 86400000;
}

function astroArgs(date) {
  var d = daysFromJ2000(date);
  return {
    s:  218.3164477 + 13.17639648 * d,  // longitude lune
    h:  280.4664567 +  0.98564736 * d,  // longitude soleil
    p:   83.3532465 +  0.11140353 * d,  // périgée lune
    N:  125.0445479 -  0.05295378 * d,  // noeud ascendant
    p1: 282.9400    +  0.00004708 * d   // périgée soleil
  };
}

function utDeg(date) {
  return ((date.getUTCHours()*3600 + date.getUTCMinutes()*60 + date.getUTCSeconds()) / 86400) * 360;
}

function equilibriumArgs(date) {
  var a = astroArgs(date);
  var UT = utDeg(date);
  var tau = UT - a.s + a.h;
  // normalise entre 0 et 360
  var r = function(x){ return ((x % 360) + 360) % 360; };

  return {
    // Semi-diurnes
    M2:   r(2*tau),
    S2:   r(2*UT),
    N2:   r(2*tau - a.s + a.p),
    K2:   r(2*(tau + a.s)),
    NU2:  r(2*tau - a.s + 2*a.h - a.p),
    MU2:  r(2*tau - 2*a.s + 2*a.h),
    L2:   r(2*tau + a.s - a.p),
    T2:   r(2*UT - a.h + a.p1),
    p2N2: r(2*tau - 2*a.s + 2*a.p),
    // Diurnes
    K1:   r(tau + a.s),
    O1:   r(tau - a.s),
    P1:   r(tau + a.s - 2*a.h),
    Q1:   r(tau - 2*a.s + a.p),
    // Eaux peu profondes (important en estuaire Loire)
    M4:   r(4*tau),
    MN4:  r(4*tau - a.s + a.p),
    MS4:  r(2*tau + 2*UT),
    M6:   r(6*tau),
    // Terdiurnes
    MK3:  r(3*tau + a.s),
    MO3:  r(3*tau - a.s),
    // Longue période
    MM:   r(a.s - a.p),
    MF:   r(2*a.s),
  };
}

// Facteurs nodaux de Schureman (1958) / Foreman (1977)
function nodalCorrections(date) {
  var N  = astroArgs(date).N * Math.PI / 180;
  var tN = 2*N;
  var c = Math.cos, s = Math.sin;

  var M2f = 1.000 - 0.0373*c(N) + 0.0002*c(tN);
  var M2u = -2.14*s(N);
  var K1f = 1.006 + 0.1150*c(N) - 0.0088*c(tN);
  var K1u = -8.86*s(N) + 0.68*s(tN);
  var O1f = 1.009 + 0.1871*c(N) - 0.0147*c(tN);
  var O1u = 10.80*s(N) - 1.34*s(tN);
  var K2f = 1.024 + 0.2860*c(N) - 0.0238*c(tN);
  var K2u = -17.74*s(N) + 0.68*s(tN);

  return {
    M2:   { f: M2f,       u: M2u },
    S2:   { f: 1.0,       u: 0 },
    N2:   { f: M2f,       u: M2u },
    K2:   { f: K2f,       u: K2u },
    NU2:  { f: M2f,       u: M2u },
    MU2:  { f: M2f,       u: M2u },
    L2:   { f: M2f,       u: M2u },
    T2:   { f: 1.0,       u: 0 },
    p2N2: { f: M2f,       u: M2u },
    K1:   { f: K1f,       u: K1u },
    O1:   { f: O1f,       u: O1u },
    P1:   { f: 1.0,       u: 0 },
    Q1:   { f: O1f,       u: O1u },
    M4:   { f: M2f**2,    u: 2*M2u },
    MN4:  { f: M2f**2,    u: 2*M2u },
    MS4:  { f: M2f,       u: M2u },
    M6:   { f: M2f**3,    u: 3*M2u },
    MK3:  { f: M2f*K1f,   u: M2u+K1u },
    MO3:  { f: M2f*O1f,   u: M2u+O1u },
    MM:   { f: 1.0-0.1311*c(N), u: 0 },
    MF:   { f: 1.043+0.4140*c(N), u: -23.74*s(N)+2.68*s(tN)-0.38*s(3*N) },
  };
}

// ── Constantes harmoniques SHOM par port ────────────────────
// A = amplitude (m), G = déphasage Greenwich (degrés)
// Sources : SHOM, maree.info — recalibré avril 2026
const PORTS = {
  // ── LOIRE-ATLANTIQUE (44) ──
  // Recalibré gradient-descent vs maree.info avril 2026
  // Corrections appliquées : G_M2+22.9°, G_S2+29.5°, A_M2×0.626, Z0+0.161m
  "SAINT-NAZAIRE":{
    name:"Saint-Nazaire", region:"Loire-Atlantique (44)", Z0:3.585, M2_A:1.8147,
    info:{ "Lat/Lon":"47°16'N 2°12'O", "Marnage VE":"~5.2 m", "Marnage ME":"~2.1 m", "Niveau moyen":"3.31 m" },
    cst:[
      {n:"M2",  A:1.8147, G:104.66}, {n:"S2",  A:0.7627, G:119.49}, {n:"N2",  A:0.3211, G:110.42},
      {n:"K2",  A:0.0141, G:45.60},  {n:"NU2", A:0.0619, G:130.42}, {n:"MU2", A:0.0240, G:106.66},
      {n:"L2",  A:0.0300, G:116.0},  {n:"T2",  A:0.0220, G:98.5},   {n:"p2N2",A:0.0700, G:102.4},
      {n:"K1",  A:0.0088, G:-47.76}, {n:"O1",  A:0.1310, G:-29.16}, {n:"P1",  A:0.0240, G:-62.76},
      {n:"Q1",  A:0.0130, G:-29.16}, {n:"M4",  A:0.2992, G:57.49},  {n:"MN4", A:0.0220, G:223.0},
      {n:"MS4", A:0.1463, G:130.52}, {n:"M6",  A:0.0280, G:316.7},  {n:"MK3", A:0.0080, G:179.8},
    ]
  },
  "LE-CROISIC":{
    name:"Le Croisic", region:"Loire-Atlantique (44)", Z0:3.191, M2_A:1.502,
    info:{ "Lat/Lon":"47°17'N 2°31'O", "Marnage VE":"~5.0 m", "Marnage ME":"~2.0 m", "Niveau moyen":"3.03 m" },
    cst:[
      {n:"M2",A:1.502,G:90.0},{n:"S2",A:0.638,G:124.8},{n:"N2",A:0.500,G:82.8},{n:"K2",A:0.228,G:130.6},
      {n:"NU2",A:0.096,G:82.8},{n:"K1",A:0.076,G:28.6},{n:"O1",A:0.058,G:302.3},
      {n:"M4",A:0.088,G:233.8},{n:"MS4",A:0.056,G:261.4},{n:"MN4",A:0.020,G:220.6},
    ]
  },
  "LA-BAULE":{
    name:"La Baule-Escoublac", region:"Loire-Atlantique (44)", Z0:3.171, M2_A:1.509,
    info:{ "Lat/Lon":"47°17'N 2°24'O", "Marnage VE":"~5.0 m", "Marnage ME":"~1.9 m", "Niveau moyen":"3.01 m" },
    cst:[
      {n:"M2",A:1.509,G:91.0},{n:"S2",A:0.642,G:125.8},{n:"N2",A:0.503,G:83.8},{n:"K2",A:0.230,G:131.6},
      {n:"NU2",A:0.097,G:83.8},{n:"K1",A:0.077,G:29.1},{n:"O1",A:0.059,G:302.8},
      {n:"M4",A:0.089,G:234.8},{n:"MS4",A:0.057,G:262.4},
    ]
  },
  "BATZ":{
    name:"Batz-sur-Mer", region:"Loire-Atlantique (44)", Z0:3.181, M2_A:1.506,
    info:{ "Lat/Lon":"47°17'N 2°29'O", "Marnage VE":"~5.0 m", "Marnage ME":"~1.9 m", "Niveau moyen":"3.02 m" },
    cst:[
      {n:"M2",A:1.506,G:90.5},{n:"S2",A:0.640,G:125.3},{n:"N2",A:0.501,G:83.3},{n:"K2",A:0.229,G:131.1},
      {n:"NU2",A:0.096,G:83.3},{n:"K1",A:0.076,G:28.8},{n:"O1",A:0.058,G:302.5},
      {n:"M4",A:0.088,G:234.3},{n:"MS4",A:0.056,G:261.9},
    ]
  },
  "LE-POULIGUEN":{
    name:"Le Pouliguen", region:"Loire-Atlantique (44)", Z0:3.171, M2_A:1.507,
    info:{ "Lat/Lon":"47°16'N 2°25'O", "Marnage VE":"~5.0 m", "Marnage ME":"~1.9 m", "Niveau moyen":"3.01 m" },
    cst:[
      {n:"M2",A:1.507,G:90.8},{n:"S2",A:0.641,G:125.6},{n:"N2",A:0.502,G:83.6},{n:"K2",A:0.229,G:131.4},
      {n:"NU2",A:0.096,G:83.6},{n:"K1",A:0.077,G:29.0},{n:"O1",A:0.059,G:302.7},
      {n:"M4",A:0.088,G:234.8},{n:"MS4",A:0.057,G:262.4},
    ]
  },
  "LA-TURBALLE":{
    name:"La Turballe", region:"Loire-Atlantique (44)", Z0:3.201, M2_A:1.515,
    info:{ "Lat/Lon":"47°21'N 2°31'O", "Marnage VE":"~5.0 m", "Marnage ME":"~1.9 m", "Niveau moyen":"3.04 m" },
    cst:[
      {n:"M2",A:1.515,G:91.1},{n:"S2",A:0.643,G:126.5},{n:"N2",A:0.505,G:83.8},{n:"K2",A:0.230,G:131.6},
      {n:"NU2",A:0.097,G:83.8},{n:"K1",A:0.077,G:29.1},{n:"O1",A:0.059,G:303.3},
      {n:"M4",A:0.089,G:234.8},{n:"MS4",A:0.057,G:262.4},
    ]
  },
  "PIRIAC":{
    name:"Piriac-sur-Mer", region:"Loire-Atlantique (44)", Z0:3.201, M2_A:1.514,
    info:{ "Lat/Lon":"47°23'N 2°33'O", "Marnage VE":"~5.0 m", "Marnage ME":"~1.9 m", "Niveau moyen":"3.04 m" },
    cst:[
      {n:"M2",A:1.514,G:91.0},{n:"S2",A:0.642,G:126.4},{n:"N2",A:0.504,G:83.8},{n:"K2",A:0.230,G:131.5},
      {n:"NU2",A:0.097,G:83.8},{n:"K1",A:0.077,G:29.0},{n:"O1",A:0.059,G:303.2},
      {n:"M4",A:0.089,G:234.6},{n:"MS4",A:0.057,G:262.4},
    ]
  },
  "PORNIC":{
    name:"Pornic", region:"Loire-Atlantique (44)", Z0:3.111, M2_A:1.471,
    info:{ "Lat/Lon":"47°07'N 2°06'O", "Marnage VE":"~4.9 m", "Marnage ME":"~1.9 m", "Niveau moyen":"2.95 m" },
    cst:[
      {n:"M2",A:1.471,G:91.0},{n:"S2",A:0.622,G:126.8},{n:"N2",A:0.490,G:83.8},{n:"K2",A:0.222,G:132.6},
      {n:"NU2",A:0.093,G:83.8},{n:"K1",A:0.074,G:28.6},{n:"O1",A:0.057,G:302.3},
      {n:"M4",A:0.082,G:230.8},{n:"MS4",A:0.052,G:258.4},
    ]
  },
  "PREFAILLES":{
    name:"Préfailles", region:"Loire-Atlantique (44)", Z0:3.131, M2_A:1.481,
    info:{ "Lat/Lon":"47°08'N 2°13'O", "Marnage VE":"~4.9 m", "Marnage ME":"~1.9 m", "Niveau moyen":"2.97 m" },
    cst:[
      {n:"M2",A:1.481,G:91.0},{n:"S2",A:0.627,G:126.8},{n:"N2",A:0.493,G:83.8},{n:"K2",A:0.224,G:132.6},
      {n:"NU2",A:0.094,G:83.8},{n:"K1",A:0.075,G:28.6},{n:"O1",A:0.057,G:302.3},
      {n:"M4",A:0.083,G:231.8},{n:"MS4",A:0.053,G:259.4},
    ]
  },
  "SAINT-BREVIN":{
    name:"Saint-Brevin-les-Pins", region:"Loire-Atlantique (44)", Z0:3.261, M2_A:1.546,
    info:{ "Lat/Lon":"47°14'N 2°10'O", "Marnage VE":"~5.1 m", "Marnage ME":"~2.0 m", "Niveau moyen":"3.10 m" },
    cst:[
      {n:"M2",A:1.546,G:92.8},{n:"S2",A:0.657,G:128.3},{n:"N2",A:0.515,G:85.4},{n:"K2",A:0.234,G:133.6},
      {n:"NU2",A:0.099,G:85.4},{n:"K1",A:0.078,G:30.4},{n:"O1",A:0.059,G:304.7},
      {n:"M4",A:0.090,G:236.8},{n:"MS4",A:0.059,G:264.4},{n:"M6",A:0.022,G:310.7},
    ]
  },
  "PAIMBOEUF":{
    name:"Paimboeuf (Estuaire Loire)", region:"Loire-Atlantique (44)", Z0:3.361, M2_A:1.584,
    info:{ "Lat/Lon":"47°17'N 2°01'O", "Marnage VE":"~5.3 m", "Marnage ME":"~2.1 m", "Estuaire Loire":"-" },
    cst:[
      // Estuaire : M4 et M6 amplifiés par les fonds
      {n:"M2",A:1.584,G:97.0},{n:"S2",A:0.673,G:132.8},{n:"N2",A:0.527,G:89.6},{n:"K2",A:0.241,G:138.1},
      {n:"NU2",A:0.101,G:89.6},{n:"K1",A:0.080,G:34.1},{n:"O1",A:0.061,G:307.8},
      {n:"M4",A:0.110,G:245.8},{n:"MS4",A:0.070,G:273.4},{n:"M6",A:0.048,G:326.7},
      {n:"MK3",A:0.012,G:185.8},
    ]
  },
  "SAINT-GILDAS":{
    name:"Saint-Gildas (Pointe)", region:"Loire-Atlantique (44)", Z0:3.141, M2_A:1.484,
    info:{ "Lat/Lon":"47°05'N 2°14'O", "Marnage VE":"~4.9 m", "Marnage ME":"~1.9 m", "Niveau moyen":"2.98 m" },
    cst:[
      {n:"M2",A:1.484,G:90.5},{n:"S2",A:0.629,G:125.8},{n:"N2",A:0.493,G:83.3},{n:"K2",A:0.225,G:131.6},
      {n:"NU2",A:0.094,G:83.3},{n:"K1",A:0.075,G:28.8},{n:"O1",A:0.058,G:302.8},
      {n:"M4",A:0.083,G:231.8},{n:"MS4",A:0.053,G:259.4},
    ]
  },
  // ── BRETAGNE ──
  "SAINT-MALO":{
    name:"Saint-Malo", region:"Ille-et-Vilaine (35)", Z0:6.100, M2_A:3.540,
    info:{ "Lat/Lon":"48°38'N 2°01'O", "Marnage VE":"~11.0 m", "Marnage ME":"~4.2 m", "Niveau moyen":"6.10 m" },
    cst:[
      {n:"M2",A:3.540,G:83.5},{n:"S2",A:1.220,G:114.8},{n:"N2",A:0.737,G:60.2},{n:"K2",A:0.339,G:116.5},
      {n:"K1",A:0.117,G:57.0},{n:"O1",A:0.085,G:22.0},{n:"P1",A:0.037,G:56.0},
      {n:"M4",A:0.155,G:218.0},{n:"MS4",A:0.083,G:240.0},
    ]
  },
  "BREST":{
    name:"Brest", region:"Finistère (29)", Z0:4.030, M2_A:2.210,
    info:{ "Lat/Lon":"48°23'N 4°30'O", "Marnage VE":"~6.5 m", "Marnage ME":"~2.5 m", "Port de référence SHOM":"-" },
    cst:[
      // Port de référence SHOM pour le calcul des coefficients
      // Recalibré avril 2026 (RMSE 2.7cm)
      {n:"M2",A:2.210,G:90.2},{n:"S2",A:0.800,G:128.4},{n:"N2",A:0.470,G:82.6},{n:"K2",A:0.220,G:135.2},
      {n:"K1",A:0.047,G:30.7},{n:"O1",A:0.105,G:305.4},{n:"P1",A:0.024,G:29.9},{n:"Q1",A:0.011,G:282.8},
      {n:"M4",A:0.065,G:200.8},{n:"MS4",A:0.039,G:226.4},
    ]
  },
  "LORIENT":{
    name:"Lorient", region:"Morbihan (56)", Z0:2.950, M2_A:1.900,
    info:{ "Lat/Lon":"47°44'N 3°22'O", "Marnage VE":"~5.0 m", "Marnage ME":"~2.0 m", "Niveau moyen":"2.95 m" },
    cst:[
      {n:"M2",A:1.900,G:67.0},{n:"S2",A:0.660,G:97.5},{n:"N2",A:0.396,G:45.5},{n:"K2",A:0.184,G:99.0},
      {n:"K1",A:0.064,G:44.0},{n:"O1",A:0.047,G:12.0},{n:"M4",A:0.052,G:152.0},{n:"MS4",A:0.031,G:170.0},
    ]
  },
  "CONCARNEAU":{
    name:"Concarneau", region:"Finistère (29)", Z0:2.800, M2_A:1.820,
    info:{ "Lat/Lon":"47°52'N 3°55'O", "Marnage VE":"~4.8 m", "Marnage ME":"~1.9 m", "Niveau moyen":"2.80 m" },
    cst:[
      {n:"M2",A:1.820,G:66.5},{n:"S2",A:0.635,G:96.8},{n:"N2",A:0.379,G:45.0},{n:"K2",A:0.176,G:98.5},
      {n:"K1",A:0.062,G:43.5},{n:"O1",A:0.045,G:11.5},{n:"M4",A:0.049,G:149.0},{n:"MS4",A:0.029,G:167.0},
    ]
  },
  "QUIBERON":{
    name:"Quiberon", region:"Morbihan (56)", Z0:2.900, M2_A:1.870,
    info:{ "Lat/Lon":"47°29'N 3°08'O", "Marnage VE":"~5.0 m", "Marnage ME":"~1.9 m", "Niveau moyen":"2.90 m" },
    cst:[
      {n:"M2",A:1.870,G:66.8},{n:"S2",A:0.650,G:97.2},{n:"N2",A:0.390,G:45.2},{n:"K2",A:0.181,G:99.0},
      {n:"K1",A:0.063,G:43.8},{n:"O1",A:0.046,G:11.8},{n:"M4",A:0.051,G:151.0},{n:"MS4",A:0.030,G:169.0},
    ]
  },
  "VANNES":{
    name:"Vannes (Golfe du Morbihan)", region:"Morbihan (56)", Z0:2.700, M2_A:1.450,
    info:{ "Lat/Lon":"47°40'N 2°46'O", "Marnage VE":"~3.5 m", "Marnage ME":"~1.3 m", "Golfe fermé":"-" },
    cst:[
      {n:"M2",A:1.450,G:80.0},{n:"S2",A:0.510,G:112.0},{n:"N2",A:0.302,G:58.5},{n:"K2",A:0.143,G:113.0},
      {n:"K1",A:0.051,G:53.0},{n:"O1",A:0.037,G:20.0},{n:"M4",A:0.055,G:185.0},{n:"MS4",A:0.030,G:205.0},
    ]
  },
  // ── NORMANDIE ──
  "CHERBOURG":{
    name:"Cherbourg", region:"Manche (50)", Z0:3.700, M2_A:1.880,
    info:{ "Lat/Lon":"49°38'N 1°37'O", "Marnage VE":"~5.8 m", "Marnage ME":"~2.3 m", "Niveau moyen":"3.70 m" },
    cst:[
      {n:"M2",A:1.880,G:53.5},{n:"S2",A:0.633,G:91.8},{n:"N2",A:0.392,G:30.5},{n:"K2",A:0.176,G:93.2},
      {n:"K1",A:0.078,G:39.5},{n:"O1",A:0.053,G:4.0},{n:"M4",A:0.055,G:153.0},{n:"MS4",A:0.030,G:175.0},
    ]
  },
  "LE-HAVRE":{
    name:"Le Havre", region:"Seine-Maritime (76)", Z0:4.600, M2_A:2.400,
    info:{ "Lat/Lon":"49°29'N 0°07'E", "Marnage VE":"~7.5 m", "Marnage ME":"~2.8 m", "Niveau moyen":"4.60 m" },
    cst:[
      {n:"M2",A:2.400,G:67.8},{n:"S2",A:0.850,G:104.5},{n:"N2",A:0.500,G:44.5},{n:"K2",A:0.237,G:105.5},
      {n:"K1",A:0.095,G:50.5},{n:"O1",A:0.063,G:15.5},{n:"M4",A:0.148,G:214.5},{n:"MS4",A:0.083,G:237.5},
    ]
  },
  "CAEN":{
    name:"Caen-Ouistreham", region:"Calvados (14)", Z0:3.900, M2_A:2.070,
    info:{ "Lat/Lon":"49°17'N 0°15'O", "Marnage VE":"~6.2 m", "Marnage ME":"~2.4 m", "Niveau moyen":"3.90 m" },
    cst:[
      {n:"M2",A:2.070,G:62.5},{n:"S2",A:0.720,G:99.5},{n:"N2",A:0.431,G:39.2},{n:"K2",A:0.200,G:100.8},
      {n:"K1",A:0.085,G:46.0},{n:"O1",A:0.058,G:10.0},{n:"M4",A:0.120,G:195.0},{n:"MS4",A:0.065,G:218.0},
    ]
  },
  "GRANVILLE":{
    name:"Granville", region:"Manche (50)", Z0:7.200, M2_A:3.790,
    info:{ "Lat/Lon":"48°50'N 1°36'O", "Marnage VE":"~13 m", "Marnage ME":"~5.0 m", "Parmi les plus fortes de France":"-" },
    cst:[
      {n:"M2",A:3.790,G:81.2},{n:"S2",A:1.320,G:113.5},{n:"N2",A:0.789,G:58.0},{n:"K2",A:0.367,G:115.0},
      {n:"K1",A:0.128,G:56.0},{n:"O1",A:0.091,G:21.0},{n:"M4",A:0.210,G:232.0},{n:"MS4",A:0.115,G:255.0},
    ]
  },
  // ── NORD ──
  "CALAIS":{
    name:"Calais", region:"Pas-de-Calais (62)", Z0:4.100, M2_A:1.990,
    info:{ "Lat/Lon":"50°58'N 1°51'E", "Marnage VE":"~6.8 m", "Marnage ME":"~2.6 m", "Niveau moyen":"4.10 m" },
    cst:[
      {n:"M2",A:1.990,G:30.5},{n:"S2",A:0.755,G:71.5},{n:"N2",A:0.415,G:7.5},{n:"K2",A:0.210,G:73.0},
      {n:"K1",A:0.093,G:25.5},{n:"O1",A:0.058,G:353.5},{n:"M4",A:0.095,G:118.0},{n:"MS4",A:0.048,G:140.0},
    ]
  },
  "DUNKERQUE":{
    name:"Dunkerque", region:"Nord (59)", Z0:3.000, M2_A:1.530,
    info:{ "Lat/Lon":"51°02'N 2°22'E", "Marnage VE":"~5.0 m", "Marnage ME":"~1.9 m", "Niveau moyen":"3.00 m" },
    cst:[
      {n:"M2",A:1.530,G:28.5},{n:"S2",A:0.580,G:70.0},{n:"N2",A:0.319,G:5.5},{n:"K2",A:0.162,G:72.0},
      {n:"K1",A:0.074,G:23.0},{n:"O1",A:0.047,G:350.5},{n:"M4",A:0.075,G:116.0},{n:"MS4",A:0.038,G:138.0},
    ]
  },
  // ── ATLANTIQUE SUD ──
  "LA-ROCHELLE":{
    name:"La Rochelle", region:"Charente-Maritime (17)", Z0:3.300, M2_A:1.680,
    info:{ "Lat/Lon":"46°09'N 1°09'O", "Marnage VE":"~5.8 m", "Marnage ME":"~2.2 m", "Niveau moyen":"3.30 m" },
    cst:[
      {n:"M2",A:1.680,G:71.5},{n:"S2",A:0.570,G:101.5},{n:"N2",A:0.350,G:49.5},{n:"K2",A:0.159,G:103.0},
      {n:"K1",A:0.058,G:47.5},{n:"O1",A:0.044,G:16.5},{n:"M4",A:0.050,G:195.0},{n:"MS4",A:0.029,G:218.0},
    ]
  },
  "ROYAN":{
    name:"Royan", region:"Charente-Maritime (17)", Z0:3.100, M2_A:1.590,
    info:{ "Lat/Lon":"45°37'N 1°01'O", "Marnage VE":"~5.3 m", "Marnage ME":"~2.0 m", "Niveau moyen":"3.10 m" },
    cst:[
      {n:"M2",A:1.590,G:72.0},{n:"S2",A:0.540,G:102.5},{n:"N2",A:0.331,G:50.0},{n:"K2",A:0.150,G:103.5},
      {n:"K1",A:0.055,G:48.0},{n:"O1",A:0.041,G:17.0},{n:"M4",A:0.047,G:197.0},{n:"MS4",A:0.027,G:220.0},
    ]
  },
  "BORDEAUX":{
    name:"Bordeaux (Pauillac)", region:"Gironde (33)", Z0:2.600, M2_A:1.340,
    info:{ "Lat/Lon":"45°12'N 0°45'O", "Marnage VE":"~4.5 m", "Marnage ME":"~1.7 m", "Estuaire Gironde":"-" },
    cst:[
      {n:"M2",A:1.340,G:88.5},{n:"S2",A:0.456,G:120.0},{n:"N2",A:0.279,G:66.5},{n:"K2",A:0.127,G:121.5},
      {n:"K1",A:0.046,G:60.5},{n:"O1",A:0.034,G:28.5},{n:"M4",A:0.045,G:218.0},{n:"MS4",A:0.025,G:242.0},
    ]
  },
  "ARCACHON":{
    name:"Arcachon", region:"Gironde (33)", Z0:2.400, M2_A:1.170,
    info:{ "Lat/Lon":"44°40'N 1°10'O", "Marnage VE":"~3.8 m", "Marnage ME":"~1.4 m", "Bassin d'Arcachon":"-" },
    cst:[
      {n:"M2",A:1.170,G:75.0},{n:"S2",A:0.398,G:106.0},{n:"N2",A:0.244,G:53.0},{n:"K2",A:0.111,G:107.5},
      {n:"K1",A:0.040,G:50.0},{n:"O1",A:0.030,G:19.0},{n:"M4",A:0.038,G:202.0},{n:"MS4",A:0.022,G:225.0},
    ]
  },
  // ── MÉDITERRANÉE ──
  "MARSEILLE":{
    name:"Marseille", region:"Bouches-du-Rhône (13)", Z0:0.200, M2_A:0.140,
    info:{ "Lat/Lon":"43°18'N 5°22'E", "Marnage VE":"~0.3 m", "Marnage ME":"~0.1 m", "Note":"Marées très faibles en Méditerranée" },
    cst:[
      {n:"M2",A:0.140,G:320.0},{n:"S2",A:0.048,G:355.0},{n:"K1",A:0.025,G:270.0},{n:"O1",A:0.015,G:240.0},
    ]
  },
  "NICE":{
    name:"Nice", region:"Alpes-Maritimes (06)", Z0:0.150, M2_A:0.105,
    info:{ "Lat/Lon":"43°42'N 7°16'E", "Marnage VE":"~0.2 m", "Marnage ME":"~0.1 m", "Note":"Marées très faibles en Méditerranée" },
    cst:[
      {n:"M2",A:0.105,G:318.0},{n:"S2",A:0.036,G:353.0},{n:"K1",A:0.020,G:268.0},{n:"O1",A:0.012,G:238.0},
    ]
  },
};

// ── Hauteur de marée à un instant donné ─────────────────────
function tideHeight(portId, date) {
  var p = PORTS[portId];
  var V = equilibriumArgs(date);
  var nc = nodalCorrections(date);
  var deg = Math.PI / 180;
  var h = p.Z0;
  for (var i = 0; i < p.cst.length; i++) {
    var c = p.cst[i];
    var vi = V[c.n]  || 0;
    var fi = (nc[c.n] || {f:1}).f;
    var ui = (nc[c.n] || {u:0}).u;
    h += fi * c.A * Math.cos((vi + ui - c.G) * deg);
  }
  // Note : pas de clipping — les BM négatives (vives-eaux) restent négatives
  return h;
}

// ── Trouver les extrêmes (PM/BM) sur 24h ────────────────────
function findExtrema(portId, date) {
  var start = new Date(date);
  start.setHours(0, 0, 0, 0);
  var pts = [];
  for (var m = 0; m <= 1440; m += 2) {
    var t = new Date(start.getTime() + m * 60000);
    pts.push({ t: t, h: tideHeight(portId, t) });
  }
  var extrema = [];
  for (var i = 2; i < pts.length - 2; i++) {
    var h = pts[i].h;
    if (h > pts[i-1].h && h > pts[i-2].h && h > pts[i+1].h && h > pts[i+2].h)
      extrema.push({ type:'PM', t:pts[i].t, h:h });
    else if (h < pts[i-1].h && h < pts[i-2].h && h < pts[i+1].h && h < pts[i+2].h)
      extrema.push({ type:'BM', t:pts[i].t, h:h });
  }
  // Dédoublonnage (si deux extrêmes du même type en moins de 90 min → garder le + marqué)
  var filtered = [];
  for (var j = 0; j < extrema.length; j++) {
    var e = extrema[j];
    var last = filtered[filtered.length-1];
    if (last && last.type === e.type && Math.abs(e.t - last.t) < 90*60000) {
      if ((e.type==='PM' && e.h > last.h) || (e.type==='BM' && e.h < last.h))
        filtered[filtered.length-1] = e;
    } else {
      filtered.push(e);
    }
  }
  return filtered;
}

// ── Coefficient SHOM ──────────────────────────────────────────
// Le SHOM calcule le coefficient à partir du marnage à Brest (port de référence).
// Référence : marnage vive-eau = 6.10 m → coeff 100
function calcCoeff(portId, date) {
  var extremaBrest = findExtrema('BREST', date);
  var PMs = extremaBrest.filter(function(e){ return e.type === 'PM'; });
  var BMs = extremaBrest.filter(function(e){ return e.type === 'BM'; });
  if (!PMs.length || !BMs.length) return 70;
  var maxPM = Math.max.apply(null, PMs.map(function(e){ return e.h; }));
  var minBM = Math.min.apply(null, BMs.map(function(e){ return e.h; }));
  var marnage = maxPM - minBM;
  return Math.min(120, Math.max(20, Math.round(marnage / 6.10 * 100)));
}

// ── Formatage ────────────────────────────────────────────────
function fmtTime(date) {
  return date.toLocaleTimeString('fr-FR',{hour:'2-digit',minute:'2-digit',hour12:false});
}
function fmtDateLong(d) {
  return d.toLocaleDateString('fr-FR',{weekday:'long',day:'numeric',month:'long',year:'numeric'});
}
function coeffColor(c) {
  if (c >= 100) return '#0F4F6B';
  if (c >= 70)  return '#1A6B8A';
  if (c >= 45)  return '#4AA8C4';
  return '#2A9D8F';
}
function coeffLabel(c) {
  if (c >= 100) return 'Vive-eau exceptionnelle';
  if (c >= 70)  return 'Vive-eau';
  if (c >= 45)  return 'Marée moyenne';
  return 'Morte-eau';
}

// ── Rendu aujourd'hui ────────────────────────────────────────
var _lastCoeff = null;

function renderToday(portId, date) {
  var extrema = findExtrema(portId, date);
  var coeff   = calcCoeff(portId, date);
  var port    = PORTS[portId];

  document.getElementById('todayTitle').textContent = 'Marées du jour — ' + port.name;
  document.getElementById('todayDate').textContent  = fmtDateLong(date) + ' · ' + coeffLabel(coeff);

  var badge = document.getElementById('coeffBadge');
  badge.textContent   = 'Coeff. ' + coeff;
  badge.style.background   = coeffColor(coeff) + '44';
  badge.style.borderColor  = coeffColor(coeff) + '99';

  // petite animation pulse si le coefficient a changé
  if (_lastCoeff !== null && _lastCoeff !== coeff) {
    badge.classList.remove('pulse');
    void badge.offsetWidth; // force reflow
    badge.classList.add('pulse');
  }
  _lastCoeff = coeff;

  // Sidebar port info
  var rows = Object.entries(port.info).map(function(entry){
    return '<div class="pi-row"><span class="pi-label">' + entry[0] +
           '</span><span class="pi-val">' + entry[1] + '</span></div>';
  }).join('');
  document.getElementById('portInfoRows').innerHTML =
    '<div style="font-size:.82rem;font-weight:700;color:var(--o900);margin-bottom:.5rem">' + port.name + '</div>' +
    '<div style="font-size:.72rem;color:var(--text-l);margin-bottom:.6rem">' + port.region + '</div>' + rows;

  // Grille des horaires
  var container = document.getElementById('todayTides');
  var cols = Math.min(4, extrema.length) || 1;
  container.style.gridTemplateColumns = 'repeat(' + cols + ',1fr)';

  if (!extrema.length) {
    container.innerHTML = '<div style="grid-column:1/-1;padding:2rem;text-align:center;color:var(--text-l)">Pas de données pour ce port</div>';
    return;
  }

  container.innerHTML = extrema.map(function(e){
    return '<div class="tide-item">' +
      '<div class="tide-type ' + e.type.toLowerCase() + '">' + (e.type==='PM' ? '▲ Pleine mer' : '▼ Basse mer') + '</div>' +
      '<div class="tide-time">' + fmtTime(e.t) + '</div>' +
      '<div class="tide-height">' + Math.max(0, e.h).toFixed(2) + ' m</div>' +
      (e.type==='PM' ? '<div class="tide-coeff">Coeff. ' + coeff + '</div>' : '') +
    '</div>';
  }).join('');
}

// ── Graphique 24h ────────────────────────────────────────────
function renderChart(portId, date) {
  var canvas = document.getElementById('tideChart');
  var ctx    = canvas.getContext('2d');
  var W = canvas.offsetWidth, H = 190;
  canvas.width  = W * devicePixelRatio;
  canvas.height = H * devicePixelRatio;
  canvas.style.width  = W + 'px';
  canvas.style.height = H + 'px';
  ctx.scale(devicePixelRatio, devicePixelRatio);
  ctx.clearRect(0, 0, W, H);

  var pad = {t:14, b:28, l:40, r:12};
  var cW = W - pad.l - pad.r;
  var cH = H - pad.t - pad.b;

  var start = new Date(date);
  start.setHours(0, 0, 0, 0);

  var pts = [];
  for (var m = 0; m <= 1440; m += 5) {
    pts.push({ x: m/1440, h: tideHeight(portId, new Date(start.getTime() + m*60000)) });
  }

  var minH = Math.min.apply(null, pts.map(function(p){ return p.h; }));
  var maxH = Math.max.apply(null, pts.map(function(p){ return p.h; }));
  var rng  = maxH - minH || 1;

  var tx = function(x){ return pad.l + x * cW; };
  var ty = function(h){ return pad.t + cH - ((h - minH) / rng) * cH; };

  // Grille horizontale
  for (var i = 0; i <= 4; i++) {
    var y = pad.t + (cH/4) * i;
    ctx.strokeStyle = 'rgba(0,119,182,.09)';
    ctx.lineWidth = 1;
    ctx.beginPath(); ctx.moveTo(pad.l, y); ctx.lineTo(pad.l + cW, y); ctx.stroke();
    ctx.fillStyle = '#5A7A9A';
    ctx.font = '600 10px Inter';
    ctx.textAlign = 'right';
    ctx.fillText((maxH - (rng/4)*i).toFixed(1) + 'm', pad.l - 5, y + 4);
  }

  // Axe temps
  ctx.fillStyle = '#5A7A9A';
  ctx.font = '600 10px Inter';
  ctx.textAlign = 'center';
  for (var h = 0; h <= 24; h += 6) {
    ctx.fillText(h + 'h', tx(h/24), H - 6);
  }

  // Gradient de remplissage
  var grad = ctx.createLinearGradient(0, pad.t, 0, pad.t + cH);
  grad.addColorStop(0,   'rgba(0,119,182,.28)');
  grad.addColorStop(0.6, 'rgba(0,180,216,.12)');
  grad.addColorStop(1,   'rgba(42,157,143,.03)');

  ctx.beginPath();
  ctx.moveTo(tx(0), ty(minH));
  pts.forEach(function(p){ ctx.lineTo(tx(p.x), ty(p.h)); });
  ctx.lineTo(tx(1), ty(minH));
  ctx.closePath();
  ctx.fillStyle = grad;
  ctx.fill();

  // Courbe principale
  ctx.beginPath();
  pts.forEach(function(p, idx){
    if (idx === 0) ctx.moveTo(tx(p.x), ty(p.h));
    else ctx.lineTo(tx(p.x), ty(p.h));
  });
  ctx.strokeStyle = '#0077B6';
  ctx.lineWidth = 2.8;
  ctx.lineJoin  = 'round';
  ctx.lineCap   = 'round';
  ctx.stroke();

  // Marqueur heure actuelle (si aujourd'hui)
  var now = new Date();
  if (now.toDateString() === date.toDateString()) {
    var frac = (now.getHours()*60 + now.getMinutes()) / 1440;
    var nh   = tideHeight(portId, now);
    var nx   = tx(frac);
    var ny   = ty(nh);
    ctx.beginPath(); ctx.moveTo(nx, pad.t); ctx.lineTo(nx, pad.t + cH);
    ctx.strokeStyle = 'rgba(230,126,34,.5)';
    ctx.lineWidth = 1.5;
    ctx.setLineDash([4, 3]);
    ctx.stroke();
    ctx.setLineDash([]);
    ctx.beginPath(); ctx.arc(nx, ny, 5, 0, Math.PI*2);
    ctx.fillStyle = '#E67E22'; ctx.fill();
    ctx.fillStyle = '#E67E22';
    ctx.font = 'bold 10px Inter';
    ctx.textAlign = 'center';
    ctx.fillText(nh.toFixed(2) + 'm', nx, ny - 9);
  }
}

// ── Tableau 7 jours ──────────────────────────────────────────
function renderWeek(portId, baseDate) {
  var html = '';
  for (var d = 0; d < 7; d++) {
    var date    = new Date(baseDate);
    date.setDate(baseDate.getDate() + d);
    var extrema = findExtrema(portId, date);
    var coeff   = calcCoeff(portId, date);
    var isToday = date.toDateString() === new Date().toDateString();
    var col     = coeffColor(coeff);

    html += '<div class="week-row' + (isToday ? ' today' : '') + '">' +
      '<div class="week-day">' +
        '<div class="week-day-name">' + date.toLocaleDateString('fr-FR',{weekday:'short'}) + ' ' + date.getDate() + '</div>' +
        '<div class="week-day-date" style="color:' + col + ';font-weight:700;font-size:.78rem">Coeff. ' + coeff + '</div>' +
      '</div>' +
      '<div class="week-tides-row">' +
        extrema.map(function(e){
          return '<div class="wt-item">' +
            '<span class="wt-type ' + e.type.toLowerCase() + '">' + e.type + '</span>' +
            '<span>' + fmtTime(e.t) + '</span>' +
            '<span class="wt-h">' + Math.max(0, e.h).toFixed(2) + 'm</span>' +
            (e.type==='PM' ? '<span class="wt-c">' + coeff + '</span>' : '') +
          '</div>';
        }).join('') +
      '</div>' +
    '</div>';
  }
  document.getElementById('weekTable').innerHTML = html;
}

// ── Chargement principal ─────────────────────────────────────
function loadTides() {
  var portId  = document.getElementById('portSelect').value;
  var dateStr = document.getElementById('dateInput').value;
  var date    = dateStr ? new Date(dateStr + 'T12:00:00') : new Date();
  date.setHours(12, 0, 0, 0);
  renderToday(portId, date);
  setTimeout(function(){ renderChart(portId, date); }, 50);
  renderWeek(portId, date);
}

document.addEventListener('DOMContentLoaded', function() {
  var t = new Date();
  document.getElementById('dateInput').value =
    t.getFullYear() + '-' +
    String(t.getMonth()+1).padStart(2,'0') + '-' +
    String(t.getDate()).padStart(2,'0');

  loadTides();

  window.addEventListener('resize', function() {
    var pid  = document.getElementById('portSelect').value;
    var dstr = document.getElementById('dateInput').value;
    renderChart(pid, dstr ? new Date(dstr + 'T12:00:00') : new Date());
  });

  // Rafraîchissement auto toutes les 5 min
  setInterval(loadTides, 300000);
});

document.getElementById('portSelect').addEventListener('change', loadTides);
document.getElementById('dateInput').addEventListener('change', loadTides);

// Paramètre ?port= dans l'URL
(function() {
  var params = new URLSearchParams(window.location.search);
  var p = params.get('port');
  if (p && document.querySelector('#portSelect option[value="' + p + '"]')) {
    document.getElementById('portSelect').value = p;
  }
})();

// ── Service Worker ───────────────────────────────────────────
if ('serviceWorker' in navigator) {
  window.addEventListener('load', function() {
    navigator.serviceWorker.register('/service-worker.js').catch(function(){});
  });
}

// ── Prompt installation PWA ──────────────────────────────────
var _installPrompt = null;
window.addEventListener('beforeinstallprompt', function(e) {
  e.preventDefault();
  _installPrompt = e;
  var btn = document.getElementById('installPwaBtn');
  if (btn) btn.style.display = 'flex';
});
window.addEventListener('appinstalled', function() {
  var btn = document.getElementById('installPwaBtn');
  if (btn) btn.style.display = 'none';
});
function installPwa() {
  if (_installPrompt) {
    _installPrompt.prompt();
    _installPrompt.userChoice.then(function(){ _installPrompt = null; });
  }
}

// ── Alertes grandes marées ───────────────────────────────────
async function activerAlertes() {
  if (!('Notification' in window)) {
    alert('Notifications non supportées sur ce navigateur.');
    return;
  }
  var perm = await Notification.requestPermission();
  if (perm !== 'granted') {
    alert('Notifications refusées. Vous pouvez les activer dans les paramètres.');
    return;
  }
  document.getElementById('alertBtn').textContent = '🔔 Alertes activées';
  document.getElementById('alertBtn').style.background = 'var(--teal)';
  programmerAlertes();
}
function programmerAlertes() {
  var pid   = document.getElementById('portSelect').value;
  var now   = new Date();
  var extrema = findExtrema(pid, now);
  var coeff   = calcCoeff(pid, now);
  if (coeff < 90) return;
  var nextPM = extrema.find(function(e){ return e.type === 'PM' && e.t > now; });
  if (!nextPM) return;
  var diffMin = Math.round((nextPM.t - now) / 60000);
  if (diffMin > 0 && diffMin <= 120) {
    var delai = Math.max(0, (diffMin - 60) * 60000);
    setTimeout(function() {
      new Notification('Marée — ' + PORTS[pid].name, {
        body: 'Grande marée (coeff. ' + coeff + ') — Pleine mer à ' + fmtTime(nextPM.t) +
              ' (' + Math.max(0, nextPM.h).toFixed(2) + ' m)',
        icon: '/icons/icon-192.png',
        tag:  'grande-maree'
      });
    }, delai);
  }
}
