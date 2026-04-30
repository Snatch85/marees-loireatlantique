#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Calibration correcte de Saint-Nazaire :
Optimise G + A pour que les EXTREMA du modele
correspondent aux extrema SHOM (temps ET hauteurs).
"""
import math, calendar, sys

DEG = math.pi/180; RAD = 180/math.pi
mod360 = lambda x: ((x%360)+360)%360
J2000_MS = 946728000000

SPEEDS = {
    'M2':28.9841042,'S2':30.0,'N2':28.4397295,'K2':30.0821373,
    'K1':15.0410686,'O1':13.9430356,'NU2':28.5125831,'MU2':27.9682084,
    'M4':57.9682084,'MS4':58.9841042,'MN4':57.4238337,'M6':86.9523126,
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
        'M2':(fM2,uM2),'S2':(1,0),'N2':(fM2,uM2),'K2':(fK2,uK2),
        'K1':(fK1,uK1),'O1':(fO1,uO1),'NU2':(fM2,uM2),'MU2':(fM2,uM2),
        'M4':(fM2**2,2*uM2),'MS4':(fM2,uM2),'MN4':(fM2**2,2*uM2),
        'M6':(fM2**3,3*uM2),'P1':(1,0),'Q1':(fO1,uO1),
    }

def equil(a):
    s,h,p = a['s'],a['h'],a['p']; r=mod360
    return {
        'M2': r(2*h-2*s),    'S2': 0,
        'N2': r(2*h-3*s+p),  'K2': r(2*h),
        'K1': r(h+90),        'O1': r(h-2*s-90),
        'NU2':r(2*h-3*s+p),  'MU2':r(4*h-4*s),
        'M4': r(4*h-4*s),    'MS4':r(2*h-2*s),
        'MN4':r(4*h-5*s+p),  'M6': r(6*h-6*s),
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

def make_h_fn(p, ms0):
    a=astro(ms0); V0=equil(a); nod=nodal(a['N'])
    cst = [
        ('M2',  p['Am'],  p['Gm']),
        ('S2',  p['As'],  p['Gs']),
        ('N2',  p['An'],  p['Gn']),
        ('K2',  p['Ak2'], p['Gk2']),
        ('K1',  p['Ak1'], p['Gk1']),
        ('O1',  p['Ao1'], p['Go1']),
        ('M4',  p['Am4'], p['Gm4']),
        ('MS4', p['Ams4'],p['Gms4']),
        ('NU2', 0.100,    p['Gn']+20),
        ('MU2', 0.024,    p['Gm']+2),
        ('P1',  0.024,    p['Gk1']-15),
        ('Q1',  0.013,    p['Go1']+0),
    ]
    def h(t):
        hh = p['Z0']
        for (n,A,G) in cst:
            spd = SPEEDS.get(n,0)
            if not spd: continue
            f,u = nod.get(n,(1,0)); phi = V0.get(n,0)
            hh += f*A*math.cos((phi+u+spd*t-G)*DEG)
        return hh
    return h

def find_extremum(h_fn, t_ref, typ, window=3.5, step=0.01):
    """Find extremum nearest to t_ref within +/-window hours."""
    best_t=t_ref; best_h=h_fn(t_ref)
    t = t_ref - window
    while t <= t_ref + window:
        hv = h_fn(t)
        if typ=='PM' and hv > best_h: best_h=hv; best_t=t
        if typ=='BM' and hv < best_h: best_h=hv; best_t=t
        t += step
    return best_t, best_h

def cost_components(p):
    sq_t=0; sq_h=0; n=0
    for (ds,t_ref,typ,h_ref) in REF:
        ms0 = ms0_of(ds)
        h_fn = make_h_fn(p, ms0)
        t_pred,h_pred = find_extremum(h_fn, t_ref, typ)
        dt = (t_pred-t_ref)*60  # minutes
        dh = h_pred-h_ref
        sq_t += dt*dt; sq_h += dh*dh; n += 1
    return math.sqrt(sq_t/n), math.sqrt(sq_h/n)

def combined_cost(p):
    et, eh = cost_components(p)
    return 30*et + 100*eh  # 30 min timing ~ 0.3m height

def gradient_descent(p0, keys, step, lr, n_iter, bounds=None):
    bounds = bounds or {}
    p = dict(p0); best=dict(p0); best_c=combined_cost(p)
    for it in range(n_iter):
        for key in keys:
            pp=dict(p); pp[key]+=step
            pm=dict(p); pm[key]-=step
            g = (combined_cost(pp)-combined_cost(pm))/(2*step)
            p[key] -= lr*g
            if key.startswith('A'): p[key]=max(0.001,p[key])
            if key in bounds:
                lo,hi=bounds[key]; p[key]=max(lo,min(hi,p[key]))
        c = combined_cost(p)
        if c < best_c: best_c=c; best=dict(p)
        if it%1000==0:
            et,eh = cost_components(p)
            print(f"  iter {it:4d}: t={et:.1f}min h={eh:.3f}m  Gm={p['Gm']:.1f} Gm4={p['Gm4']:.1f} Am={p['Am']:.3f} Z0={p['Z0']:.3f}")
    return best

# --- Initial: original SHOM-like constants ---
p0 = {
    'Z0': 3.147,
    'Gm':  70.3, 'Am':  2.497,
    'Gs':  99.2, 'As':  0.851,
    'Gn':  49.1, 'An':  0.519,
    'Gk2': 99.8, 'Ak2': 0.238,
    'Gk1': 53.7, 'Ak1': 0.101,
    'Go1': 16.6, 'Ao1': 0.072,
    'Gm4':191.5, 'Am4': 0.091,
    'Gms4':212.3,'Ams4':0.060,
}

print("Initial (SHOM-like constants):")
et,eh = cost_components(p0)
print(f"  t-RMSE={et:.1f}min  h-RMSE={eh:.3f}m")
print()

KEYS_G   = ['Gm','Gs','Gn','Gk2','Gk1','Go1','Gm4','Gms4','Z0']
KEYS_ALL = KEYS_G + ['Am','As','An','Ak2','Ak1','Ao1','Am4','Ams4']
BOUNDS = {'Am':(1.0,3.5),'As':(0.3,1.5),'Am4':(0.01,0.3),'Ams4':(0.01,0.2)}

print("=== Phase 1: G phases only (step=1, lr=0.05) ===")
p1 = gradient_descent(p0, KEYS_G, step=1.0, lr=0.05, n_iter=4000)
et,eh = cost_components(p1)
print(f"  => t-RMSE={et:.1f}min  h-RMSE={eh:.3f}m")

print("\n=== Phase 2: all params (step=0.5, lr=0.02) ===")
p2 = gradient_descent(p1, KEYS_ALL, step=0.5, lr=0.02, n_iter=5000, bounds=BOUNDS)
et,eh = cost_components(p2)
print(f"  => t-RMSE={et:.1f}min  h-RMSE={eh:.3f}m")

print("\n=== Phase 3: fine tune (step=0.1, lr=0.008) ===")
p3 = gradient_descent(p2, KEYS_ALL, step=0.1, lr=0.008, n_iter=3000, bounds=BOUNDS)

best = p3
et,eh = cost_components(best)
print(f"\n=== FINAL RESULTS ===")
print(f"t-RMSE = {et:.1f} min   h-RMSE = {eh:.3f} m")
print(f"Z0    = {best['Z0']:.3f} m")
print(f"G_M2  = {best['Gm']:.1f}   A_M2  = {best['Am']:.3f} m")
print(f"G_S2  = {best['Gs']:.1f}   A_S2  = {best['As']:.3f} m")
print(f"G_N2  = {best['Gn']:.1f}   A_N2  = {best['An']:.3f} m")
print(f"G_K2  = {best['Gk2']:.1f}   A_K2  = {best['Ak2']:.3f} m")
print(f"G_K1  = {best['Gk1']:.1f}   A_K1  = {best['Ak1']:.3f} m")
print(f"G_O1  = {best['Go1']:.1f}   A_O1  = {best['Ao1']:.3f} m")
print(f"G_M4  = {best['Gm4']:.1f}   A_M4  = {best['Am4']:.3f} m")
print(f"G_MS4 = {best['Gms4']:.1f}   A_MS4 = {best['Ams4']:.3f} m")

print("\n=== Verification point par point ===")
for (ds,t_ref,typ,h_ref) in REF:
    ms0 = ms0_of(ds)
    h_fn = make_h_fn(best, ms0)
    t_pred,h_pred = find_extremum(h_fn, t_ref, typ)
    dt = (t_pred-t_ref)*60
    dh = h_pred-h_ref
    flag = 'OK' if abs(dt)<10 and abs(dh)<0.15 else '~~'
    tc = t_pred+2
    print(f"[{flag}] {ds} {typ}  ref:{t_ref+2:.2f}h_CEST/{h_ref:.2f}m  pred:{tc:.2f}h_CEST/{h_pred:.2f}m  dt={dt:+.0f}min dh={dh:+.2f}m")
