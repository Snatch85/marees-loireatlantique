#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Calibration Saint-Nazaire - minimise timing + height errors on SHOM extrema.
Uses scipy.optimize for speed.
"""
import math, calendar, sys
import numpy as np
from scipy.optimize import minimize

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
    y,m,d = int(s[:4]),int(s[5:7]),int(s[8:10])
    return calendar.timegm((y,m,d,0,0,0,0,0,0))*1000

def astro(ms):
    d = (ms-J2000_MS)/86400000.0
    return {
        's': mod360(218.3164477+13.17639648*d),
        'h': mod360(280.4664567+ 0.98564736*d),
        'p': mod360( 83.3532465+ 0.11140353*d),
        'N': mod360(125.0445479- 0.05295378*d),
    }

def nodal(N_deg):
    N=N_deg*DEG; c=math.cos; s=math.sin
    fM2 = 1-0.03731*c(N)+0.00052*c(2*N)
    uM2 = math.atan2(-0.03731*s(N)+0.00052*s(2*N), fM2)*RAD
    fO1 = 1-0.18890*c(N)+0.00587*c(2*N)
    uO1 = math.atan2(0.18890*s(N)-0.00587*s(2*N), fO1)*RAD
    fK1 = 1+0.11583*c(N)-0.00292*c(2*N)
    uK1 = math.atan2(-0.11583*s(N)+0.00292*s(2*N), fK1)*RAD
    fK2 = 1+0.28519*c(N)+0.03240*c(2*N)
    uK2 = math.atan2(-0.28519*s(N)-0.03240*s(2*N), fK2)*RAD
    return {
        'M2':(fM2,uM2),'S2':(1.0,0.0),'N2':(fM2,uM2),'K2':(fK2,uK2),
        'K1':(fK1,uK1),'O1':(fO1,uO1),'NU2':(fM2,uM2),'MU2':(fM2,uM2),
        'M4':(fM2**2,2*uM2),'MS4':(fM2,uM2),'MN4':(fM2**2,2*uM2),
        'P1':(1.0,0.0),'Q1':(fO1,uO1),
    }

def equil(a):
    s,h,p = a['s'],a['h'],a['p']; r=mod360
    return {
        'M2': r(2*h-2*s),    'S2': 0.0,
        'N2': r(2*h-3*s+p),  'K2': r(2*h),
        'K1': r(h+90),        'O1': r(h-2*s-90),
        'NU2':r(2*h-3*s+p),  'MU2':r(4*h-4*s),
        'M4': r(4*h-4*s),    'MS4':r(2*h-2*s),
        'MN4':r(4*h-5*s+p),
        'P1': r(-h+270),      'Q1': r(h-3*s+p-90),
    }

# SHOM reference extrema (date_str, t_utc_hours, type, height_m)
REF = [
    ('2026-04-22',  1.167,'BM',1.25), ('2026-04-22',  6.483,'PM',5.18),
    ('2026-04-22', 13.500,'BM',1.65), ('2026-04-22', 18.700,'PM',5.21),
    ('2026-04-23',  2.150,'BM',1.64), ('2026-04-23',  7.417,'PM',4.71),
    ('2026-04-23', 14.550,'BM',2.03), ('2026-04-23', 19.750,'PM',4.81),
    ('2026-04-27',  1.167,'PM',5.09), ('2026-04-27',  6.933,'BM',1.76),
    ('2026-04-27', 13.533,'PM',5.08),
    ('2026-04-28',  1.733,'PM',5.24), ('2026-04-28',  7.817,'BM',1.52),
    ('2026-04-28', 13.917,'PM',5.25),
    ('2026-04-29',  2.400,'PM',5.38), ('2026-04-29',  8.450,'BM',1.33),
    ('2026-04-29', 14.650,'PM',5.31),
    ('2026-04-30',  2.783,'PM',5.47), ('2026-04-30',  9.133,'BM',1.21),
    ('2026-04-30', 14.967,'PM',5.44),
]

# Pre-compute astronomy for each reference date
_astro_cache = {}
def get_env(ds):
    if ds not in _astro_cache:
        ms0 = ms0_of(ds)
        a = astro(ms0)
        _astro_cache[ds] = (equil(a), nodal(a['N']))
    return _astro_cache[ds]

# T_SEARCH: times at which we evaluate h() around each reference point
# Use 15-min steps over ±3h window = 24 evaluations
SEARCH_DT = [i*0.25 - 3.0 for i in range(25)]  # -3 to +3 hours step 0.25h

def make_residuals(params):
    """
    params = [Z0, Gm, Gs, Gn, Gk2, Gk1, Go1, Gm4, Gms4,
              Am, As, An, Ak2, Ak1, Ao1, Am4, Ams4]
    Returns residuals: [dt1_min, dh1_m, dt2_min, dh2_m, ...]
    """
    Z0,Gm,Gs,Gn,Gk2,Gk1,Go1,Gm4,Gms4,Am,As,An,Ak2,Ak1,Ao1,Am4,Ams4 = params

    residuals = []
    for (ds, t_ref, typ, h_ref) in REF:
        V0, nod = get_env(ds)
        cst_list = [
            ('M2',Am,Gm),('S2',As,Gs),('N2',An,Gn),('K2',Ak2,Gk2),
            ('K1',Ak1,Gk1),('O1',Ao1,Go1),('M4',Am4,Gm4),('MS4',Ams4,Gms4),
            ('NU2',0.100,Gn+20),('MU2',0.024,Gm+2),
            ('P1',0.024,Gk1-15),('Q1',0.013,Go1),
        ]
        # Precompute terms
        terms = []
        for (n,A,G) in cst_list:
            spd = SPEEDS.get(n,0)
            if not spd: continue
            f,u = nod.get(n,(1.0,0.0))
            phi = V0.get(n,0.0)
            offset = (phi+u-G)*DEG
            terms.append((f*A, spd*DEG, offset))

        def h(t):
            hh = Z0
            for (fA, spd_rad, off) in terms:
                hh += fA * math.cos(spd_rad*t + off)
            return hh

        # Find extremum in search window
        best_t = t_ref; best_h = h(t_ref)
        for dt in SEARCH_DT:
            tt = t_ref + dt
            hv = h(tt)
            if typ == 'PM' and hv > best_h: best_h=hv; best_t=tt
            if typ == 'BM' and hv < best_h: best_h=hv; best_t=tt

        # Residuals: weight timing in minutes (x30 relative to height)
        dt_min = (best_t - t_ref) * 60.0
        dh = best_h - h_ref
        residuals.append(dt_min * 30.0)  # 1 min timing = 30 cost units
        residuals.append(dh * 100.0)     # 0.01m height = 1 cost unit

    return residuals

def cost(params):
    r = make_residuals(params)
    return sum(x*x for x in r) / len(r)

# Parameter names for display
PNAMES = ['Z0','Gm','Gs','Gn','Gk2','Gk1','Go1','Gm4','Gms4',
          'Am','As','An','Ak2','Ak1','Ao1','Am4','Ams4']

# Initial values (original SHOM-like)
x0 = np.array([3.147, 70.3, 99.2, 49.1, 99.8, 53.7, 16.6, 191.5, 212.3,
                2.497, 0.851, 0.519, 0.238, 0.101, 0.072, 0.091, 0.060])

print("Initial params (SHOM-like):")
r0 = make_residuals(x0)
sq_t = sum((r0[i])**2 for i in range(0,len(r0),2)) / (len(r0)/2)
sq_h = sum((r0[i])**2 for i in range(1,len(r0),2)) / (len(r0)/2)
print(f"  t-RMSE = {math.sqrt(sq_t)/30:.1f} min")
print(f"  h-RMSE = {math.sqrt(sq_h)/100:.3f} m")
print()

call_count = [0]
def cb(xk):
    call_count[0] += 1
    if call_count[0] % 50 == 0:
        r = make_residuals(xk)
        sq_t = sum(r[i]**2 for i in range(0,len(r),2))/(len(r)/2)
        sq_h = sum(r[i]**2 for i in range(1,len(r),2))/(len(r)/2)
        print(f"  iter {call_count[0]:4d}: t={math.sqrt(sq_t)/30:.1f}min h={math.sqrt(sq_h)/100:.3f}m  Gm={xk[1]:.1f} Gm4={xk[7]:.1f} Am={xk[9]:.3f} Z0={xk[0]:.3f}")
    sys.stdout.flush()

# Bounds: G unconstrained, A >= 0.001
bounds_list = [
    (None, None),    # Z0
    (None, None), (None, None), (None, None), (None, None),  # G phases
    (None, None), (None, None), (None, None), (None, None),
    (0.5, 3.5),      # Am
    (0.2, 1.5),      # As
    (0.1, 1.0),      # An
    (0.01, 0.5),     # Ak2
    (0.01, 0.3),     # Ak1
    (0.001, 0.3),    # Ao1
    (0.001, 0.3),    # Am4
    (0.001, 0.2),    # Ams4
]

print("=== Optimization (Nelder-Mead) ===")
result = minimize(cost, x0, method='Nelder-Mead', callback=cb,
                  options={'maxiter': 50000, 'xatol': 1e-4, 'fatol': 1e-4,
                           'adaptive': True})
print(f"Nelder-Mead done: success={result.success}, fun={result.fun:.4f}")

xbest = result.x
print("\n=== L-BFGS-B fine tune ===")
result2 = minimize(cost, xbest, method='L-BFGS-B', bounds=bounds_list,
                   options={'maxiter': 2000, 'ftol': 1e-10, 'gtol': 1e-6})
print(f"L-BFGS-B done: success={result2.success}, fun={result2.fun:.4f}")
xbest = result2.x

# Final report
r = make_residuals(xbest)
sq_t = sum(r[i]**2 for i in range(0,len(r),2))/(len(r)/2)
sq_h = sum(r[i]**2 for i in range(1,len(r),2))/(len(r)/2)
et = math.sqrt(sq_t)/30; eh = math.sqrt(sq_h)/100
print(f"\n=== FINAL RESULTS ===")
print(f"t-RMSE = {et:.1f} min   h-RMSE = {eh:.3f} m")
Z0,Gm,Gs,Gn,Gk2,Gk1,Go1,Gm4,Gms4,Am,As,An,Ak2,Ak1,Ao1,Am4,Ams4 = xbest
print(f"Z0    = {Z0:.3f} m")
print(f"G_M2  = {Gm:.1f}   A_M2  = {Am:.3f} m")
print(f"G_S2  = {Gs:.1f}   A_S2  = {As:.3f} m")
print(f"G_N2  = {Gn:.1f}   A_N2  = {An:.3f} m")
print(f"G_K2  = {Gk2:.1f}  A_K2  = {Ak2:.3f} m")
print(f"G_K1  = {Gk1:.1f}   A_K1  = {Ak1:.3f} m")
print(f"G_O1  = {Go1:.1f}   A_O1  = {Ao1:.3f} m")
print(f"G_M4  = {Gm4:.1f}   A_M4  = {Am4:.3f} m")
print(f"G_MS4 = {Gms4:.1f}  A_MS4 = {Ams4:.3f} m")

# Point-by-point
print("\n=== Verification ===")
V0_ds = {}; nod_ds = {}
for (ds,t_ref,typ,h_ref) in REF:
    V0, nod = get_env(ds)
    cst_list = [
        ('M2',Am,Gm),('S2',As,Gs),('N2',An,Gn),('K2',Ak2,Gk2),
        ('K1',Ak1,Gk1),('O1',Ao1,Go1),('M4',Am4,Gm4),('MS4',Ams4,Gms4),
        ('NU2',0.100,Gn+20),('MU2',0.024,Gm+2),
        ('P1',0.024,Gk1-15),('Q1',0.013,Go1),
    ]
    terms = []
    for (n,A,G) in cst_list:
        spd = SPEEDS.get(n,0)
        if not spd: continue
        f,u = nod.get(n,(1.0,0.0)); phi = V0.get(n,0.0)
        terms.append((f*A, spd*DEG, (phi+u-G)*DEG))
    def h(t, terms=terms):
        return Z0 + sum(fA*math.cos(spd*t+off) for fA,spd,off in terms)

    # finer search for verification
    best_t=t_ref; best_h=h(t_ref)
    for i in range(-360,361):
        tt=t_ref+i/120.0
        hv=h(tt)
        if typ=='PM' and hv>best_h: best_h=hv; best_t=tt
        if typ=='BM' and hv<best_h: best_h=hv; best_t=tt

    dt=(best_t-t_ref)*60; dh=best_h-h_ref
    flag='OK' if abs(dt)<10 and abs(dh)<0.15 else '~~'
    tc=best_t+2
    hh=int(tc); mm=int((tc%1)*60)
    rh=int(t_ref+2); rm=int(((t_ref+2)%1)*60)
    print(f"[{flag}] {ds} {typ}  ref:{rh:02d}h{rm:02d}/{h_ref:.2f}m  pred:{hh:02d}h{mm:02d}/{best_h:.2f}m  dt={dt:+.0f}min dh={dh:+.2f}m")
