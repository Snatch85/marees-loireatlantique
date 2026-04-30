#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Calibration Saint-Nazaire - methode correcte:
- Amplitudes fixees (SHOM-like)
- Optimise G_M2, G_S2, G_N2, G_K2, G_K1, G_O1, G_M4, G_MS4, Z0
- Minimise les erreurs de TEMPS et HAUTEUR des extrema SHOM
"""
import math, calendar, sys
import numpy as np
from scipy.optimize import minimize, differential_evolution

DEG = math.pi/180; RAD = 180/math.pi
mod360 = lambda x: ((x%360)+360)%360
J2000_MS = 946728000000

SPEEDS = {
    'M2':28.9841042,'S2':30.0,'N2':28.4397295,'K2':30.0821373,
    'K1':15.0410686,'O1':13.9430356,'NU2':28.5125831,'MU2':27.9682084,
    'M4':57.9682084,'MS4':58.9841042,'MN4':57.4238337,
    'P1':14.9589314,'Q1':13.3986609,
}

def ms0_of(s):
    y,m,d=int(s[:4]),int(s[5:7]),int(s[8:10])
    return calendar.timegm((y,m,d,0,0,0,0,0,0))*1000

def astro(ms):
    d=(ms-J2000_MS)/86400000.0
    return {
        's':mod360(218.3164477+13.17639648*d),
        'h':mod360(280.4664567+0.98564736*d),
        'p':mod360(83.3532465+0.11140353*d),
        'N':mod360(125.0445479-0.05295378*d)
    }

def nodal(N_deg):
    N=N_deg*DEG; c=math.cos; s=math.sin
    fM2=1-0.03731*c(N)+0.00052*c(2*N)
    uM2=math.atan2(-0.03731*s(N)+0.00052*s(2*N),fM2)*RAD
    fO1=1-0.18890*c(N)+0.00587*c(2*N)
    uO1=math.atan2(0.18890*s(N)-0.00587*s(2*N),fO1)*RAD
    fK1=1+0.11583*c(N)-0.00292*c(2*N)
    uK1=math.atan2(-0.11583*s(N)+0.00292*s(2*N),fK1)*RAD
    fK2=1+0.28519*c(N)+0.03240*c(2*N)
    uK2=math.atan2(-0.28519*s(N)-0.03240*s(2*N),fK2)*RAD
    return {
        'M2':(fM2,uM2),'S2':(1,0),'N2':(fM2,uM2),'K2':(fK2,uK2),
        'K1':(fK1,uK1),'O1':(fO1,uO1),'NU2':(fM2,uM2),'MU2':(fM2,uM2),
        'M4':(fM2**2,2*uM2),'MS4':(fM2,uM2),'MN4':(fM2**2,2*uM2),
        'P1':(1,0),'Q1':(fO1,uO1)
    }

def equil(a):
    s,h,p=a['s'],a['h'],a['p']; r=mod360
    return {
        'M2':r(2*h-2*s),'S2':0,'N2':r(2*h-3*s+p),'K2':r(2*h),
        'K1':r(h+90),'O1':r(h-2*s-90),'NU2':r(2*h-3*s+p),'MU2':r(4*h-4*s),
        'M4':r(4*h-4*s),'MS4':r(2*h-2*s),'MN4':r(4*h-5*s+p),
        'P1':r(-h+270),'Q1':r(h-3*s+p-90)
    }

# SHOM reference extrema: maree.info April 22-30 2026 (CEST -> UTC: subtract 2h)
REF = [
    # Apr 22 (coeff 65-73)
    ('2026-04-22', 1.167,'BM',1.25), ('2026-04-22', 6.483,'PM',5.18),
    ('2026-04-22',13.500,'BM',1.65), ('2026-04-22',18.700,'PM',5.21),
    # Apr 23 (coeff 51-58)
    ('2026-04-23', 2.150,'BM',1.64), ('2026-04-23', 7.417,'PM',4.71),
    ('2026-04-23',14.550,'BM',2.03), ('2026-04-23',19.750,'PM',4.81),
    # Apr 24 (neap, coeff ~44-47)
    ('2026-04-24', 3.283,'BM',1.95), ('2026-04-24',10.717,'PM',4.58),
    ('2026-04-24',15.750,'BM',2.27), ('2026-04-24',23.150,'PM',4.77),
    # Apr 25 (coeff ~46-49)
    ('2026-04-25', 4.533,'BM',2.08), ('2026-04-25',11.933,'PM',4.71),
    ('2026-04-25',17.017,'BM',2.27),
    # Apr 26 (coeff ~50-54)
    ('2026-04-26', 0.300,'PM',4.92), ('2026-04-26', 5.817,'BM',1.99),
    ('2026-04-26',12.883,'PM',4.90), ('2026-04-26',18.217,'BM',2.07),
    # Apr 27 (coeff 56-61)
    ('2026-04-27', 1.167,'PM',5.09), ('2026-04-27', 6.933,'BM',1.76),
    ('2026-04-27',13.533,'PM',5.08), ('2026-04-27',19.250,'BM',1.79),
    # Apr 28 (coeff 66-71)
    ('2026-04-28', 1.733,'PM',5.24), ('2026-04-28', 7.817,'BM',1.52),
    ('2026-04-28',13.917,'PM',5.25), ('2026-04-28',20.100,'BM',1.54),
    # Apr 29 (coeff 74-78)
    ('2026-04-29', 2.400,'PM',5.38), ('2026-04-29', 8.450,'BM',1.33),
    ('2026-04-29',14.650,'PM',5.31),
    # Apr 30 (coeff 80-83)
    ('2026-04-30', 2.783,'PM',5.47), ('2026-04-30', 9.133,'BM',1.21),
    ('2026-04-30',14.967,'PM',5.44),
]
print(f'{len(REF)} reference points (Apr 22-30 2026)')

_cache = {}
def get_env(ds):
    if ds not in _cache:
        a=astro(ms0_of(ds)); _cache[ds]=(equil(a),nodal(a['N']))
    return _cache[ds]

# Fixed amplitudes - SHOM-like (from published data and tidal analysis)
# A_M2 estimated from marnage: VE~6.1m (coeff100), ME~2.6m (coeff44)
# (A_M2+A_S2) ~ 3.05m, (A_M2-A_S2) ~ 1.31m -> A_M2~2.18, A_S2~0.87
# Use original values which are close to published SHOM
FIXED_A = {
    'M2': 2.180, 'S2': 0.870, 'N2': 0.460, 'K2': 0.230,
    'K1': 0.100, 'O1': 0.070,
    'M4': 0.095, 'MS4': 0.055, 'MN4': 0.020,
    'NU2': 0.100, 'MU2': 0.024, 'P1': 0.024, 'Q1': 0.013,
}

# G_N2 ~ G_M2 - 21 (typical offset), G_K2 ~ G_S2 + 4, G_K1 ~ 54, G_O1 ~ 17
# G_MN4 ~ G_M4 + G_N2 - G_M2 (combination)
# G_NU2 ~ G_N2 + 16, G_MU2 ~ G_M2 + 2

def make_terms(Gm, Gs, Gm4, Gms4, Z0, ds):
    """Build tide model terms with free G_M2, G_S2, G_M4, G_MS4."""
    V0,nod = get_env(ds)
    # Dependent G values
    Gn  = Gm - 21.0   # N2 ≈ M2 - 21deg
    Gk2 = Gs + 4.0    # K2 ≈ S2 + 4deg
    Gk1 = 54.0        # fixed
    Go1 = 17.0        # fixed
    Gmn4 = mod360(Gm4 + Gn - Gm)   # MN4 combination
    Gnu2 = Gn + 16.0
    Gmu2 = Gm + 2.0
    Gp1  = Gk1 - 15.0

    cst = [
        ('M2',  FIXED_A['M2'],  Gm),
        ('S2',  FIXED_A['S2'],  Gs),
        ('N2',  FIXED_A['N2'],  Gn),
        ('K2',  FIXED_A['K2'],  Gk2),
        ('K1',  FIXED_A['K1'],  Gk1),
        ('O1',  FIXED_A['O1'],  Go1),
        ('M4',  FIXED_A['M4'],  Gm4),
        ('MS4', FIXED_A['MS4'], Gms4),
        ('MN4', FIXED_A['MN4'], Gmn4),
        ('NU2', FIXED_A['NU2'], Gnu2),
        ('MU2', FIXED_A['MU2'], Gmu2),
        ('P1',  FIXED_A['P1'],  Gp1),
        ('Q1',  FIXED_A['Q1'],  Go1),
    ]
    terms = []
    for (n,A,G) in cst:
        spd = SPEEDS.get(n,0)
        if not spd: continue
        f,u = nod.get(n,(1,0)); phi = V0.get(n,0)
        terms.append((f*A, spd*DEG, (phi+u-G)*DEG))
    return Z0, terms

def find_ext_fine(terms, Z0, t_ref, typ, window=3.0, step=1/120):
    """Find extremum with 0.5-min resolution."""
    def h(t): return Z0+sum(fA*math.cos(spd*t+off) for fA,spd,off in terms)
    best_t=t_ref; best_h=h(t_ref)
    n = int(2*window/step)+1
    for i in range(n):
        tt=t_ref-window+i*step; hv=h(tt)
        if typ=='PM' and hv>best_h: best_h=hv; best_t=tt
        if typ=='BM' and hv<best_h: best_h=hv; best_t=tt
    return best_t, best_h

def cost_fn(params):
    Gm, Gs, Gm4, Gms4, Z0 = params
    sq_t=0; sq_h=0; n=0
    prev_ds=None; terms_c=None; Z0_c=None
    for (ds,t_ref,typ,h_ref) in REF:
        if ds!=prev_ds:
            Z0_c,terms_c=make_terms(Gm,Gs,Gm4,Gms4,Z0,ds); prev_ds=ds
        # Coarse search +-3h step 15min
        def h(t,T=terms_c,Z=Z0_c): return Z+sum(fA*math.cos(spd*t+off) for fA,spd,off in T)
        best_t=t_ref; best_h=h(t_ref)
        for i in range(-12,13):
            tt=t_ref+i*0.25; hv=h(tt)
            if typ=='PM' and hv>best_h: best_h=hv; best_t=tt
            if typ=='BM' and hv<best_h: best_h=hv; best_t=tt
        # Fine search +-20min around coarse best
        for i in range(-24,25):
            tt=best_t+i/120; hv=h(tt)
            if typ=='PM' and hv>best_h: best_h=hv; best_t=tt
            if typ=='BM' and hv<best_h: best_h=hv; best_t=tt
        dt_min=(best_t-t_ref)*60; dh=best_h-h_ref
        # Normalize: target 5min and 5cm equally weighted
        sq_t+=(dt_min/5)**2; sq_h+=(dh/0.05)**2; n+=1
    return math.sqrt((sq_t+sq_h)/n)

def metrics(params):
    Gm, Gs, Gm4, Gms4, Z0 = params
    sq_t=0; sq_h=0; n=0
    prev_ds=None; terms_c=None; Z0_c=None
    for (ds,t_ref,typ,h_ref) in REF:
        if ds!=prev_ds:
            Z0_c,terms_c=make_terms(Gm,Gs,Gm4,Gms4,Z0,ds); prev_ds=ds
        best_t,best_h=find_ext_fine(terms_c,Z0_c,t_ref,typ)
        sq_t+=(best_t-t_ref)**2*3600; sq_h+=(best_h-h_ref)**2; n+=1
    return math.sqrt(sq_t/n), math.sqrt(sq_h/n)

# Initial guess: original G values
x0 = np.array([70.3, 99.2, 191.5, 212.3, 3.147])

et0,eh0=metrics(x0)
print(f'Initial: t-RMSE={et0/60:.1f}min  h-RMSE={eh0:.3f}m')
print()

# Use differential evolution for global search (avoids local minima)
bounds_de = [
    (60, 110),   # G_M2
    (90, 140),   # G_S2
    (80, 240),   # G_M4
    (100, 280),  # G_MS4
    (2.8, 3.6),  # Z0
]

call=[0]
def cb(xk, convergence):
    call[0]+=1
    if call[0]%10==0:
        et,eh=metrics(xk)
        print(f'  DE iter {call[0]:3d}: t={et/60:.1f}min h={eh:.3f}m  Gm={xk[0]:.1f} Gm4={xk[2]:.1f} Z0={xk[4]:.3f}')
        sys.stdout.flush()

print('=== Global search (Differential Evolution) ===')
res_de = differential_evolution(
    cost_fn, bounds_de,
    maxiter=200, popsize=15, tol=0.001,
    mutation=(0.5,1.5), recombination=0.9,
    seed=42, callback=cb, polish=True, workers=1
)
xb = res_de.x
print(f'DE done: fun={res_de.fun:.4f}')

# Fine-tune with Nelder-Mead
print('\n=== Fine-tune (Nelder-Mead) ===')
res2 = minimize(cost_fn, xb, method='Nelder-Mead',
                options={'maxiter':5000,'xatol':1e-5,'fatol':1e-5})
if res2.fun < res_de.fun:
    xb = res2.x

Gm, Gs, Gm4, Gms4, Z0 = xb
Gn = Gm - 21.0
Gk2 = Gs + 4.0

et,eh=metrics(xb)
print(f'\n=== FINAL RESULTS ===')
print(f't-RMSE = {et/60:.1f} min   h-RMSE = {eh:.3f} m')
print(f'Z0    = {Z0:.3f} m')
print(f'G_M2  = {Gm:.1f}   A_M2  = {FIXED_A["M2"]:.3f} m')
print(f'G_S2  = {Gs:.1f}   A_S2  = {FIXED_A["S2"]:.3f} m')
print(f'G_N2  = {Gn:.1f}   A_N2  = {FIXED_A["N2"]:.3f} m')
print(f'G_K2  = {Gk2:.1f}   A_K2  = {FIXED_A["K2"]:.3f} m')
print(f'G_M4  = {Gm4:.1f}   A_M4  = {FIXED_A["M4"]:.3f} m')
print(f'G_MS4 = {Gms4:.1f}   A_MS4 = {FIXED_A["MS4"]:.3f} m')

print('\n=== Verification ===')
ok=0; total=0
prev_ds=None; terms_c=None; Z0_c=None
for (ds,t_ref,typ,h_ref) in REF:
    if ds!=prev_ds:
        Z0_c,terms_c=make_terms(Gm,Gs,Gm4,Gms4,Z0,ds); prev_ds=ds
    best_t,best_h=find_ext_fine(terms_c,Z0_c,t_ref,typ)
    dt=(best_t-t_ref)*60; dh=best_h-h_ref
    flag='OK' if abs(dt)<8 and abs(dh)<0.12 else '~~'
    if flag=='OK': ok+=1
    total+=1
    tc=best_t+2; rh=int(tc); rm=int((tc%1)*60)
    ref_c=t_ref+2; rrh=int(ref_c); rrm=int((ref_c%1)*60)
    print(f'[{flag}] {ds} {typ} ref:{rrh:02d}h{rrm:02d}/{h_ref:.2f}m pred:{rh:02d}h{rm:02d}/{best_h:.2f}m dt={dt:+.0f}min dh={dh:+.2f}m')
print(f'\n{ok}/{total} OK (dt<8min AND dh<12cm)')
