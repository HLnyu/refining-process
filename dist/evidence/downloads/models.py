"""SI calculation kernel. No hidden empirical constants or inferred plant calibration.

All functions are research calculations. Concentrations use fractions or ppm as named.
Source and derivation for each callable are in registry.py and generated docs.
"""
import math
from statistics import fmean
R=8.31446261815324
G=9.80665

def positive(**values):
    for name,v in values.items():
        if not math.isfinite(v) or v<=0:raise ValueError(f'{name} must be finite and positive')

def nonnegative(**values):
    for name,v in values.items():
        if not math.isfinite(v) or v<0:raise ValueError(f'{name} must be finite and nonnegative')

def fraction(**values):
    for name,v in values.items():
        if not math.isfinite(v) or not 0<=v<=1:raise ValueError(f'{name} must lie in [0,1]')

def gas_actual(QN_m3_s,T_K,p_abs_Pa,TN_K,pN_Pa):
    nonnegative(QN=QN_m3_s);positive(T=T_K,p=p_abs_Pa,TN=TN_K,pN=pN_Pa)
    return QN_m3_s*T_K/TN_K*pN_Pa/p_abs_Pa

def gas_power(QN_m3_s,T_K,p_surface_Pa,rho,H,M,TN,pN):
    nonnegative(QN=QN_m3_s,H=H);positive(T=T_K,p=p_surface_Pa,rho=rho,M=M,TN=TN,pN=pN)
    mol_s=pN*QN_m3_s/(R*TN)
    power=mol_s*R*T_K*math.log1p(rho*G*H/p_surface_Pa)
    return {'power_W':power,'mean_W_kg':power/M,'definition':'ideal_isothermal_expansion_not_local_epsilon','model_id':'M02'}

def higbie(D_m2_s,contact_s):
    positive(D=D_m2_s,contact=contact_s)
    return 2*math.sqrt(D_m2_s/(math.pi*contact_s))

def eddy_transfer(D_m2_s,eps_local_W_kg,nu_m2_s,C):
    positive(D=D_m2_s,nu=nu_m2_s,C=C);nonnegative(eps=eps_local_W_kg)
    return C*math.sqrt(D_m2_s)*(eps_local_W_kg/nu_m2_s)**0.25

def two_film(km,ks,Lw,rho_m,rho_s):
    positive(km=km,ks=ks,Lw=Lw,rho_m=rho_m,rho_s=rho_s)
    return 1/(1/km+rho_m/(rho_s*ks*Lw))

def interface_area(A_resolved,effectiveness,V_drop,d32):
    nonnegative(A=A_resolved,V=V_drop);fraction(effectiveness=effectiveness)
    if V_drop:
        positive(d32=d32);drop=6*V_drop/d32
    else:drop=0
    return {'bulk_effective_m2':effectiveness*A_resolved,'drop_m2':drop,
        'total_m2':effectiveness*A_resolved+drop,'model_id':'M06',
        'note':'drop size/volume and bulk resolved area are required inputs, not predictions from Q'}

def combine_conductance(zones,Vm):
    positive(Vm=Vm);conductance=0
    for z in zones:
        nonnegative(k=z['k_m_s'],A=z['A_m2']);conductance+=z['k_m_s']*z['A_m2']
    return {'G_m3_s':conductance,'gamma_s_inv':conductance/Vm,'model_id':'M06'}

def sulfur_two_phase(Mm_kg,Ms_kg,wm0,ws0,Lw,gamma_s_inv,t_s):
    positive(Mm=Mm_kg,Ms=Ms_kg,Lw=Lw);fraction(wm=wm0,ws=ws0)
    nonnegative(gamma=gamma_s_inv,t=t_s)
    total=Mm_kg*wm0+Ms_kg*ws0
    eq=total/(Mm_kg+Ms_kg*Lw)
    lam=gamma_s_inv*(1+Mm_kg/(Ms_kg*Lw))
    wm=eq+(wm0-eq)*math.exp(-lam*t_s)
    ws=(total-Mm_kg*wm)/Ms_kg
    if ws>1+1e-10:raise ValueError('Constant-partition assumptions yield impossible slag fraction')
    return {'steel_fraction':wm,'slag_fraction':ws,'steel_equilibrium_fraction':eq,
        'lambda_s_inv':lam,'mass_residual_kg':Mm_kg*wm+Ms_kg*ws-total,'model_id':'M07'}

def sulfur_time(Mm_kg,Ms_kg,wm0,ws0,Lw,gamma_s_inv,target_fraction):
    s=sulfur_two_phase(Mm_kg,Ms_kg,wm0,ws0,Lw,gamma_s_inv,0)
    fraction(target=target_fraction)
    eq=s['steel_equilibrium_fraction']
    if target_fraction>=wm0:return 0.0
    if gamma_s_inv==0 or target_fraction<=eq:raise ValueError('Target not reachable in finite time under specified equilibrium and rate')
    return -math.log((target_fraction-eq)/(wm0-eq))/s['lambda_s_inv']

def fit_rate(time_s,concentration,Ceq):
    if len(time_s)!=len(concentration) or len(time_s)<3:raise ValueError('Need >=3 matched time/concentration samples')
    if not all(math.isfinite(x) for x in [*time_s,*concentration,Ceq]):raise ValueError('Nonfinite sample')
    if any(time_s[i+1]<=time_s[i] for i in range(len(time_s)-1)):raise ValueError('Times must increase')
    delta=[c-Ceq for c in concentration]
    if not all(d>0 for d in delta):raise ValueError('Concentrations must exceed specified equilibrium')
    ys=[math.log(d/delta[0]) for d in delta];xs=[t-time_s[0] for t in time_s]
    xm,ym=fmean(xs),fmean(ys)
    slope=sum((x-xm)*(y-ym) for x,y in zip(xs,ys))/sum((x-xm)**2 for x in xs)
    if slope>=0:raise ValueError('No positive removal rate identified')
    intercept=ym-slope*xm
    residual=sum((y-intercept-slope*x)**2 for x,y in zip(xs,ys))
    return {'lambda_s_inv':-slope,'intercept':intercept,'log_residual_sum_squares':residual,
        'identified':'lumped lambda only; k and A not separately identifiable','model_id':'M08'}

def mixing_relative(tau_ref_s,Q,Q_ref):
    positive(tau_ref=tau_ref_s,Q=Q,Q_ref=Q_ref)
    return tau_ref_s*(Q/Q_ref)**(-1/3)

def mixing_2017(Q_actual_m3_s,L,Rv,slag_h,nu_s,rho_l,rho_s,plug_r_over_R):
    positive(Q=Q_actual_m3_s,L=L,R=Rv,slag_h=slag_h,nu_s=nu_s,rho_l=rho_l,rho_s=rho_s)
    if abs(plug_r_over_R-0.5)>1e-8:raise ValueError('S01 Eq7 requires single plug at 0.5R')
    if rho_s>=rho_l:raise ValueError('Buoyant upper phase required')
    if not 0.01<=slag_h/L<=0.10:raise ValueError('Slag-depth ratio outside source optimization envelope')
    if not 0.75<=L/(2*Rv)<=1.35:raise ValueError('Aspect ratio outside source envelope')
    # Source dimensionless Eq7; Q is hot-gas flow at mean bath pressure, NOT QN.
    tau=222*(Q_actual_m3_s**2/(G*Rv**5))**0.33*(L/Rv)**-1*(slag_h/Rv)**0.3*(nu_s**2/(G*Rv**3))**0.016*((rho_l-rho_s)/rho_l)**-0.044*Rv**3/Q_actual_m3_s
    return {'tau95_s':tau,'model_id':'M25','status':'published_correlation_not_plant_validated_here','warning':'Source water-model scaling; geometry, gas-inertial regime and physical similarity still need verification'}

def slag_eye_2017(U_plume,L,slag_h,nu_s,rho_l,rho_s,Rv,plug_r_over_R):
    positive(U=U_plume,L=L,h=slag_h,nu_s=nu_s,rho_l=rho_l,rho_s=rho_s,R=Rv)
    if rho_s>=rho_l:raise ValueError('Upper phase must be lighter')
    if abs(plug_r_over_R-0.5)>1e-8:raise ValueError('S01 mid-radius correlation only')
    a=2.67*(U_plume**2/(G*slag_h))**1.28*(nu_s/(slag_h*U_plume))**-0.05*(rho_l/(rho_l-rho_s))**0.55*L*slag_h
    if a>math.pi*Rv**2:raise ValueError('Predicted eye exceeds bath area: correlation outside valid regime; not silently clipped')
    return {'eye_m2':a,'flat_contact_m2':math.pi*Rv**2-a,'model_id':'M26',
        'note':'Eye rim distorted area and droplets not included; Uplume must be independently supplied'}

def rh_lift_circulation(Ad_m2,rho,H_m,alpha_up,alpha_down,Kloss):
    positive(A=Ad_m2,rho=rho,H=H_m,Kloss=Kloss);fraction(up=alpha_up,down=alpha_down)
    if alpha_up<alpha_down:raise ValueError('Up-leg gas hold-up must not be below down-leg')
    return Ad_m2*rho*math.sqrt(2*G*H_m*(alpha_up-alpha_down)/Kloss)

def rh_tracer_circulation(Cl,Cl0,Ceq,Ml,Mv,t):
    positive(Ml=Ml,Mv=Mv,t=t)
    if Cl0==Ceq:raise ValueError('No initial tracer contrast')
    ratio=(Cl-Ceq)/(Cl0-Ceq)
    if not 0<ratio<1:raise ValueError('Tracer point must be between initial and equilibrium')
    return -math.log(ratio)/(t*(1/Ml+1/Mv))

def rh_two_tank(Ml,Mv,q,kv,Cstar,Cl0,Cv0,t,oxygen_available_ppm=None):
    positive(Ml=Ml,Mv=Mv);nonnegative(q=q,kv=kv,Cstar=Cstar,Cl0=Cl0,Cv0=Cv0,t=t)
    a,b=q/Ml,q/Mv
    rate=max(a,b+kv)
    n=max(1,math.ceil(t*rate/0.02))
    if n>200000:raise ValueError('Stiff/long scenario; use a dedicated solver')
    dt=t/n;cl,cv=Cl0,Cv0
    def f(l,v):return a*(v-l),b*(l-v)-kv*(v-Cstar)
    for _ in range(n):
        k1=f(cl,cv);k2=f(cl+dt*k1[0]/2,cv+dt*k1[1]/2);k3=f(cl+dt*k2[0]/2,cv+dt*k2[1]/2);k4=f(cl+dt*k3[0],cv+dt*k3[1])
        cl+=dt*(k1[0]+2*k2[0]+2*k3[0]+k4[0])/6
        cv+=dt*(k1[1]+2*k2[1]+2*k3[1]+k4[1])/6
    removed=(Ml*Cl0+Mv*Cv0-Ml*cl-Mv*cv)*1e-6
    o_required=removed*16/12
    if oxygen_available_ppm is not None:
        nonnegative(O_available=oxygen_available_ppm)
        if o_required>(Ml+Mv)*oxygen_available_ppm*1e-6+1e-9:
            raise ValueError('Carbon removal exceeds oxygen budget for CO; supply/coupled oxygen model required')
    return {'ladle_ppm':cl,'vessel_ppm':cv,'mean_ppm':(Ml*cl+Mv*cv)/(Ml+Mv),
        'removed_kg':removed,'O_required_kg_if_C_to_CO':o_required,'steps':n,'model_id':'M12',
        'status':'conditional_scenario_not_calibrated_prediction'}

def carbon_offgas(QNdry_m3_s,dt_s,yCO,yCO2,VmN_m3_mol,correction):
    arrays=[QNdry_m3_s,dt_s,yCO,yCO2]
    if len({len(a) for a in arrays})!=1 or not len(dt_s):raise ValueError('Need equal nonempty arrays')
    positive(VmN=VmN_m3_mol,correction=correction)
    total=0
    for q,dt,co,co2 in zip(*arrays):
        nonnegative(Q=q,dt=dt);fraction(CO=co,CO2=co2)
        if co+co2>1+1e-12:raise ValueError('Dry fractions exceed 1')
        total+=q*dt/VmN_m3_mol*(co+co2)*0.012011*correction
    return total

def hydrogen(KH_ppm,pH2,p0,H0,gammaH,t):
    positive(KH=KH_ppm,p0=p0);nonnegative(pH2=pH2,H0=H0,gamma=gammaH,t=t)
    eq=KH_ppm*math.sqrt(pH2/p0)
    return {'H_eq_ppm':eq,'H_ppm':eq+(H0-eq)*math.exp(-gammaH*t),'model_id':'M14'}

def aluminum_dose(M,O0_ppm,Of_ppm,Al0_ppm,Alf_ppm,loss_kg,purity):
    positive(M=M,purity=purity);fraction(purity=purity)
    nonnegative(O0=O0_ppm,Of=Of_ppm,Al0=Al0_ppm,Alf=Alf_ppm,loss=loss_kg)
    if Of_ppm>O0_ppm or Alf_ppm<Al0_ppm:raise ValueError('This function only handles oxygen removal and Al enrichment')
    deox=M*(O0_ppm-Of_ppm)*1e-6*54/48;retained=M*(Alf_ppm-Al0_ppm)*1e-6
    return {'dose_kg':(deox+retained+loss_kg)/purity,'deoxidation_Al_kg':deox,'retained_Al_kg':retained,
        'loss_Al_kg':loss_kg,'model_id':'M15','not_predicted':'total oxygen endpoint and inclusion removal'}

def alloy_single(M,w0,wt,alloy_x,eta):
    positive(M=M);fraction(w0=w0,wt=wt,x=alloy_x,eta=eta)
    if wt<w0:raise ValueError('Cannot remove an element by adding an enriching alloy')
    if wt==w0:return 0.0
    den=alloy_x*eta-wt
    if den<=0:raise ValueError('Target not reachable with this alloy and recovery')
    return M*(wt-w0)/den

def thermal_step(T,M,cp,P,eta,Qrxn,Qloss,Qaddition,dt):
    positive(M=M,cp=cp);fraction(eta=eta);nonnegative(P=P,Qloss=Qloss,Qaddition=Qaddition,dt=dt)
    if not all(math.isfinite(x) for x in [T,Qrxn]):raise ValueError('Nonfinite temperature or reaction heat')
    return T+((eta*P+Qrxn-Qloss)*dt-Qaddition)/(M*cp)

def backward_temperature(TL,superheat,losses,heating):
    nonnegative(superheat=superheat)
    for x in losses+heating:nonnegative(delta=x)
    return TL+superheat+sum(losses)-sum(heating)

def stokes_rise(rho_m,rho_p,d,mu,H):
    positive(rho_m=rho_m,rho_p=rho_p,d=d,mu=mu,H=H)
    if rho_p>=rho_m:raise ValueError('Particle does not float')
    u=(rho_m-rho_p)*G*d*d/(18*mu);re=rho_m*u*d/mu
    if re>=0.1:raise ValueError('Stokes estimate outside conservative Re<0.1 domain')
    return {'velocity_m_s':u,'rise_time_s':H/u,'Re':re,'model_id':'M20'}

def rate_sensitivity(C0,Ceq,gamma_low,gamma_high,t):
    nonnegative(gamma_low=gamma_low,gamma_high=gamma_high,t=t)
    if gamma_low>gamma_high or C0<Ceq:raise ValueError('Invalid interval')
    return {'lower':Ceq+(C0-Ceq)*math.exp(-gamma_high*t),
        'upper':Ceq+(C0-Ceq)*math.exp(-gamma_low*t),
        'kind':'parameter_sensitivity_envelope_NOT_statistical_prediction_interval'}
