"""Conditional LF multi-stage scenario. User-supplied closure required, no optimizer."""
import models as m

def simulate_lf(config):
    """All phases are sequential; simultaneous heating/gassing share phase duration.

    This only couples piecewise-constant Lw/K/A sulfur and sensible heat. It does
    NOT solve Al-O thermodynamics, inclusion populations or complete gas chemistry.
    """
    if config.get('scenario_type') not in ('synthetic_scenario','conditional_user_scenario'):
        raise ValueError('Scenario type must explicitly state conditional or synthetic')
    if not config.get('provenance'):raise ValueError('Scenario input provenance required')
    s=config['state'];par=config['parameters']
    M=s['steel_mass_kg'];Ms=s['slag_mass_kg'];rho=par['steel_density_kg_m3'];rs=par['slag_density_kg_m3']
    m.positive(M=M,Ms=Ms,rho=rho,rs=rs)
    wm=s['S_steel_fraction'];ws=s['S_slag_fraction'];T=s['T_degC'];records=[];gas=0;time=0
    for phase in config['phases']:
        dt=phase['duration_s'];q=phase['QN_m3_s'];p=phase['surface_pressure_Pa']
        m.positive(dt=dt);m.nonnegative(q=q)
        power=m.gas_power(q,T+273.15,p,rho,par['bath_depth_m'],M,par['normal_temperature_K'],par['normal_pressure_Pa'])
        m.nonnegative(epsilon_factor=phase['interface_epsilon_factor'])
        eps=power['mean_W_kg']*phase['interface_epsilon_factor']
        km=m.eddy_transfer(par['diffusivity_steel_m2_s'],eps,par['nu_steel_m2_s'],phase['eddy_C'])
        # zero Q implies zero modeled turbulent mass transfer; no hidden molecular default.
        if km==0:keff=0.0
        else:keff=m.two_film(km,phase['ks_m_s'],phase['Lw'],rho,rs)
        area=m.interface_area(phase['A_resolved_m2'],phase['area_effectiveness'],phase['drop_volume_m3'],phase['drop_d32_m'])
        gamma=m.combine_conductance([{'k_m_s':keff,'A_m2':area['total_m2']}],M/rho)['gamma_s_inv']
        sulfur=m.sulfur_two_phase(M,Ms,wm,ws,phase['Lw'],gamma,dt)
        wm,ws=sulfur['steel_fraction'],sulfur['slag_fraction']
        T=m.thermal_step(T,M,par['cp_J_kg_K'],phase['electric_power_W'],phase['electrical_efficiency'],phase['reaction_heat_W'],phase['heat_loss_W'],phase['addition_heat_J'],dt)
        gas+=q*dt;time+=dt
        records.append({'phase':phase['name'],'elapsed_s':time,'S_steel_ppm':wm*1e6,'S_slag_fraction':ws,'T_degC':T,'km_m_s':km,'Keff_m_s':keff,'A_m2':area['total_m2'],'gamma_s_inv':gamma,'gas_power_W':power['power_W'],'mass_residual_kg':sulfur['mass_residual_kg']})
    return {'scenario_type':config['scenario_type'],'status':'conditional_unvalidated_scenario','provenance':config['provenance'],
        'source_ids':['S02','S03','S04','S19'],'model_ids':['M02','M04','M05','M06','M07','M18'],
        'trajectory':records,'total_normal_gas_m3':gas,'duration_s':time,
        'not_predicted':['dissolved oxygen endpoint','total oxygen','independent A(Q)','RH circulation from Q alone','product certification'],
        'assumptions':['constant metal/slag mass within scenario','piecewise constant Lw, local epsilon factor, interface geometry and physical properties','no reoxidation/resulfurization sources beyond two-phase exchange','no automatic plant calibration']}
