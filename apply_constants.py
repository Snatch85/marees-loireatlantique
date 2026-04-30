#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Apply calibrated Saint-Nazaire constants to all HTML/JS files.
Run this after calibrate_v2.py produces final parameters.

Usage: python apply_constants.py
Edit the PARAMS dict below with the calibrated values first.
"""
import os, re, glob

# ── INSERT CALIBRATED VALUES HERE ─────────────────────────────────
PARAMS = {
    'Z0':   3.585,    # calibré vs SHOM maree.info avril 2026
    'Am':   1.8147,   # M2 amplitude
    'Gm':   104.657,  # M2 phase (G)
    'As':   0.7627,   # S2 amplitude
    'Gs':   119.488,  # S2 phase
    'An':   0.3211,   # N2 amplitude
    'Gn':   110.417,  # N2 phase
    'Ak2':  0.0141,   # K2 amplitude
    'Gk2':  45.601,   # K2 phase
    'Ak1':  0.0088,   # K1 amplitude
    'Gk1':  -47.762,  # K1 phase
    'Ao1':  0.1310,   # O1 amplitude
    'Go1':  -29.155,  # O1 phase
    'Am4':  0.2992,   # M4 amplitude
    'Gm4':  57.490,   # M4 phase
    'Ams4': 0.1463,   # MS4 amplitude
    'Gms4': 130.518,  # MS4 phase
}

def check_params():
    missing = [k for k, v in PARAMS.items() if v is None]
    if missing:
        print(f"ERROR: Missing parameters: {missing}")
        print("Edit PARAMS dict in this file with calibrated values.")
        return False
    return True

def derived(p):
    """Compute derived constituent values."""
    return {
        # NU2: coupled to N2 (ratio 0.100/0.519, phase +20°)
        'Anu2': p['An'] * 0.100 / 0.519,
        'Gnu2': p['Gn'] + 20.0,
        # MU2: coupled to M2 (fixed amp, phase = Gm+2)
        'Amu2': 0.024,
        'Gmu2': p['Gm'] + 2.0,
        # P1: coupled to K1 (fixed amp, phase = Gk1-15)
        'Ap1':  0.024,
        'Gp1':  p['Gk1'] - 15.0,
        # Q1: coupled to O1 (fixed amp, phase = Go1)
        'Aq1':  0.013,
        'Gq1':  p['Go1'],
    }

def update_html_cst(content, p, d):
    """Replace Saint-Nazaire cst block in HTML files (G-convention)."""
    # Match the Z0/M2_A header line
    old_header = r'Z0:3\.308, M2_A:1\.563,'
    new_header = f'Z0:{p["Z0"]:.3f}, M2_A:{p["Am"]:.4f},'
    content = re.sub(old_header, new_header, content)

    # Replace the 3-line cst block (identical across all HTML files)
    old_cst = (
        r'\{n:"M2", A:1\.563, G:93\.2\}, \{n:"S2", A:0\.662, G:128\.7\}, \{n:"N2", A:0\.563, G:85\.8\},\n'
        r'      \{n:"K2", A:0\.194, G:134\.2\},\{n:"NU2",A:0\.100, G:85\.7\},  \{n:"MU2",A:0\.024, G:88\.1\},\n'
        r'      \{n:"L2", A:0\.030, G:116\.0\},\{n:"T2", A:0\.022, G:98\.5\},  \{n:"p2N2",A:0\.070,G:102\.4\},\n'
        r'      \{n:"K1", A:0\.072, G:38\.6\}, \{n:"O1", A:0\.108, G:309\.4\}, \{n:"P1", A:0\.024, G:29\.4\},\n'
        r'      \{n:"Q1", A:0\.013, G:278\.3\},\{n:"M4", A:0\.091, G:237\.3\}, \{n:"MN4",A:0\.022, G:223\.0\},\n'
        r'      \{n:"MS4",A:0\.060, G:264\.7\},\{n:"M6", A:0\.028, G:316\.7\}, \{n:"MK3",A:0\.008, G:179\.8\},'
    )
    new_cst = (
        f'{{n:"M2",  A:{p["Am"]:.4f}, G:{p["Gm"]:.2f}}}, {{n:"S2",  A:{p["As"]:.4f}, G:{p["Gs"]:.2f}}}, {{n:"N2",  A:{p["An"]:.4f}, G:{p["Gn"]:.2f}}},\n'
        f'      {{n:"K2",  A:{p["Ak2"]:.4f}, G:{p["Gk2"]:.2f}}},{{n:"NU2", A:{d["Anu2"]:.4f}, G:{d["Gnu2"]:.2f}}}, {{n:"MU2", A:{d["Amu2"]:.4f}, G:{d["Gmu2"]:.2f}}},\n'
        f'      {{n:"L2",  A:0.0300, G:116.0}},{{n:"T2",  A:0.0220, G:98.5}},   {{n:"p2N2",A:0.0700,G:102.4}},\n'
        f'      {{n:"K1",  A:{p["Ak1"]:.4f}, G:{p["Gk1"]:.2f}}}, {{n:"O1",  A:{p["Ao1"]:.4f}, G:{p["Go1"]:.2f}}}, {{n:"P1",  A:{d["Ap1"]:.4f}, G:{d["Gp1"]:.2f}}},\n'
        f'      {{n:"Q1",  A:{d["Aq1"]:.4f}, G:{d["Gq1"]:.2f}}},{{n:"M4",  A:{p["Am4"]:.4f}, G:{p["Gm4"]:.2f}}}, {{n:"MN4", A:0.0220, G:223.0}},\n'
        f'      {{n:"MS4", A:{p["Ams4"]:.4f}, G:{p["Gms4"]:.2f}}},{{n:"M6",  A:0.0280, G:316.7}}, {{n:"MK3", A:0.0080, G:179.8}},'
    )
    content, n = re.subn(old_cst, new_cst, content)
    return content, n

def update_tide_calculator_js(content, p, d):
    """Replace SAINT_NAZAIRE block in tide-calculator.js (K-convention)."""
    old_block = (
        r"SAINT_NAZAIRE: \{ nom: 'Saint-Nazaire', Z0: 3\.308, cst: \{\n"
        r"    M2:    \{ A: 1\.563, K:  93\.2 \},  S2:    \{ A: 0\.662, K: 128\.7 \},\n"
        r"    N2:    \{ A: 0\.563, K:  85\.8 \},  K2:    \{ A: 0\.194, K: 134\.2 \},\n"
        r"    K1:    \{ A: 0\.072, K:  38\.6 \},  O1:    \{ A: 0\.108, K: 309\.4 \},\n"
        r"    P1:    \{ A: 0\.024, K:  29\.4 \},  Q1:    \{ A: 0\.013, K: 278\.3 \},\n"
        r"    M4:    \{ A: 0\.091, K: 237\.3 \},  MS4:   \{ A: 0\.060, K: 264\.7 \},\n"
        r"    MN4:   \{ A: 0\.022, K: 223\.0 \},  '2N2': \{ A: 0\.070, K: 102\.4 \},\n"
        r"    NU2:   \{ A: 0\.100, K:  85\.7 \},  MU2:   \{ A: 0\.024, K:  88\.1 \},\n"
        r"    M6:    \{ A: 0\.028, K: 316\.7 \},\n"
        r"  \}\}"
    )
    new_block = (
        f"SAINT_NAZAIRE: {{ nom: 'Saint-Nazaire', Z0: {p['Z0']:.3f}, cst: {{\n"
        f"    M2:    {{ A: {p['Am']:.4f}, K: {p['Gm']:.2f} }},  S2:    {{ A: {p['As']:.4f}, K: {p['Gs']:.2f} }},\n"
        f"    N2:    {{ A: {p['An']:.4f}, K: {p['Gn']:.2f} }},  K2:    {{ A: {p['Ak2']:.4f}, K: {p['Gk2']:.2f} }},\n"
        f"    K1:    {{ A: {p['Ak1']:.4f}, K: {p['Gk1']:.2f} }},  O1:    {{ A: {p['Ao1']:.4f}, K: {p['Go1']:.2f} }},\n"
        f"    P1:    {{ A: {d['Ap1']:.4f}, K: {d['Gp1']:.2f} }},  Q1:    {{ A: {d['Aq1']:.4f}, K: {d['Gq1']:.2f} }},\n"
        f"    M4:    {{ A: {p['Am4']:.4f}, K: {p['Gm4']:.2f} }},  MS4:   {{ A: {p['Ams4']:.4f}, K: {p['Gms4']:.2f} }},\n"
        f"    MN4:   {{ A: 0.0220, K: 223.0 }},  '2N2': {{ A: 0.0700, K: 102.4 }},\n"
        f"    NU2:   {{ A: {d['Anu2']:.4f}, K: {d['Gnu2']:.2f} }},  MU2:   {{ A: {d['Amu2']:.4f}, K: {d['Gmu2']:.2f} }},\n"
        f"    M6:    {{ A: 0.0280, K: 316.7 }},\n"
        f"  }}}}"
    )
    content, n = re.subn(old_block, new_block, content)
    return content, n

def process_file(path, p, d, is_js=False):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    if is_js:
        new_content, n = update_tide_calculator_js(content, p, d)
    else:
        new_content, n = update_html_cst(content, p, d)

    if new_content != content:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True, n
    return False, 0

def main():
    if not check_params():
        return

    p = PARAMS
    d = derived(p)

    root = os.path.dirname(os.path.abspath(__file__))

    # Collect HTML files to update (exclude android/ to avoid touching app build)
    html_patterns = [
        'index.html',
        'marees-*/index.html',
        'marees/*/index.html',
        'peche-a-pied/index.html',
        'marees-france/index.html',
        'www/index.html',
        'www/marees-*/index.html',
        'www/marees/*/index.html',
        'www/peche-a-pied/index.html',
        'www/marees-france/index.html',
    ]

    js_files = [
        'assets/tide-calculator.js',
        'www/assets/tide-calculator.js',
    ]

    print(f"\nApplying Saint-Nazaire constants:")
    print(f"  Z0={p['Z0']:.3f}  M2: A={p['Am']:.4f} G={p['Gm']:.2f}")
    print(f"  S2: A={p['As']:.4f} G={p['Gs']:.2f}  N2: A={p['An']:.4f} G={p['Gn']:.2f}")
    print(f"  K2: A={p['Ak2']:.4f} G={p['Gk2']:.2f}  K1: A={p['Ak1']:.4f} G={p['Gk1']:.2f}")
    print(f"  O1: A={p['Ao1']:.4f} G={p['Go1']:.2f}  M4: A={p['Am4']:.4f} G={p['Gm4']:.2f}")
    print(f"  MS4: A={p['Ams4']:.4f} G={p['Gms4']:.2f}")
    print()

    updated = 0
    skipped = 0

    # Process HTML files
    for pattern in html_patterns:
        full_pattern = os.path.join(root, pattern)
        files = glob.glob(full_pattern)
        for fpath in files:
            changed, n = process_file(fpath, p, d, is_js=False)
            rel = os.path.relpath(fpath, root)
            if changed:
                print(f"  [OK] {rel}  ({n} replacement(s))")
                updated += 1
            else:
                print(f"  [--] {rel}  (no match / already updated)")
                skipped += 1

    # Process JS files
    for js_rel in js_files:
        fpath = os.path.join(root, js_rel)
        if not os.path.exists(fpath):
            print(f"  [!!] {js_rel}  NOT FOUND")
            continue
        changed, n = process_file(fpath, p, d, is_js=True)
        if changed:
            print(f"  [OK] {js_rel}  ({n} replacement(s))")
            updated += 1
        else:
            print(f"  [--] {js_rel}  (no match / already updated)")
            skipped += 1

    print(f"\nDone: {updated} files updated, {skipped} unchanged.")

if __name__ == '__main__':
    main()
