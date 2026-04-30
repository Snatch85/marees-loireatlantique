#!/usr/bin/env python3
"""
Patch all Loire-Atlantique sub-pages:
1. Replace PORTS Loire section with corrected constants (from main index.html)
2. Fix calcCoeff to use Brest-based SHOM-standard coefficient
3. Update Brest PORTS entry with calibrated values
"""
import re
import os

# Sub-pages to patch
SUBPAGES = [
    r"marees-saint-nazaire\index.html",
    r"marees-la-baule\index.html",
    r"marees-le-croisic\index.html",
    r"marees-pornic\index.html",
    r"marees-piriac-sur-mer\index.html",
    r"marees-la-turballe\index.html",
    r"marees-saint-brevin-les-pins\index.html",
    r"marees-prefailles\index.html",
    r"marees-paimboeuf\index.html",
]

# Corrected Loire-Atlantique PORTS block (to replace in sub-pages)
NEW_LOIRE_BLOCK = '''  // ── LOIRE-ATLANTIQUE (44) ──
  // Constantes recalibrees vs SHOM maree.info avril 2026
  // Corrections : G_M2 +22.9deg, G_S2 +29.5deg | A_M2 x0.626, A_S2 x0.778 | Z0 +0.161m
  "SAINT-NAZAIRE":{
    name:"Saint-Nazaire", region:"Loire-Atlantique (44)", Z0:3.308, M2_A:1.563,
    info:{ "Lat/Lon":"47\u00b016'N 2\u00b012'O", "Marnage VE":"~5.2 m", "Marnage ME":"~2.1 m", "Niveau moyen":"3.31 m" },
    cst:[
      {n:"M2", A:1.563, G:93.2}, {n:"S2", A:0.662, G:128.7}, {n:"N2", A:0.563, G:85.8},
      {n:"K2", A:0.194, G:134.2},{n:"NU2",A:0.100, G:85.7},  {n:"MU2",A:0.024, G:88.1},
      {n:"L2", A:0.030, G:116.0},{n:"T2", A:0.022, G:98.5},  {n:"p2N2",A:0.070,G:102.4},
      {n:"K1", A:0.072, G:38.6}, {n:"O1", A:0.108, G:309.4}, {n:"P1", A:0.024, G:29.4},
      {n:"Q1", A:0.013, G:278.3},{n:"M4", A:0.091, G:237.3}, {n:"MN4",A:0.022, G:223.0},
      {n:"MS4",A:0.060, G:264.7},{n:"M6", A:0.028, G:316.7}, {n:"MK3",A:0.008, G:179.8},
    ]
  },
  "LE-CROISIC":{
    name:"Le Croisic", region:"Loire-Atlantique (44)", Z0:3.191, M2_A:1.502,
    info:{ "Lat/Lon":"47\u00b017'N 2\u00b031'O", "Marnage VE":"~5.0 m", "Marnage ME":"~2.0 m", "Niveau moyen":"3.03 m" },
    cst:[
      {n:"M2",A:1.502,G:90.0},{n:"S2",A:0.638,G:124.8},{n:"N2",A:0.500,G:82.8},{n:"K2",A:0.228,G:130.6},
      {n:"NU2",A:0.096,G:82.8},{n:"K1",A:0.076,G:28.6},{n:"O1",A:0.058,G:302.3},
      {n:"M4",A:0.088,G:233.8},{n:"MS4",A:0.056,G:261.4},{n:"MN4",A:0.020,G:220.6},
    ]
  },
  "LA-BAULE":{
    name:"La Baule-Escoublac", region:"Loire-Atlantique (44)", Z0:3.171, M2_A:1.509,
    info:{ "Lat/Lon":"47\u00b017'N 2\u00b024'O", "Marnage VE":"~5.0 m", "Marnage ME":"~1.9 m", "Niveau moyen":"3.01 m" },
    cst:[
      {n:"M2",A:1.509,G:91.0},{n:"S2",A:0.642,G:125.8},{n:"N2",A:0.503,G:83.8},{n:"K2",A:0.230,G:131.6},
      {n:"NU2",A:0.097,G:83.8},{n:"K1",A:0.077,G:29.1},{n:"O1",A:0.059,G:302.8},
      {n:"M4",A:0.089,G:234.8},{n:"MS4",A:0.057,G:262.4},
    ]
  },
  "BATZ":{
    name:"Batz-sur-Mer", region:"Loire-Atlantique (44)", Z0:3.181, M2_A:1.506,
    info:{ "Lat/Lon":"47\u00b017'N 2\u00b029'O", "Marnage VE":"~5.0 m", "Marnage ME":"~1.9 m", "Niveau moyen":"3.02 m" },
    cst:[
      {n:"M2",A:1.506,G:90.5},{n:"S2",A:0.640,G:125.3},{n:"N2",A:0.501,G:83.3},{n:"K2",A:0.229,G:131.1},
      {n:"NU2",A:0.096,G:83.3},{n:"K1",A:0.076,G:28.8},{n:"O1",A:0.058,G:302.5},
      {n:"M4",A:0.088,G:234.3},{n:"MS4",A:0.056,G:261.9},
    ]
  },
  "LE-POULIGUEN":{
    name:"Le Pouliguen", region:"Loire-Atlantique (44)", Z0:3.171, M2_A:1.507,
    info:{ "Lat/Lon":"47\u00b016'N 2\u00b025'O", "Marnage VE":"~5.0 m", "Marnage ME":"~1.9 m", "Niveau moyen":"3.01 m" },
    cst:[
      {n:"M2",A:1.507,G:90.8},{n:"S2",A:0.641,G:125.6},{n:"N2",A:0.502,G:83.6},{n:"K2",A:0.229,G:131.4},
      {n:"NU2",A:0.096,G:83.6},{n:"K1",A:0.077,G:29.0},{n:"O1",A:0.059,G:302.7},
      {n:"M4",A:0.088,G:234.8},{n:"MS4",A:0.057,G:262.4},
    ]
  },
  "LA-TURBALLE":{
    name:"La Turballe", region:"Loire-Atlantique (44)", Z0:3.201, M2_A:1.515,
    info:{ "Lat/Lon":"47\u00b021'N 2\u00b031'O", "Marnage VE":"~5.0 m", "Marnage ME":"~1.9 m", "Niveau moyen":"3.04 m" },
    cst:[
      {n:"M2",A:1.515,G:91.1},{n:"S2",A:0.643,G:126.5},{n:"N2",A:0.505,G:83.8},{n:"K2",A:0.230,G:131.6},
      {n:"NU2",A:0.097,G:83.8},{n:"K1",A:0.077,G:29.1},{n:"O1",A:0.059,G:303.3},
      {n:"M4",A:0.089,G:234.8},{n:"MS4",A:0.057,G:262.4},
    ]
  },
  "PIRIAC":{
    name:"Piriac-sur-Mer", region:"Loire-Atlantique (44)", Z0:3.201, M2_A:1.514,
    info:{ "Lat/Lon":"47\u00b023'N 2\u00b033'O", "Marnage VE":"~5.0 m", "Marnage ME":"~1.9 m", "Niveau moyen":"3.04 m" },
    cst:[
      {n:"M2",A:1.514,G:91.0},{n:"S2",A:0.642,G:126.4},{n:"N2",A:0.504,G:83.8},{n:"K2",A:0.230,G:131.5},
      {n:"NU2",A:0.097,G:83.8},{n:"K1",A:0.077,G:29.0},{n:"O1",A:0.059,G:303.2},
      {n:"M4",A:0.089,G:234.6},{n:"MS4",A:0.057,G:262.4},
    ]
  },
  "PORNIC":{
    name:"Pornic", region:"Loire-Atlantique (44)", Z0:3.111, M2_A:1.471,
    info:{ "Lat/Lon":"47\u00b007'N 2\u00b006'O", "Marnage VE":"~4.9 m", "Marnage ME":"~1.9 m", "Niveau moyen":"2.95 m" },
    cst:[
      {n:"M2",A:1.471,G:91.0},{n:"S2",A:0.622,G:126.8},{n:"N2",A:0.490,G:83.8},{n:"K2",A:0.222,G:132.6},
      {n:"NU2",A:0.093,G:83.8},{n:"K1",A:0.074,G:28.6},{n:"O1",A:0.057,G:302.3},
      {n:"M4",A:0.082,G:230.8},{n:"MS4",A:0.052,G:258.4},
    ]
  },
  "PREFAILLES":{
    name:"Pr\u00e9failles", region:"Loire-Atlantique (44)", Z0:3.131, M2_A:1.481,
    info:{ "Lat/Lon":"47\u00b008'N 2\u00b013'O", "Marnage VE":"~4.9 m", "Marnage ME":"~1.9 m", "Niveau moyen":"2.97 m" },
    cst:[
      {n:"M2",A:1.481,G:91.0},{n:"S2",A:0.627,G:126.8},{n:"N2",A:0.493,G:83.8},{n:"K2",A:0.224,G:132.6},
      {n:"NU2",A:0.094,G:83.8},{n:"K1",A:0.075,G:28.6},{n:"O1",A:0.057,G:302.3},
      {n:"M4",A:0.083,G:231.8},{n:"MS4",A:0.053,G:259.4},
    ]
  },
  "SAINT-BREVIN":{
    name:"Saint-Brevin-les-Pins", region:"Loire-Atlantique (44)", Z0:3.261, M2_A:1.546,
    info:{ "Lat/Lon":"47\u00b014'N 2\u00b010'O", "Marnage VE":"~5.1 m", "Marnage ME":"~2.0 m", "Niveau moyen":"3.10 m" },
    cst:[
      {n:"M2",A:1.546,G:92.8},{n:"S2",A:0.657,G:128.3},{n:"N2",A:0.515,G:85.4},{n:"K2",A:0.234,G:133.6},
      {n:"NU2",A:0.099,G:85.4},{n:"K1",A:0.078,G:30.4},{n:"O1",A:0.059,G:304.7},
      {n:"M4",A:0.090,G:236.8},{n:"MS4",A:0.059,G:264.4},{n:"M6",A:0.022,G:310.7},
    ]
  },
  "PAIMBOEUF":{
    name:"Paimboeuf (Estuaire Loire)", region:"Loire-Atlantique (44)", Z0:3.361, M2_A:1.584,
    info:{ "Lat/Lon":"47\u00b017'N 2\u00b001'O", "Marnage VE":"~5.3 m", "Marnage ME":"~2.1 m", "Estuaire Loire":"-" },
    cst:[
      {n:"M2",A:1.584,G:97.0},{n:"S2",A:0.673,G:132.8},{n:"N2",A:0.527,G:89.6},{n:"K2",A:0.241,G:138.1},
      {n:"NU2",A:0.101,G:89.6},{n:"K1",A:0.080,G:34.1},{n:"O1",A:0.061,G:307.8},
      {n:"M4",A:0.110,G:245.8},{n:"MS4",A:0.070,G:273.4},{n:"M6",A:0.048,G:326.7},
      {n:"MK3",A:0.012,G:185.8},
    ]
  },
  "SAINT-GILDAS":{
    name:"Saint-Gildas (Pointe)", region:"Loire-Atlantique (44)", Z0:3.141, M2_A:1.484,
    info:{ "Lat/Lon":"47\u00b005'N 2\u00b014'O", "Marnage VE":"~4.9 m", "Marnage ME":"~1.9 m", "Niveau moyen":"2.98 m" },
    cst:[
      {n:"M2",A:1.484,G:90.5},{n:"S2",A:0.629,G:125.8},{n:"N2",A:0.493,G:83.3},{n:"K2",A:0.225,G:131.6},
      {n:"NU2",A:0.094,G:83.3},{n:"K1",A:0.075,G:28.8},{n:"O1",A:0.058,G:302.8},
      {n:"M4",A:0.083,G:231.8},{n:"MS4",A:0.053,G:259.4},
    ]
  },'''

# Corrected BREST entry (to replace in sub-pages Bretagne section)
NEW_BREST_ENTRY = '''  "BREST":{
    name:"Brest", region:"Finist\u00e8re (29)", Z0:4.030, M2_A:2.210,
    info:{ "Lat/Lon":"48\u00b023'N 4\u00b030'O", "Marnage VE":"~6.5 m", "Marnage ME":"~2.5 m", "Port de r\u00e9f\u00e9rence SHOM":"-" },
    cst:[
      {n:"M2",A:2.210,G:90.2},{n:"S2",A:0.800,G:128.4},{n:"N2",A:0.470,G:82.6},{n:"K2",A:0.220,G:135.2},
      {n:"K1",A:0.047,G:30.7},{n:"O1",A:0.105,G:305.4},{n:"P1",A:0.024,G:29.9},{n:"Q1",A:0.011,G:282.8},
      {n:"M4",A:0.065,G:200.8},{n:"MS4",A:0.039,G:226.4},
    ]
  },'''

# New calcCoeff function (Brest-based, SHOM standard)
NEW_CALC_COEFF = '''// ── Coefficient SHOM (marnage Brest / 6.10m = reference officielle) ──────
function calcCoeff(portId, extrema, date) {
  // Methode officielle SHOM : coefficient = marnage a Brest / 6.10 * 100
  if (date) {
    const brestEx = findExtrema('BREST', date);
    const pms = brestEx.filter(e => e.type==='PM');
    const bms = brestEx.filter(e => e.type==='BM');
    if (pms.length && bms.length) {
      const marnage = Math.max(...pms.map(e=>e.h)) - Math.min(...bms.map(e=>e.h));
      return Math.min(120, Math.max(20, Math.round(marnage / 6.10 * 100)));
    }
  }
  // Fallback : estimation locale si date non disponible
  const pms = extrema.filter(e => e.type==='PM');
  const bms = extrema.filter(e => e.type==='BM');
  if (!pms.length || !bms.length) return 70;
  const marnage = Math.max(...pms.map(e=>e.h)) - Math.min(...bms.map(e=>e.h));
  return Math.min(120, Math.max(20, Math.round(marnage / 5.20 * 100)));
}'''

base = r"C:\Users\33629\Desktop\Claude Cooode\marees-loire"

for rel_path in SUBPAGES:
    fpath = os.path.join(base, rel_path)
    if not os.path.exists(fpath):
        print(f"NOT FOUND: {fpath}")
        continue

    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    # 1. Replace Loire-Atlantique PORTS block
    # Pattern: from "// ── LOIRE-ATLANTIQUE" to "// ── BRETAGNE"
    loire_pattern = r'(  // ── LOIRE-ATLANTIQUE \(44\) ──.*?)(?=  // ── BRETAGNE)'
    m = re.search(loire_pattern, content, re.DOTALL)
    if m:
        content = content[:m.start()] + NEW_LOIRE_BLOCK + '\n' + content[m.end():]
        print(f"[OK] Loire PORTS replaced in {rel_path}")
    else:
        print(f"[!!] Loire PORTS pattern NOT FOUND in {rel_path}")

    # 2. Replace BREST entry
    brest_pattern = r'"BREST":\{.*?name:"Brest".*?\},\n'
    m = re.search(brest_pattern, content, re.DOTALL)
    if m:
        content = content[:m.start()] + NEW_BREST_ENTRY + '\n' + content[m.end():]
        print(f"[OK] Brest entry replaced in {rel_path}")
    else:
        print(f"[!!] Brest entry NOT FOUND in {rel_path}")

    # 3. Replace calcCoeff function
    coeff_pattern = r'// ── Coefficient ──.*?^}'
    m = re.search(coeff_pattern, content, re.DOTALL | re.MULTILINE)
    if m:
        content = content[:m.start()] + NEW_CALC_COEFF + content[m.end():]
        print(f"[OK] calcCoeff replaced in {rel_path}")
    else:
        print(f"[!!] calcCoeff NOT FOUND in {rel_path}")

    # 4. Update calcCoeff call sites to pass date
    # Pattern: calcCoeff(portId, extrema) → calcCoeff(portId, extrema, date)
    # Only in renderToday(portId, date) and renderWeek context
    content = re.sub(
        r'calcCoeff\((\w+),\s*(\w+)\)(?!\s*[,;]?\s*// )',
        lambda m2: (
            'calcCoeff(%s, %s, date)' % (m2.group(1), m2.group(2))
            if 'date' not in m2.group(0) else m2.group(0)
        ),
        content
    )
    print(f"[OK] calcCoeff calls updated in {rel_path}")

    if content != original:
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"[SAVED] {rel_path}")
    else:
        print(f"[UNCHANGED] {rel_path}")
    print()
