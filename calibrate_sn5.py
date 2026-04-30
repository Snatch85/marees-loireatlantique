#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Calibration Saint-Nazaire v5 - clean slate.
Starts from amplitude estimates derived from the data range:
  Z0 ~ 3.33m, A_M2 ~ 1.76m, A_S2 ~ 0.44m
Optimises ALL 17 parameters with fine search (0.5 min steps).
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

REF = [
    ('2026-04-22', 1.167,'BM',1.25), ('2026-04-22', 6.483,'PM',5.18),
    ('2026-04-22',13.500,'BM',1.65), ('2026-04-22',18.700,'PM',5.21),
    ('2026-04-23', 2.150,'BM',1.64), ('2026-04-23', 7.417,'PM',4.71),
    ('2026-04-23',14.550,'BM',2.03), ('2026-04-23',19.750,'PM',4.81),
    ('2026-04-24', 3.283,'BM',1.95), ('2026-04-24',10.717,'PM',4.58),
    ('2026-04-24',15.750,'BM',2.27), ('2026-04-24',23.150,'PM',4.77),
    ('2026-04-25', 4.533,'BM',2.08), ('2026-04-25',11.933,'PM',4.71),
    ('2026-04-25',17.017,'BM',2.27),
    ('2026-04-26', 0.300,'PM',4.92), ('2026-04-26', 5.817,'BM',1.99),
    ('2026-04-26',12.883,'PM',4.90), ('2026-04-26',18.217,'BM',2.07),
    ('2026-04-27', 1.167,'PM',5.09), ('2026-04-27', 6.933,'BM',1.76),
    ('2026-04-27',13.533,'PM',5.08), ('2026-04-27',19.250,'BM',1.79),
    ('2026-04-28', 1.733,'PM',5.24), ('2026-04-28', 7.817,'BM',1.52),
    ('2026-04-28',13.917,'PM',5.25), ('2026-04-28',20.100,'BM',1.54),
    ('2026-04-29', 2.400,'PM',5.38), ('2026-04-29', 8.450,'BM',1.33),
    ('2026-04-29',14.650,'PM',5.31),
    ('2026-04-30', 2.783,'PM',5.47), ('2026-04-30', 9.133,'BM',1.21),
    ('2026-04-30',14.967,'PM',5.44),
]
print(f'{len(REF)} reference points (Apr 22-30 2026 UTC)')

_cache={}
def get_env(ds):
    if ds not in _cache:
        a=astro(ms0_of(ds)); _cache[ds]=(equil(a),nodal(a['N']))
    return _cache[ds]

# params = [Z0, Gm, Gs, Gn, Gk2, Gk1, Go1, Gm4, Gms4,
#            Am, As, An, Ak2, Ak1, Ao1, Am4, Ams4]
def make_terms(params, ds):
    Z0,Gm,Gs,Gn,Gk2,Gk1,Go1,Gm4,Gms4,Am,As,An,Ak2,Ak1,Ao1,Am4,Ams4=params
    V0,nod=get_env(ds)
    cst=[
        ('M2',Am,Gm),('S2',As,Gs),('N2',An,Gn),('K2',Ak2,Gk2),
        ('K1',Ak1,Gk1),('O1',Ao1,Go1),('M4',Am4,Gm4),('MS4',Ams4,Gms4),
        ('NU2',0.100*An/0.519,Gn+20),  # scale NU2 with N2
        ('MU2',0.024,Gm+2),
        ('P1',0.024,Gk1-15),
        ('Q1',0.013,Go1),
    ]
    terms=[]
    for (n,A,G) in cst:
        spd=SPEEDS.get(n,0)
        if not spd: continue
        f,u=nod.get(n,(1,0)); phi=V0.get(n,0)
        terms.append((f*A, spd*DEG, (phi+u-G)*DEG))
    return Z0, terms

# Fine extremum search: window ±3.5h, step 0.5 min
def find_ext(terms, Z0, t_ref, typ, window=3.5, step=1/120.0):
    def h(t): return Z0+sum(fA*math.cos(spd*t+off) for fA,spd,off in terms)
    best_t=t_ref; best_h=h(t_ref)
    n=int(2*window/step)+1
    for i in range(n):
        tt=t_ref-window+i*step; hv=h(tt)
        if typ=='PM' and hv>best_h: best_h=hv; best_t=tt
        if typ=='BM' and hv<best_h: best_h=hv; best_t=tt
    return best_t, best_h

def metrics(params):
    sq_t=0; sq_h=0; n=0
    prev_ds=None
    for (ds,t_ref,typ,h_ref) in REF:
        if ds!=prev_ds:
            Z0_c,terms_c=make_terms(params,ds); prev_ds=ds
        bt,bh=find_ext(terms_c,Z0_c,t_ref,typ)
        sq_t+=(bt-t_ref)**2*3600; sq_h+=(bh-h_ref)**2; n+=1
    return math.sqrt(sq_t/n), math.sqrt(sq_h/n)

def cost(params):
    # Penalise unreasonable amplitudes
    Z0,Gm,Gs,Gn,Gk2,Gk1,Go1,Gm4,Gms4,Am,As,An,Ak2,Ak1,Ao1,Am4,Ams4=params
    if Am<0.5 or Am>3.5 or As<0.05 or As>1.5 or An<0.05 or An>1.0: return 1e9
    if Am4<0.001 or Ams4<0.001: return 1e9
    sq_t=0; sq_h=0; n=0
    prev_ds=None
    for (ds,t_ref,typ,h_ref) in REF:
        if ds!=prev_ds:
            Z0_c,terms_c=make_terms(params,ds); prev_ds=ds
        bt,bh=find_ext(terms_c,Z0_c,t_ref,typ)
        dt_min=(bt-t_ref)*60; dh=bh-h_ref
        # Weight: 1 min timing ~ 0.01m height (penalise both roughly equally)
        sq_t+=(dt_min/5)**2; sq_h+=(dh/0.05)**2; n+=1
    return math.sqrt((sq_t+sq_h)/n)

# ---- Starting point: amplitude estimates from data range ----
# Z0: average (PM_max + BM_min)/2 over spring and neap:
#   spring: (5.47+1.21)/2=3.34, neap: (4.58+1.95)/2=3.27 -> ~3.30
# A_M2: from (PM_spring-Z0-A_S2)/f_M2, estimated ~1.76m
# A_S2: from (PM_spring-PM_neap)/2 ~ 0.44m
# A_N2: maintain ratio A_N2/A_M2 ~ 0.519/2.497 = 0.208 -> 0.37m
# Other amplitudes scaled from original by ratio A_M2_new/A_M2_orig
# G values: start from original SHOM values (G_M2=70.3 was always the best start)

SCALE = 1.76 / 2.497  # amplitude scaling factor

x0 = np.array([
    3.30,           # Z0
    70.3,           # G_M2
    99.2,           # G_S2
    49.1,           # G_N2
    99.8,           # G_K2
    53.7,           # G_K1
    16.6,           # G_O1
    191.5,          # G_M4
    212.3,          # G_MS4
    1.76,           # A_M2
    0.44,           # A_S2
    0.37,           # A_N2  (1.76 * 0.519/2.497)
    0.238*SCALE,    # A_K2
    0.101*SCALE,    # A_K1
    0.072*SCALE,    # A_O1
    0.091*SCALE,    # A_M4
    0.060*SCALE,    # A_MS4
])

et0,eh0=metrics(x0)
print(f'Start x0: t-RMSE={et0/60:.1f}min  h-RMSE={eh0:.3f}m')

# Also try starting from deployed constants
x_dep = np.array([
    3.308,93.2,128.7,72.1,132.7,53.7,16.6,191.5,212.3,
    1.563,0.662,0.430,0.130,0.101,0.072,0.091,0.060])
et_dep,eh_dep=metrics(x_dep)
print(f'Start deployed: t-RMSE={et_dep/60:.1f}min  h-RMSE={eh_dep:.3f}m')
print()

call=[0]
def cb(xk):
    call[0]+=1
    if call[0]%500==0:
        et,eh=metrics(xk)
        print(f'  iter {call[0]:5d}: t={et/60:.1f}min h={eh:.3f}m  Gm={xk[1]:.1f} Gs={xk[2]:.1f} Am={xk[9]:.3f} As={xk[10]:.3f} Z0={xk[0]:.3f}')
        sys.stdout.flush()

# Phase 1: Nelder-Mead from x0
print('=== Phase 1: Nelder-Mead from x0 ===')
r1=minimize(cost,x0,method='Nelder-Mead',callback=cb,
            options={'maxiter':100000,'xatol':1e-6,'fatol':1e-6,'adaptive':True})
xb=r1.x
et,eh=metrics(xb)
print(f'  => t={et/60:.1f}min h={eh:.3f}m  cost={r1.fun:.4f}')

# Phase 2: Nelder-Mead from deployed
print('=== Phase 2: Nelder-Mead from deployed ===')
r2=minimize(cost,x_dep,method='Nelder-Mead',callback=cb,
            options={'maxiter':100000,'xatol':1e-6,'fatol':1e-6,'adaptive':True})
if metrics(r2.x)[0]<metrics(xb)[0]: xb=r2.x
et,eh=metrics(xb)
print(f'  => t={et/60:.1f}min h={eh:.3f}m  cost={r2.fun:.4f}')

# Phase 3: L-BFGS-B fine-tune with bounds
print('=== Phase 3: L-BFGS-B fine-tune ===')
bounds=[
    (2.5,4.0),   # Z0
    (None,None),(None,None),(None,None),(None,None),
    (None,None),(None,None),(None,None),(None,None),
    (0.5,3.0),(0.05,1.2),(0.05,0.8),(0.01,0.4),
    (0.01,0.2),(0.001,0.2),(0.001,0.2),(0.001,0.15),
]
r3=minimize(cost,xb,method='L-BFGS-B',bounds=bounds,
            options={'maxiter':3000,'ftol':1e-14,'gtol':1e-8})
if r3.fun<cost(xb): xb=r3.x

# Final metrics and print
et,eh=metrics(xb)
Z0,Gm,Gs,Gn,Gk2,Gk1,Go1,Gm4,Gms4,Am,As,An,Ak2,Ak1,Ao1,Am4,Ams4=xb
print(f'\n=== FINAL RESULTS ===')
print(f't-RMSE = {et/60:.1f} min   h-RMSE = {eh:.3f} m')
print(f'Z0={Z0:.3f}')
print(f'G_M2={Gm:.2f}  A_M2={Am:.4f}')
print(f'G_S2={Gs:.2f}  A_S2={As:.4f}')
print(f'G_N2={Gn:.2f}  A_N2={An:.4f}')
print(f'G_K2={Gk2:.2f}  A_K2={Ak2:.4f}')
print(f'G_K1={Gk1:.2f}  A_K1={Ak1:.4f}')
print(f'G_O1={Go1:.2f}  A_O1={Ao1:.4f}')
print(f'G_M4={Gm4:.2f}  A_M4={Am4:.4f}')
print(f'G_MS4={Gms4:.2f}  A_MS4={Ams4:.4f}')

print('\n=== Verification ===')
ok=0; total=0
prev_ds=None
for (ds,t_ref,typ,h_ref) in REF:
    if ds!=prev_ds:
        Z0_c,terms_c=make_terms(xb,ds); prev_ds=ds
    bt,bh=find_ext(terms_c,Z0_c,t_ref,typ)
    dt=(bt-t_ref)*60; dh=bh-h_ref
    flag='OK' if abs(dt)<8 and abs(dh)<0.12 else '~~'
    if flag=='OK': ok+=1; total+=1
    tc=bt+2; rh=int(tc); rm=int((tc%1)*60)
    ref_c=t_ref+2; rrh=int(ref_c); rrm=int((ref_c%1)*60)
    print(f'[{flag}] {ds} {typ} ref:{rrh:02d}h{rrm:02d}/{h_ref:.2f}m pred:{rh:02d}h{rm:02d}/{bh:.2f}m dt={dt:+.0f}min dh={dh:+.2f}m')
print(f'\n{ok}/{total} OK (|dt|<8min AND |dh|<0.12m)')
