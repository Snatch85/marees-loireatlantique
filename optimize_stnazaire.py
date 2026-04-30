#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Optimisation des constantes harmoniques pour Saint-Nazaire
en calant sur les donnees SHOM de maree.info/117 (avril 2026).
"""
import math, calendar, sys

DEG = math.pi / 180
RAD = 180 / math.pi
mod360 = lambda x: ((x % 360) + 360) % 360

SPEEDS = {
    'M2': 28.9841042, 'S2': 30.0000000, 'N2': 28.4397295,
    'K2': 30.0821373, 'K1': 15.0410686, 'O1': 13.9430356,
    'NU2': 28.5125831, 'MU2': 27.9682084,
    'M4': 57.9682084,  'MS4': 58.9841042, 'MN4': 57.4238337,
    'M6': 86.9523126,
}

J2000_MS = 946728000000  # Date.UTC(2000,0,1,12,0,0)

def date_to_ms(date_str):
    y, m, d = int(date_str[:4]), int(date_str[5:7]), int(date_str[8:10])
    return calendar.timegm((y, m, d, 0, 0, 0, 0, 0, 0)) * 1000

def days_from_j2000(ms):
    return (ms - J2000_MS) / 86400000.0

def astro_args(ms_midnight):
    d = days_from_j2000(ms_midnight)
    return {
        's': mod360(218.3164477 + 13.17639648 * d),
        'h': mod360(280.4664567 +  0.98564736 * d),
        'p': mod360( 83.3532465 +  0.11140353 * d),
        'N': mod360(125.0445479 -  0.05295378 * d),
    }

def nodal_factors(N_deg):
    N  = N_deg * DEG
    cN, sN   = math.cos(N),   math.sin(N)
    c2N, s2N = math.cos(2*N), math.sin(2*N)
    reM2 = 1 - 0.03731*cN + 0.00052*c2N
    imM2 =   - 0.03731*sN + 0.00052*s2N
    fM2  = math.hypot(reM2, imM2);  uM2 = math.atan2(imM2, reM2) * RAD
    reO1 = 1 - 0.18890*cN + 0.00587*c2N
    imO1 =     0.18890*sN  - 0.00587*s2N
    fO1  = math.hypot(reO1, imO1);  uO1 = math.atan2(imO1, reO1) * RAD
    reK1 = 1 + 0.11583*cN - 0.00292*c2N
    imK1 =   - 0.11583*sN  + 0.00292*s2N
    fK1  = math.hypot(reK1, imK1);  uK1 = math.atan2(imK1, reK1) * RAD
    reK2 = 1 + 0.28519*cN + 0.03240*c2N
    imK2 =   - 0.28519*sN  - 0.03240*s2N
    fK2  = math.hypot(reK2, imK2);  uK2 = math.atan2(imK2, reK2) * RAD
    return {
        'M2': (fM2,uM2), 'S2': (1.0,0.0), 'N2': (fM2,uM2), 'K2': (fK2,uK2),
        'K1': (fK1,uK1), 'O1': (fO1,uO1), 'NU2':(fM2,uM2), 'MU2':(fM2,uM2),
        'M4': (fM2**2,2*uM2), 'MS4':(fM2,uM2), 'MN4':(fM2**2,2*uM2),
        'M6': (fM2**3,3*uM2),
    }

def equil_args(astro):
    s, h, p = astro['s'], astro['h'], astro['p']
    r = mod360
    return {
        'M2':  r(2*h - 2*s),    'S2':  0,
        'N2':  r(2*h - 3*s + p),'K2':  r(2*h),
        'K1':  r(h + 90),       'O1':  r(h - 2*s - 90),
        'NU2': r(2*h - 3*s + p),'MU2': r(4*h - 4*s),
        'M4':  r(4*h - 4*s),    'MS4': r(2*h - 2*s),
        'MN4': r(4*h - 5*s + p),'M6':  r(6*h - 6*s),
    }

def height_at(p, ms_midnight, t_hrs):
    astro = astro_args(ms_midnight)
    V0 = equil_args(astro)
    nod = nodal_factors(astro['N'])
    h = p['Z0']
    # Main 6 constituents (optimised)
    main_cst = {
        'M2':(p['Am'],p['Km']), 'S2':(p['As'],p['Ks']),
        'N2':(p['An'],p['Kn']), 'K2':(p['Ak2'],p['Kk2']),
        'K1':(p['Ak1'],p['Kk1']), 'O1':(p['Ao1'],p['Ko1']),
    }
    # Minor constituents held fixed (corrected K = original + Brest offset)
    minor_cst = {
        'NU2':(0.100, 85.7), 'MU2':(0.024, 71.8),
        'M4': (0.091,191.5), 'MS4':(0.060,212.3),
        'MN4':(0.022,163.4), 'M6': (0.028,248.0),
    }
    all_cst = {**main_cst, **minor_cst}
    for name, (A, K) in all_cst.items():
        spd = SPEEDS.get(name)
        if not spd:
            continue
        f, u = nod.get(name, (1.0, 0.0))
        phi  = V0.get(name, 0)
        h   += f * A * math.cos((phi + u + spd * t_hrs - K) * DEG)
    return h

# ── Reference data from maree.info/117 (CEST = UTC+2 in April) ───────
# Format: (date_str_midnight_UTC, t_utc_hours, type, height_m)
SN_REF = [
    # April 22 -- coeff 65-73
    ("2026-04-22",  1.167, "BM", 1.25),   # 03:10 CEST
    ("2026-04-22",  6.483, "PM", 5.18),   # 08:29 CEST
    ("2026-04-22", 13.500, "BM", 1.65),   # 15:30 CEST
    ("2026-04-22", 18.700, "PM", 5.21),   # 20:42 CEST
    # April 23 -- coeff 51-58
    ("2026-04-23",  2.150, "BM", 1.64),   # 04:09 CEST
    ("2026-04-23",  7.417, "PM", 4.71),   # 09:25 CEST
    ("2026-04-23", 14.550, "BM", 2.03),   # 16:33 CEST
    ("2026-04-23", 19.750, "PM", 4.81),   # 21:45 CEST
    # April 27 -- coeff 56-61
    ("2026-04-27",  1.167, "PM", 5.09),   # 03:10 CEST
    ("2026-04-27",  6.933, "BM", 1.76),   # 08:56 CEST
    ("2026-04-27", 13.533, "PM", 5.08),   # 15:32 CEST
    # April 28 -- coeff 66-71
    ("2026-04-28",  1.733, "PM", 5.24),   # 03:44 CEST
    ("2026-04-28",  7.817, "BM", 1.52),   # 09:49 CEST
    ("2026-04-28", 13.917, "PM", 5.25),   # 15:55 CEST
    # April 29 -- coeff 74-78
    ("2026-04-29",  2.400, "PM", 5.38),   # 04:24 CEST
    ("2026-04-29",  8.450, "BM", 1.33),   # 10:27 CEST
    ("2026-04-29", 14.650, "PM", 5.31),   # 16:39 CEST
    # April 30 -- coeff 80-83
    ("2026-04-30",  2.783, "PM", 5.47),   # 04:47 CEST
    ("2026-04-30",  9.133, "BM", 1.21),   # 11:08 CEST
    ("2026-04-30", 14.967, "PM", 5.44),   # 16:58 CEST
]

def rmse(p):
    sq = []
    for (d, t, typ, h_ref) in SN_REF:
        ms = date_to_ms(d)
        sq.append((height_at(p, ms, t) - h_ref)**2)
    return math.sqrt(sum(sq)/len(sq))

def gradient_descent(p0, step=1e-3, lr=0.05, n_iter=3000, fixed_keys=None, bounds=None):
    fixed = set(fixed_keys or [])
    bounds = bounds or {}
    p = dict(p0)
    best = dict(p0)
    best_err = rmse(p)
    for it in range(n_iter):
        for key in list(p.keys()):
            if key in fixed:
                continue
            pp = dict(p); pp[key] += step
            pm = dict(p); pm[key] -= step
            g = (rmse(pp) - rmse(pm)) / (2*step)
            p[key] -= lr * g
            if key.startswith('A'):
                p[key] = max(0.001, p[key])
            if key in bounds:
                lo, hi = bounds[key]
                p[key] = max(lo, min(hi, p[key]))
        err = rmse(p)
        if err < best_err:
            best_err = err
            best = dict(p)
        if it % 500 == 0:
            print("  iter %4d: RMSE=%.4fm  Z0=%.3f Km=%.1f Ks=%.1f Am=%.3f As=%.3f" % (
                it, err, p['Z0'], p['Km'], p['Ks'], p['Am'], p['As']))
    return best, best_err

# ── Initial params: Brest offsets applied to Saint-Nazaire original values ──
# G_M2: 70.3 + 22.6 = 92.9  G_S2: 99.2 + 29.5 = 128.7
# G_N2: 49.1 + 36.6 = 85.7  G_K2: 99.8 + 34.4 = 134.2
# G_K1: 53.7 - 15.1 = 38.6  G_O1: 16.6 + 292.7 = 309.3
p0 = {
    'Z0': 3.147,
    'Km': 92.9,  'Ks': 128.7, 'Kn': 85.7, 'Kk2': 134.2, 'Kk1': 38.6, 'Ko1': 309.3,
    'Am': 2.497, 'As': 0.851, 'An': 0.519, 'Ak2': 0.238, 'Ak1': 0.101, 'Ao1': 0.072,
}

print("Initial RMSE (Brest corrections applied): %.4fm" % rmse(p0))
print()

# ── Approach B: full optimisation, A_M2 bounded ≥ 2.0m ──
print("=== Approach B: full optimisation (Am bounded >= 2.0m) ===")
BOUNDS_B = {'Am': (2.0, 3.5), 'As': (0.3, 1.5), 'An': (0.1, 1.0)}
pB, errB = gradient_descent(p0, step=1e-3, lr=0.05, n_iter=3000, bounds=BOUNDS_B)
pB, errB = gradient_descent(pB, step=1e-4, lr=0.01, n_iter=3000, bounds=BOUNDS_B)
print("Approach B RMSE = %.4fm  Z0=%.3f  Am=%.3f" % (errB, pB['Z0'], pB['Am']))

# ── Approach C: full optimisation, no bounds ──
print("\n=== Approach C: full optimisation (no amplitude bounds) ===")
pC, errC = gradient_descent(p0, step=1e-3, lr=0.05, n_iter=3000)
pC, errC = gradient_descent(pC, step=1e-4, lr=0.01, n_iter=2000)
print("Approach C RMSE = %.4fm  Z0=%.3f  Am=%.3f" % (errC, pC['Z0'], pC['Am']))

# Choose approach with lowest RMSE
if errB <= errC:
    best, best_err, approach = pB, errB, "B (bounded Am >= 2.0)"
else:
    best, best_err, approach = pC, errC, "C (unbounded)"
print("\nBest approach: %s" % approach)

print("""
=== FINAL RESULTS - Saint-Nazaire ===
Z0   = %.3fm  (was: 3.147m)
K_M2 = %.1f   (was: 70.3)
K_S2 = %.1f   (was: 99.2)
K_N2 = %.1f   (was: 49.1)
K_K2 = %.1f   (was: 99.8)
K_K1 = %.1f   (was: 53.7)
K_O1 = %.1f   (was: 16.6)
A_M2 = %.3fm  (was: 2.497m)
A_S2 = %.3fm  (was: 0.851m)
A_N2 = %.3fm  (was: 0.519m)
A_K2 = %.3fm  (was: 0.238m)
A_K1 = %.3fm  (was: 0.101m)
A_O1 = %.3fm  (was: 0.072m)
RMSE = %.4fm = %.1fcm
""" % (best['Z0'],best['Km'],best['Ks'],best['Kn'],best['Kk2'],best['Kk1'],best['Ko1'],
       best['Am'],best['As'],best['An'],best['Ak2'],best['Ak1'],best['Ao1'],best_err,best_err*100))

print("=== Point-by-point verification ===")
for (d, t, typ, h_ref) in SN_REF:
    ms = date_to_ms(d)
    h_pred = height_at(best, ms, t)
    err_h = h_pred - h_ref
    flag = "OK" if abs(err_h) < 0.10 else "~~"
    sign = "+" if err_h >= 0 else ""
    print("[%s] %s %s ref=%.2fm pred=%.2fm err=%s%.2fm (UTC %.2fh)" % (
        flag, d, typ, h_ref, h_pred, sign, err_h, t))
print("Global RMSE:", round(rmse(best)*100, 1), "cm")
