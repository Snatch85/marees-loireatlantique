#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Calibration v3 — correct starting point, positive-amplitude constraints,
maxiter=5000 for Phase 1 (converges ~3000), then L-BFGS-B + final NM.
"""
import math, calendar, sys
import numpy as np
from scipy.optimize import minimize

DEG = math.pi/180
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
    uM2=math.atan2(-0.03731*s(N)+0.00052*s(2*N),fM2)*180/math.pi
    fO1=1-0.18890*c(N)+0.00587*c(2*N)
    uO1=math.atan2(0.18890*s(N)-0.00587*s(2*N),fO1)*180/math.pi
    fK1=1+0.11583*c(N)-0.00292*c(2*N)
    uK1=math.atan2(-0.11583*s(N)+0.00292*s(2*N),fK1)*180/math.pi
    fK2=1+0.28519*c(N)+0.03240*c(2*N)
    uK2=math.atan2(-0.28519*s(N)-0.03240*s(2*N),fK2)*180/math.pi
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
        ('NU2',An*0.100/0.519,Gn+20),
        ('MU2',0.024,Gm+2),('P1',0.024,Gk1-15),('Q1',0.013,Go1),
    ]
    terms=[]
    for (n,A,G) in cst:
        spd=SPEEDS.get(n,0)
        if not spd: continue
        f,u=nod.get(n,(1,0)); phi=V0.get(n,0)
        terms.append((f*A, spd*DEG, (phi+u-G)*DEG))
    return Z0, terms

def find_ext(terms, Z0, t_ref, typ, window=3.5, step=1/120.0):
    def h(t): return Z0+sum(fA*math.cos(spd*t+off) for fA,spd,off in terms)
    best_t=t_ref; best_h=h(t_ref)
    n_steps=int(2*window/step)+1
    for i in range(n_steps):
        tt=t_ref-window+i*step; hv=h(tt)
        if typ=='PM' and hv>best_h: best_h=hv; best_t=tt
        if typ=='BM' and hv<best_h: best_h=hv; best_t=tt
    return best_t, best_h

def metrics(params):
    sq_t=0; sq_h=0; n=0; prev_ds=None
    for (ds,t_ref,typ,h_ref) in REF:
        if ds!=prev_ds:
            Z0_c,terms_c=make_terms(params,ds); prev_ds=ds
        bt,bh=find_ext(terms_c,Z0_c,t_ref,typ)
        sq_t+=(bt-t_ref)**2; sq_h+=(bh-h_ref)**2; n+=1
    return math.sqrt(sq_t/n)*60, math.sqrt(sq_h/n)

def cost(params):
    Z0,Gm,Gs,Gn,Gk2,Gk1,Go1,Gm4,Gms4,Am,As,An,Ak2,Ak1,Ao1,Am4,Ams4=params
    # Reject unphysical amplitudes
    if Am<0.5 or Am>3.5: return 1e9
    if As<0.05 or As>1.5: return 1e9
    if An<0.05 or An>1.0: return 1e9
    if Ak2<0.001 or Ak2>0.5: return 1e9
    if Ak1<0.001 or Ak1>0.3: return 1e9
    if Ao1<0.001 or Ao1>0.3: return 1e9
    if Am4<0.001 or Am4>0.3: return 1e9
    if Ams4<0.001 or Ams4>0.2: return 1e9
    sq=0; n=0; prev_ds=None
    for (ds,t_ref,typ,h_ref) in REF:
        if ds!=prev_ds:
            Z0_c,terms_c=make_terms(params,ds); prev_ds=ds
        bt,bh=find_ext(terms_c,Z0_c,t_ref,typ)
        dt_min=(bt-t_ref)*60; dh=bh-h_ref
        sq+=(dt_min/5)**2+(dh/0.05)**2; n+=1
    return math.sqrt(sq/n)

SCALE = 1.76/2.497

# Original SHOM starting point (scaled amplitudes to match data range)
x0 = np.array([
    3.30,           # Z0
    70.3,           # Gm (M2)
    99.2,           # Gs (S2)
    49.1,           # Gn (N2)
    99.8,           # Gk2 (K2)
    53.7,           # Gk1 (K1)
    16.6,           # Go1 (O1)
    191.5,          # Gm4 (M4)
    212.3,          # Gms4 (MS4)
    1.76,           # Am (M2) — from data
    0.44,           # As (S2) — from data
    0.37,           # An (N2) — scaled
    0.238*SCALE,    # Ak2
    0.101*SCALE,    # Ak1
    0.072*SCALE,    # Ao1
    0.091*SCALE,    # Am4
    0.060*SCALE,    # Ams4
])

et0,eh0=metrics(x0)
print(f'Start: t-RMSE={et0:.1f}min  h-RMSE={eh0:.3f}m')
sys.stdout.flush()

best_params = x0.copy()
best_cost = cost(x0)

call=[0]
def cb(xk):
    global best_params, best_cost
    call[0]+=1
    c=cost(xk)
    if c < best_cost:
        best_cost=c; best_params=xk.copy()
    if call[0]%500==0:
        et,eh=metrics(xk)
        Z0,Gm,Gs,Gn,Gk2,Gk1,Go1,Gm4,Gms4,Am,As,An,Ak2,Ak1,Ao1,Am4,Ams4=xk
        print(f'  iter {call[0]:5d}: t={et:.1f}min h={eh:.3f}m  Gm={Gm:.2f} Gs={Gs:.2f} Gn={Gn:.2f} Am={Am:.4f} As={As:.4f} Z0={Z0:.4f}')
        sys.stdout.flush()

print('=== Nelder-Mead phase 1 (maxiter=5000) ===')
r1=minimize(cost, x0, method='Nelder-Mead', callback=cb,
            options={'maxiter':5000,'xatol':1e-7,'fatol':1e-7,'adaptive':True})
if r1.fun < best_cost: best_params=r1.x.copy(); best_cost=r1.fun

et,eh=metrics(best_params)
print(f'  Phase 1 done: t={et:.1f}min h={eh:.3f}m')
sys.stdout.flush()

# L-BFGS-B with strict positive-amplitude bounds
print('=== L-BFGS-B fine-tune ===')
bounds=[
    (2.5,4.2),                        # Z0
    (50,180),(50,180),(30,160),(60,180), # Gm,Gs,Gn,Gk2
    (30,100),(0,60),(80,300),(80,350),  # Gk1,Go1,Gm4,Gms4
    (0.5,3.0),(0.05,1.5),(0.05,1.0),   # Am,As,An
    (0.01,0.5),(0.005,0.3),            # Ak2,Ak1
    (0.001,0.3),(0.001,0.3),(0.001,0.2), # Ao1,Am4,Ams4
]
r2=minimize(cost, best_params, method='L-BFGS-B', bounds=bounds,
            options={'maxiter':5000,'ftol':1e-15,'gtol':1e-9})
if r2.fun < best_cost: best_params=r2.x.copy(); best_cost=r2.fun

et,eh=metrics(best_params)
print(f'  L-BFGS-B done: t={et:.1f}min h={eh:.3f}m')
sys.stdout.flush()

# Final Nelder-Mead polish
print('=== Nelder-Mead phase 2 (from L-BFGS-B) ===')
r3=minimize(cost, best_params, method='Nelder-Mead',
            options={'maxiter':8000,'xatol':1e-8,'fatol':1e-8,'adaptive':True})
if r3.fun < best_cost: best_params=r3.x.copy(); best_cost=r3.fun

et,eh=metrics(best_params)
Z0,Gm,Gs,Gn,Gk2,Gk1,Go1,Gm4,Gms4,Am,As,An,Ak2,Ak1,Ao1,Am4,Ams4=best_params

print(f'\n=== RÉSULTATS FINAUX ===')
print(f't-RMSE = {et:.2f} min   h-RMSE = {eh:.4f} m')
print(f'Z0={Z0:.4f}')
print(f'M2:  Gm={Gm:.3f}  Am={Am:.4f}')
print(f'S2:  Gs={Gs:.3f}  As={As:.4f}')
print(f'N2:  Gn={Gn:.3f}  An={An:.4f}')
print(f'K2:  Gk2={Gk2:.3f}  Ak2={Ak2:.4f}')
print(f'K1:  Gk1={Gk1:.3f}  Ak1={Ak1:.4f}')
print(f'O1:  Go1={Go1:.3f}  Ao1={Ao1:.4f}')
print(f'M4:  Gm4={Gm4:.3f}  Am4={Am4:.4f}')
print(f'MS4: Gms4={Gms4:.3f}  Ams4={Ams4:.4f}')

print('\n=== Vérification point par point ===')
ok=0; total=0; prev_ds=None
for (ds,t_ref,typ,h_ref) in REF:
    if ds!=prev_ds:
        Z0_c,terms_c=make_terms(best_params,ds); prev_ds=ds
    bt,bh=find_ext(terms_c,Z0_c,t_ref,typ)
    dt=(bt-t_ref)*60; dh=bh-h_ref
    flag='OK' if abs(dt)<8 and abs(dh)<0.12 else '~~'
    if flag=='OK': ok+=1
    total+=1
    tc=bt+2; rh=int(tc); rm=int((tc%1)*60)
    ref_c=t_ref+2; rrh=int(ref_c); rrm=int((ref_c%1)*60)
    print(f'[{flag}] {ds} {typ} ref:{rrh:02d}h{rrm:02d}/{h_ref:.2f}m pred:{rh:02d}h{rm:02d}/{bh:.2f}m dt={dt:+.1f}min dh={dh:+.3f}m')
print(f'\n{ok}/{total} OK (|dt|<8min AND |dh|<0.12m)')

# Derived quantities for output
Anu2 = An*0.100/0.519
Gnu2 = Gn+20.0
Amu2 = 0.024; Gmu2 = Gm+2.0
Ap1 = 0.024;  Gp1  = Gk1-15.0
Aq1 = 0.013;  Gq1  = Go1

print('\n=== Constantes JavaScript (tide-calculator.js format) ===')
print(f"  SAINT_NAZAIRE: {{ nom: 'Saint-Nazaire', Z0: {Z0:.3f}, cst: {{")
print(f"    M2:    {{ A: {Am:.4f}, K: {Gm:.2f} }},  S2:    {{ A: {As:.4f}, K: {Gs:.2f} }},")
print(f"    N2:    {{ A: {An:.4f}, K: {Gn:.2f} }},  K2:    {{ A: {Ak2:.4f}, K: {Gk2:.2f} }},")
print(f"    K1:    {{ A: {Ak1:.4f}, K: {Gk1:.2f} }},  O1:    {{ A: {Ao1:.4f}, K: {Go1:.2f} }},")
print(f"    P1:    {{ A: {Ap1:.4f}, K: {Gp1:.2f} }},  Q1:    {{ A: {Aq1:.4f}, K: {Gq1:.2f} }},")
print(f"    M4:    {{ A: {Am4:.4f}, K: {Gm4:.2f} }},  MS4:   {{ A: {Ams4:.4f}, K: {Gms4:.2f} }},")
print(f"    MN4:   {{ A: 0.0220, K: 223.0 }},  '2N2': {{ A: 0.0700, K: 102.4 }},")
print(f"    NU2:   {{ A: {Anu2:.4f}, K: {Gnu2:.2f} }},  MU2:   {{ A: {Amu2:.4f}, K: {Gmu2:.2f} }},")
print(f"    M6:    {{ A: 0.0280, K: 316.7 }},")
print(f"  }}}}")

print('\n=== Constantes HTML (format {n:"M2", A:..., G:...}) ===')
print(f'      {{n:"M2",  A:{Am:.4f}, G:{Gm:.2f}}}, {{n:"S2",  A:{As:.4f}, G:{Gs:.2f}}}, {{n:"N2",  A:{An:.4f}, G:{Gn:.2f}}},')
print(f'      {{n:"K2",  A:{Ak2:.4f}, G:{Gk2:.2f}}},{{n:"NU2", A:{Anu2:.4f}, G:{Gnu2:.2f}}}, {{n:"MU2", A:{Amu2:.4f}, G:{Gmu2:.2f}}},')
print(f'      {{n:"L2",  A:0.0300, G:116.0}},{{n:"T2",  A:0.0220, G:98.5}},   {{n:"p2N2",A:0.0700,G:102.4}},')
print(f'      {{n:"K1",  A:{Ak1:.4f}, G:{Gk1:.2f}}}, {{n:"O1",  A:{Ao1:.4f}, G:{Go1:.2f}}}, {{n:"P1",  A:{Ap1:.4f}, G:{Gp1:.2f}}},')
print(f'      {{n:"Q1",  A:{Aq1:.4f}, G:{Gq1:.2f}}},{{n:"M4",  A:{Am4:.4f}, G:{Gm4:.2f}}}, {{n:"MN4", A:0.0220, G:223.0}},')
print(f'      {{n:"MS4", A:{Ams4:.4f}, G:{Gms4:.2f}}},{{n:"M6",  A:0.0280, G:316.7}}, {{n:"MK3", A:0.0080, G:179.8}},')

print(f'\n=== En-tête HTML ===')
print(f'  Z0:{Z0:.3f}, M2_A:{Am:.4f},')
