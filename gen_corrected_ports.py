#!/usr/bin/env python3
"""
Generates corrected harmonic constants for index.html Loire-Atlantique ports.
Corrections derived from:
  - Brest:          full calibration vs SHOM reference (RMSE 2.7cm)
  - Saint-Nazaire:  gradient-descent calibration vs maree.info (RMSE 8.3cm)

Systematic offsets (wrong source, same for all nearby Atlantic ports):
  DK_M2  = +22.9   DK_S2  = +29.5   DK_N2  = +36.7
  DK_K2  = +34.4   DK_K1  = -15.1   DK_O1  = +292.8 (= -67.2 mod360)
  DK_NU2 = +36.7   DK_MU2 = +16.3   (MU2 = 2M2-S2)
  DK_M4  = +45.8   DK_MS4 = +52.4   DK_MN4 = +59.6
  DK_M6  = +68.7   DK_MK3 = +7.8    DK_MO3 = -44.3
  DK_p2N2= +73.4   (2N2 ~ 2*N2_offset)
  DK_P1  = -15.1   (same as K1)     DK_Q1  = +292.8 (same as O1)

Amplitude/Z0 corrections from Saint-Nazaire calibration:
  A_M2 *= 0.626    A_S2 *= 0.778    Z0 += 0.161
  Other amplitudes: unchanged (not well-constrained without spring tide data)
"""

mod360 = lambda x: round(((x % 360) + 360) % 360, 1)

# G corrections indexed by constituent name
DG = {
    'M2': 22.9, 'S2': 29.5, 'N2': 36.7, 'K2': 34.4, 'K1': -15.1, 'O1': 292.8,
    'NU2': 36.7, 'MU2': 16.3,
    'L2': 0.0,   'T2': 0.0,  # unchanged (too complex / small)
    'p2N2': 73.4, '2N2': 73.4,
    'P1': -15.1, 'Q1': 292.8,
    'M4': 45.8, 'MS4': 52.4, 'MN4': 59.6, 'M6': 68.7,
    'MK3': 7.8, 'MO3': -44.3,
}

DA_M2 = 0.626   # A_M2 scale factor (from SN calibration)
DA_S2 = 0.778   # A_S2 scale factor
DZ0   = 0.161   # Z0 absolute offset (m)

def corr_g(n, g):
    return mod360(g + DG.get(n, 0))

def corr_a(n, a):
    if n == 'M2': return round(a * DA_M2, 3)
    if n == 'S2': return round(a * DA_S2, 3)
    return round(a, 3)

def fmt_port(name, region, lat_lon, marnage_ve, marnage_me, note, z0, m2_a, cst):
    z0c = round(z0 + DZ0, 3)
    lines = []
    lines.append(f'  "{name}"{{')
    lines.append(f'    name:"{name}", region:"{region}", Z0:{z0c}, M2_A:{round(corr_a("M2", m2_a), 3)},')
    info_parts = [f'"Lat/Lon":"{lat_lon}"']
    info_parts.append(f'"Marnage VE":"{marnage_ve}"')
    info_parts.append(f'"Marnage ME":"{marnage_me}"')
    info_parts.append(f'"{list(note.keys())[0]}":"{list(note.values())[0]}"')
    lines.append(f'    info:{{ {", ".join(info_parts)} }},')
    lines.append(f'    cst:[')
    row = '      '
    for i, (n, a, g) in enumerate(cst):
        entry = '{n:"%s",A:%s,G:%s}' % (n, corr_a(n, a), corr_g(n, g))
        if i < len(cst) - 1:
            row += entry + ','
        else:
            row += entry
        if len(row) > 100 or i == len(cst)-1:
            lines.append(row)
            row = '      '
    lines.append('    ]')
    lines.append('  },')
    return '\n'.join(lines)

# ── SAINT-NAZAIRE: exact optimization values ──────────────────────────────
# Z0=3.308 (was 3.147), amplitudes from calibration
print("""  "SAINT-NAZAIRE":{
    name:"Saint-Nazaire", region:"Loire-Atlantique (44)", Z0:3.308, M2_A:1.563,
    info:{ "Lat/Lon":"47\u00b016'N 2\u00b012'O", "Marnage VE":"~5.2 m", "Marnage ME":"~2.1 m", "Niveau moyen":"3.31 m" },
    cst:[
      // Constantes recalibrees SHOM maree.info avril 2026 (RMSE 8.3cm)
      {n:"M2", A:1.563, G:93.2}, {n:"S2", A:0.662, G:128.7}, {n:"N2", A:0.563, G:85.8},
      {n:"K2", A:0.194, G:134.2},{n:"NU2",A:0.100, G:85.7},  {n:"MU2",A:0.024, G:88.1},
      {n:"L2", A:0.030, G:116.0},{n:"T2", A:0.022, G:98.5},  {n:"p2N2",A:0.070,G:102.4},
      {n:"K1", A:0.072, G:38.6}, {n:"O1", A:0.108, G:309.4}, {n:"P1", A:0.024, G:29.4},
      {n:"Q1", A:0.013, G:278.3},{n:"M4", A:0.091, G:237.3}, {n:"MN4",A:0.022, G:223.0},
      {n:"MS4",A:0.060, G:264.7},{n:"M6", A:0.028, G:316.7}, {n:"MK3",A:0.008, G:179.8},
    ]
  },""")

# ── LE-CROISIC ───────────────────────────────────────────────────────────
cst = [('M2',2.400,67.1),('S2',0.820,95.3),('N2',0.500,46.1),('K2',0.228,96.2),
       ('NU2',0.096,46.1),('K1',0.076,43.7),('O1',0.058,9.5),
       ('M4',0.088,188.0),('MS4',0.056,209.0),('MN4',0.020,161.0)]
print(f"""  "LE-CROISIC":{{
    name:"Le Croisic", region:"Loire-Atlantique (44)", Z0:{round(3.030+DZ0,3)}, M2_A:{round(2.400*DA_M2,3)},
    info:{{ "Lat/Lon":"47\u00b017'N 2\u00b031'O", "Marnage VE":"~5.0 m", "Marnage ME":"~2.0 m", "Niveau moyen":"3.03 m" }},
    cst:[
      {{{','.join('{n:"%s",A:%s,G:%s}'%(n,corr_a(n,a),corr_g(n,g)) for n,a,g in cst[:4])}}},
      {{{','.join('{n:"%s",A:%s,G:%s}'%(n,corr_a(n,a),corr_g(n,g)) for n,a,g in cst[4:])}}},
    ]
  }},""")

# ── LA-BAULE ─────────────────────────────────────────────────────────────
cst = [('M2',2.410,68.1),('S2',0.825,96.3),('N2',0.503,47.1),('K2',0.230,97.2),
       ('NU2',0.097,47.1),('K1',0.077,44.2),('O1',0.059,10.0),
       ('M4',0.089,189.0),('MS4',0.057,210.0)]
print(f"""  "LA-BAULE":{{
    name:"La Baule-Escoublac", region:"Loire-Atlantique (44)", Z0:{round(3.010+DZ0,3)}, M2_A:{round(2.410*DA_M2,3)},
    info:{{ "Lat/Lon":"47\u00b017'N 2\u00b024'O", "Marnage VE":"~5.0 m", "Marnage ME":"~1.9 m", "Niveau moyen":"3.01 m" }},
    cst:[
      {{{','.join('{n:"%s",A:%s,G:%s}'%(n,corr_a(n,a),corr_g(n,g)) for n,a,g in cst[:4])}}},
      {{{','.join('{n:"%s",A:%s,G:%s}'%(n,corr_a(n,a),corr_g(n,g)) for n,a,g in cst[4:])}}},
    ]
  }},""")

# ── BATZ ─────────────────────────────────────────────────────────────────
cst = [('M2',2.405,67.6),('S2',0.822,95.8),('N2',0.501,46.6),('K2',0.229,96.7),
       ('NU2',0.096,46.6),('K1',0.076,43.9),('O1',0.058,9.7),
       ('M4',0.088,188.5),('MS4',0.056,209.5)]
print(f"""  "BATZ":{{
    name:"Batz-sur-Mer", region:"Loire-Atlantique (44)", Z0:{round(3.020+DZ0,3)}, M2_A:{round(2.405*DA_M2,3)},
    info:{{ "Lat/Lon":"47\u00b017'N 2\u00b029'O", "Marnage VE":"~5.0 m", "Marnage ME":"~1.9 m", "Niveau moyen":"3.02 m" }},
    cst:[
      {{{','.join('{n:"%s",A:%s,G:%s}'%(n,corr_a(n,a),corr_g(n,g)) for n,a,g in cst[:4])}}},
      {{{','.join('{n:"%s",A:%s,G:%s}'%(n,corr_a(n,a),corr_g(n,g)) for n,a,g in cst[4:])}}},
    ]
  }},""")

# ── LE-POULIGUEN ──────────────────────────────────────────────────────────
cst = [('M2',2.408,67.9),('S2',0.824,96.1),('N2',0.502,46.9),('K2',0.229,97.0),
       ('NU2',0.096,46.9),('K1',0.077,44.1),('O1',0.059,9.9),
       ('M4',0.088,189.0),('MS4',0.057,210.0)]
print(f"""  "LE-POULIGUEN":{{
    name:"Le Pouliguen", region:"Loire-Atlantique (44)", Z0:{round(3.010+DZ0,3)}, M2_A:{round(2.408*DA_M2,3)},
    info:{{ "Lat/Lon":"47\u00b016'N 2\u00b025'O", "Marnage VE":"~5.0 m", "Marnage ME":"~1.9 m", "Niveau moyen":"3.01 m" }},
    cst:[
      {{{','.join('{n:"%s",A:%s,G:%s}'%(n,corr_a(n,a),corr_g(n,g)) for n,a,g in cst[:4])}}},
      {{{','.join('{n:"%s",A:%s,G:%s}'%(n,corr_a(n,a),corr_g(n,g)) for n,a,g in cst[4:])}}},
    ]
  }},""")

# ── LA-TURBALLE ───────────────────────────────────────────────────────────
cst = [('M2',2.420,68.2),('S2',0.826,97.0),('N2',0.505,47.1),('K2',0.230,97.2),
       ('NU2',0.097,47.1),('K1',0.077,44.2),('O1',0.059,10.5),
       ('M4',0.089,189.0),('MS4',0.057,210.0)]
print(f"""  "LA-TURBALLE":{{
    name:"La Turballe", region:"Loire-Atlantique (44)", Z0:{round(3.040+DZ0,3)}, M2_A:{round(2.420*DA_M2,3)},
    info:{{ "Lat/Lon":"47\u00b021'N 2\u00b031'O", "Marnage VE":"~5.0 m", "Marnage ME":"~1.9 m", "Niveau moyen":"3.04 m" }},
    cst:[
      {{{','.join('{n:"%s",A:%s,G:%s}'%(n,corr_a(n,a),corr_g(n,g)) for n,a,g in cst[:4])}}},
      {{{','.join('{n:"%s",A:%s,G:%s}'%(n,corr_a(n,a),corr_g(n,g)) for n,a,g in cst[4:])}}},
    ]
  }},""")

# ── PIRIAC ────────────────────────────────────────────────────────────────
cst = [('M2',2.418,68.1),('S2',0.825,96.9),('N2',0.504,47.1),('K2',0.230,97.1),
       ('NU2',0.097,47.1),('K1',0.077,44.1),('O1',0.059,10.4),
       ('M4',0.089,188.8),('MS4',0.057,210.0)]
print(f"""  "PIRIAC":{{
    name:"Piriac-sur-Mer", region:"Loire-Atlantique (44)", Z0:{round(3.040+DZ0,3)}, M2_A:{round(2.418*DA_M2,3)},
    info:{{ "Lat/Lon":"47\u00b023'N 2\u00b033'O", "Marnage VE":"~5.0 m", "Marnage ME":"~1.9 m", "Niveau moyen":"3.04 m" }},
    cst:[
      {{{','.join('{n:"%s",A:%s,G:%s}'%(n,corr_a(n,a),corr_g(n,g)) for n,a,g in cst[:4])}}},
      {{{','.join('{n:"%s",A:%s,G:%s}'%(n,corr_a(n,a),corr_g(n,g)) for n,a,g in cst[4:])}}},
    ]
  }},""")

# ── PORNIC ────────────────────────────────────────────────────────────────
cst = [('M2',2.350,68.1),('S2',0.800,97.3),('N2',0.490,47.1),('K2',0.222,98.2),
       ('NU2',0.093,47.1),('K1',0.074,43.7),('O1',0.057,9.5),
       ('M4',0.082,185.0),('MS4',0.052,206.0)]
print(f"""  "PORNIC":{{
    name:"Pornic", region:"Loire-Atlantique (44)", Z0:{round(2.950+DZ0,3)}, M2_A:{round(2.350*DA_M2,3)},
    info:{{ "Lat/Lon":"47\u00b007'N 2\u00b006'O", "Marnage VE":"~4.9 m", "Marnage ME":"~1.9 m", "Niveau moyen":"2.95 m" }},
    cst:[
      {{{','.join('{n:"%s",A:%s,G:%s}'%(n,corr_a(n,a),corr_g(n,g)) for n,a,g in cst[:4])}}},
      {{{','.join('{n:"%s",A:%s,G:%s}'%(n,corr_a(n,a),corr_g(n,g)) for n,a,g in cst[4:])}}},
    ]
  }},""")

# ── PREFAILLES ────────────────────────────────────────────────────────────
cst = [('M2',2.365,68.1),('S2',0.806,97.3),('N2',0.493,47.1),('K2',0.224,98.2),
       ('NU2',0.094,47.1),('K1',0.075,43.7),('O1',0.057,9.5),
       ('M4',0.083,186.0),('MS4',0.053,207.0)]
print(f"""  "PREFAILLES":{{
    name:"Pr\u00e9failles", region:"Loire-Atlantique (44)", Z0:{round(2.970+DZ0,3)}, M2_A:{round(2.365*DA_M2,3)},
    info:{{ "Lat/Lon":"47\u00b008'N 2\u00b013'O", "Marnage VE":"~4.9 m", "Marnage ME":"~1.9 m", "Niveau moyen":"2.97 m" }},
    cst:[
      {{{','.join('{n:"%s",A:%s,G:%s}'%(n,corr_a(n,a),corr_g(n,g)) for n,a,g in cst[:4])}}},
      {{{','.join('{n:"%s",A:%s,G:%s}'%(n,corr_a(n,a),corr_g(n,g)) for n,a,g in cst[4:])}}},
    ]
  }},""")

# ── SAINT-BREVIN ──────────────────────────────────────────────────────────
cst = [('M2',2.470,69.9),('S2',0.844,98.8),('N2',0.515,48.7),('K2',0.234,99.2),
       ('NU2',0.099,48.7),('K1',0.078,45.5),('O1',0.059,11.9),
       ('M4',0.090,191.0),('MS4',0.059,212.0),('M6',0.022,242.0)]
print(f"""  "SAINT-BREVIN":{{
    name:"Saint-Brevin-les-Pins", region:"Loire-Atlantique (44)", Z0:{round(3.100+DZ0,3)}, M2_A:{round(2.470*DA_M2,3)},
    info:{{ "Lat/Lon":"47\u00b014'N 2\u00b010'O", "Marnage VE":"~5.1 m", "Marnage ME":"~2.0 m", "Niveau moyen":"3.10 m" }},
    cst:[
      {{{','.join('{n:"%s",A:%s,G:%s}'%(n,corr_a(n,a),corr_g(n,g)) for n,a,g in cst[:5])}}},
      {{{','.join('{n:"%s",A:%s,G:%s}'%(n,corr_a(n,a),corr_g(n,g)) for n,a,g in cst[5:])}}},
    ]
  }},""")

# ── PAIMBOEUF ─────────────────────────────────────────────────────────────
cst = [('M2',2.530,74.1),('S2',0.865,103.3),('N2',0.527,52.9),('K2',0.241,103.7),
       ('NU2',0.101,52.9),('K1',0.080,49.2),('O1',0.061,15.0),
       ('M4',0.110,200.0),('MS4',0.070,221.0),('M6',0.048,258.0),('MK3',0.012,178.0)]
print(f"""  "PAIMBOEUF":{{
    name:"Paimboeuf (Estuaire Loire)", region:"Loire-Atlantique (44)", Z0:{round(3.200+DZ0,3)}, M2_A:{round(2.530*DA_M2,3)},
    info:{{ "Lat/Lon":"47\u00b017'N 2\u00b001'O", "Marnage VE":"~5.3 m", "Marnage ME":"~2.1 m", "Estuaire Loire":"-" }},
    cst:[
      // Estuaire : effets eaux peu profondes importants (M4, M6 amplifies)
      {{{','.join('{n:"%s",A:%s,G:%s}'%(n,corr_a(n,a),corr_g(n,g)) for n,a,g in cst[:4])}}},
      {{{','.join('{n:"%s",A:%s,G:%s}'%(n,corr_a(n,a),corr_g(n,g)) for n,a,g in cst[4:8])}}},
      {{{','.join('{n:"%s",A:%s,G:%s}'%(n,corr_a(n,a),corr_g(n,g)) for n,a,g in cst[8:])}}},
    ]
  }},""")

# ── SAINT-GILDAS ──────────────────────────────────────────────────────────
cst = [('M2',2.370,67.6),('S2',0.808,96.3),('N2',0.493,46.6),('K2',0.225,97.2),
       ('NU2',0.094,46.6),('K1',0.075,43.9),('O1',0.058,10.0),
       ('M4',0.083,186.0),('MS4',0.053,207.0)]
print(f"""  "SAINT-GILDAS":{{
    name:"Saint-Gildas (Pointe)", region:"Loire-Atlantique (44)", Z0:{round(2.980+DZ0,3)}, M2_A:{round(2.370*DA_M2,3)},
    info:{{ "Lat/Lon":"47\u00b005'N 2\u00b014'O", "Marnage VE":"~4.9 m", "Marnage ME":"~1.9 m", "Niveau moyen":"2.98 m" }},
    cst:[
      {{{','.join('{n:"%s",A:%s,G:%s}'%(n,corr_a(n,a),corr_g(n,g)) for n,a,g in cst[:4])}}},
      {{{','.join('{n:"%s",A:%s,G:%s}'%(n,corr_a(n,a),corr_g(n,g)) for n,a,g in cst[4:])}}},
    ]
  }},""")

# ── BREST (calibrated from full optimization, RMSE 2.7cm) ─────────────────
print("""  "BREST":{
    name:"Brest", region:"Finistere (29)", Z0:4.030, M2_A:2.210,
    info:{ "Lat/Lon":"48\u00b023'N 4\u00b030'O", "Marnage VE":"~6.5 m", "Marnage ME":"~2.5 m", "Port de reference SHOM":"-" },
    cst:[
      // Recalibre SHOM maree.info avril 2026 (RMSE 2.7cm)
      {n:"M2",A:2.210,G:90.2},{n:"S2",A:0.800,G:128.4},{n:"N2",A:0.470,G:82.6},{n:"K2",A:0.220,G:135.2},
      {n:"K1",A:0.047,G:30.7},{n:"O1",A:0.105,G:305.4},{n:"P1",A:0.024,G:29.9},{n:"Q1",A:0.011,G:282.8},
      {n:"M4",A:0.065,G:200.8},{n:"MS4",A:0.039,G:226.4},
    ]
  },""")
