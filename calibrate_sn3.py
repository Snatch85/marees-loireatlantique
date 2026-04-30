#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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

# FULL dataset: maree.info April 22-30 2026 (CEST -> UTC = CEST - 2h)
REF = [
    # Apr 22 (coeff 65-73)
    ('2026-04-22', 1.167,'BM',1.25), ('2026-04-22', 6.483,'PM',5.18),
    ('2026-04-22',13.500,'BM',1.65), ('2026-04-22',18.700,'PM',5.21),
    # Apr 23 (coeff 51-58)
    ('2026-04-23', 2.150,'BM',1.64), ('2026-04-23', 7.417,'PM',4.71),
    ('2026-04-23',14.550,'BM',2.03), ('2026-04-23',19.750,'PM',4.81),
    # Apr 24 (coeff ~44-47 neap)
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
print(f'Total reference points: {len(REF)}')

_cache = {}
def get_env(ds):
    if ds not in _cache:
        a = astro(ms0_of(ds))
        _cache[ds] = (equil(a), nodal(a['N']))
    return _cache[ds]

SEARCH_DT = [i*0.25-3.5 for i in range(29)]  # -3.5 to +3.5h step 0.25h

def make_terms(params, ds):
    Z0,Gm,Gs,Gn,Gk2,Gk1,Go1,Gm4,Gms4,Am,As,An,Ak2,Ak1,Ao1,Am4,Ams4 = params
    V0,nod = get_env(ds)
    cst = [
        ('M2',Am,Gm),('S2',As,Gs),('N2',An,Gn),('K2',Ak2,Gk2),
        ('K1',Ak1,Gk1),('O1',Ao1,Go1),('M4',Am4,Gm4),('MS4',Ams4,Gms4),
        ('NU2',0.100,Gn+20),('MU2',0.024,Gm+2),('P1',0.024,Gk1-15),('Q1',0.013,Go1)
    ]
    terms = []
    for (n,A,G) in cst:
        spd = SPEEDS.get(n,0)
        if not spd: continue
        f,u = nod.get(n,(1,0)); phi = V0.get(n,0)
        terms.append((f*A, spd*DEG, (phi+u-G)*DEG))
    return Z0, terms

def find_ext(terms, Z0, t_ref, typ):
    def h(t): return Z0+sum(fA*math.cos(spd*t+off) for fA,spd,off in terms)
    best_t=t_ref; best_h=h(t_ref)
    for dt in SEARCH_DT:
        tt=t_ref+dt; hv=h(tt)
        if typ=='PM' and hv>best_h: best_h=hv; best_t=tt
        if typ=='BM' and hv<best_h: best_h=hv; best_t=tt
    return best_t, best_h

def cost(params):
    sq=0; n=0
    prev_ds=None; Z0_c=None; terms_c=None
    for (ds,t_ref,typ,h_ref) in REF:
        if ds!=prev_ds:
            Z0_c,terms_c=make_terms(params,ds); prev_ds=ds
        best_t,best_h=find_ext(terms_c,Z0_c,t_ref,typ)
        dt_min=(best_t-t_ref)*60; dh=best_h-h_ref
        sq+=(30*dt_min)**2+(100*dh)**2
        n+=1
    return math.sqrt(sq/n)

def metrics(params):
    sq_t=0; sq_h=0; n=0
    prev_ds=None; Z0_c=None; terms_c=None
    for (ds,t_ref,typ,h_ref) in REF:
        if ds!=prev_ds:
            Z0_c,terms_c=make_terms(params,ds); prev_ds=ds
        best_t,best_h=find_ext(terms_c,Z0_c,t_ref,typ)
        sq_t+=(best_t-t_ref)**2*3600; sq_h+=(best_h-h_ref)**2; n+=1
    return math.sqrt(sq_t/n), math.sqrt(sq_h/n)

x0 = np.array([3.147,70.3,99.2,49.1,99.8,53.7,16.6,191.5,212.3,
               2.497,0.851,0.519,0.238,0.101,0.072,0.091,0.060])

et0,eh0 = metrics(x0)
print(f'Initial: t-RMSE={et0/60:.1f}min  h-RMSE={eh0:.3f}m')

call=[0]
def cb(xk):
    call[0]+=1
    if call[0]%300==0:
        et,eh=metrics(xk)
        print(f'  iter {call[0]:5d}: t={et/60:.1f}min h={eh:.3f}m  Gm={xk[1]:.1f} Gm4={xk[7]:.1f} Am={xk[9]:.3f} Z0={xk[0]:.3f}')
        sys.stdout.flush()

res=minimize(cost, x0, method='Nelder-Mead', callback=cb,
             options={'maxiter':80000,'xatol':1e-5,'fatol':1e-5,'adaptive':True})
xb=res.x

bounds=[
    (None,None),
    (None,None),(None,None),(None,None),(None,None),
    (None,None),(None,None),(None,None),(None,None),
    (0.5,3.5),(0.2,1.5),(0.1,1.0),(0.01,0.5),
    (0.01,0.3),(0.001,0.3),(0.001,0.3),(0.001,0.2),
]
res2=minimize(cost, xb, method='L-BFGS-B', bounds=bounds,
              options={'maxiter':2000,'ftol':1e-14,'gtol':1e-8})
if res2.fun < res.fun: xb=res2.x

et,eh=metrics(xb)
Z0,Gm,Gs,Gn,Gk2,Gk1,Go1,Gm4,Gms4,Am,As,An,Ak2,Ak1,Ao1,Am4,Ams4=xb
print(f'\nFINAL: t-RMSE={et/60:.1f}min  h-RMSE={eh:.3f}m')
print(f'Z0={Z0:.3f}  Gm={Gm:.1f} Am={Am:.3f}  Gs={Gs:.1f} As={As:.3f}')
print(f'Gn={Gn:.1f} An={An:.3f}  Gk1={Gk1:.1f} Ak1={Ak1:.3f}')
print(f'Go1={Go1:.1f} Ao1={Ao1:.3f}  Gk2={Gk2:.1f} Ak2={Ak2:.3f}')
print(f'Gm4={Gm4:.1f} Am4={Am4:.3f}  Gms4={Gms4:.1f} Ams4={Ams4:.3f}')

print('\nVerification:')
prev_ds=None; Z0_c=None; terms_c=None
for (ds,t_ref,typ,h_ref) in REF:
    if ds!=prev_ds:
        Z0_c,terms_c=make_terms(xb,ds); prev_ds=ds
    # fine search +-3h step 0.5min for display
    def hh(t,T=terms_c,Z=Z0_c): return Z+sum(fA*math.cos(spd*t+off) for fA,spd,off in T)
    best_t=t_ref; best_h=hh(t_ref)
    for i in range(-360,361):
        tt=t_ref+i/120.0; hv=hh(tt)
        if typ=='PM' and hv>best_h: best_h=hv; best_t=tt
        if typ=='BM' and hv<best_h: best_h=hv; best_t=tt
    dt=(best_t-t_ref)*60; dh=best_h-h_ref
    flag='OK' if abs(dt)<8 and abs(dh)<0.12 else '~~'
    tc=best_t+2; rh=int(tc); rm=int((tc%1)*60)
    ref_c=t_ref+2; rrh=int(ref_c); rrm=int((ref_c%1)*60)
    print(f'[{flag}] {ds} {typ} ref:{rrh:02d}h{rrm:02d}/{h_ref:.2f}m pred:{rh:02d}h{rm:02d}/{best_h:.2f}m dt={dt:+.0f}min dh={dh:+.2f}m')
