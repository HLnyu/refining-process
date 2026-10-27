import unittest, math, sqlite3
from pathlib import Path
import models as m
from scenario import simulate_lf

class PhysicalTests(unittest.TestCase):
    def test_gas_identity(self):self.assertAlmostEqual(m.gas_actual(1,273.15,101325,273.15,101325),1)
    def test_gas_expansion(self):self.assertAlmostEqual(m.gas_actual(1,546.3,50662.5,273.15,101325),4)
    def test_power_zero(self):self.assertEqual(m.gas_power(0,1873,101325,7000,3,100000,273.15,101325)['power_W'],0)
    def test_higbie_dimensions_scaling(self):self.assertAlmostEqual(m.higbie(4e-9,2)/m.higbie(1e-9,2),2)
    def test_twofilm_concentration_basis(self):
        km,ks,L,rm,rs=0.001,0.0001,100,7000,2800
        self.assertAlmostEqual(m.two_film(km,ks,L,rm,rs),1/(1/km+1/(ks*L*rs/rm)))
    def test_droplet_area(self):self.assertAlmostEqual(m.interface_area(0,1,0.001,0.001)['total_m2'],6)
    def test_sulfur_conservation(self):
        s=m.sulfur_two_phase(100000,1500,0.0002,0.001,100,0.001,600)
        self.assertAlmostEqual(100000*s['steel_fraction']+1500*s['slag_fraction'],21.5,places=11)
    def test_sulfur_no_rate(self):self.assertAlmostEqual(m.sulfur_two_phase(100000,1000,0.001,0.002,100,0,1000)['steel_fraction'],0.001)
    def test_sulfur_equilibrium_limit(self):
        s=m.sulfur_two_phase(100000,1000,0.0002,0.001,100,1,100)
        self.assertAlmostEqual(s['slag_fraction']/s['steel_fraction'],100)
    def test_sulfur_reverse_transfer(self):
        s=m.sulfur_two_phase(100000,1000,0.00001,0.02,100,0.001,100)
        self.assertGreater(s['steel_fraction'],0.00001)
    def test_inverse_sulfur(self):
        t=m.sulfur_time(100000,1500,0.0002,0.001,100,0.001,0.00012)
        self.assertAlmostEqual(m.sulfur_two_phase(100000,1500,0.0002,0.001,100,0.001,t)['steel_fraction'],0.00012)
    def test_unreachable(self):
        with self.assertRaises(ValueError):m.sulfur_time(100000,1500,0.0002,0.001,100,0.001,0)
    def test_identification(self):
        times=[0,10,30,60];cs=[5+100*math.exp(-0.02*t) for t in times]
        self.assertAlmostEqual(m.fit_rate(times,cs,5)['lambda_s_inv'],0.02)
    def test_rate_not_k_A(self):self.assertIn('not separately',m.fit_rate([0,1,2],[10,8,6],0)['identified'])
    def test_rh_conservation_no_reaction(self):
        s=m.rh_two_tank(90000,10000,1500,0,0,200,0,600)
        self.assertAlmostEqual(s['removed_kg'],0,places=9);self.assertAlmostEqual(s['mean_ppm'],180)
    def test_rh_no_circulation(self):
        s=m.rh_two_tank(90000,10000,0,0.01,0,200,200,100)
        self.assertEqual(s['ladle_ppm'],200);self.assertAlmostEqual(s['vessel_ppm'],200*math.exp(-1),places=4)
    def test_rh_oxygen_guard(self):
        with self.assertRaises(ValueError):m.rh_two_tank(90000,10000,1500,0.01,0,200,200,600,oxygen_available_ppm=1)
    def test_tracer_inverse(self):
        ml,mv,q,t=90000,10000,1500,10;eq=180;cl0=200
        cl=eq+(cl0-eq)*math.exp(-q*(1/ml+1/mv)*t)
        self.assertAlmostEqual(m.rh_tracer_circulation(cl,cl0,eq,ml,mv,t),q)
    def test_offgas_carbon(self):self.assertAlmostEqual(m.carbon_offgas([0.022414],[1],[1],[0],0.022414,1),0.012011)
    def test_offgas_fractions(self):
        with self.assertRaises(ValueError):m.carbon_offgas([1],[1],[0.8],[0.8],0.022414,1)
    def test_al_balance(self):
        r=m.aluminum_dose(100000,400,5,0,300,0,1)
        self.assertAlmostEqual(r['deoxidation_Al_kg'],44.4375);self.assertAlmostEqual(r['dose_kg'],74.4375)
    def test_alloy_exact_mass_balance(self):
        mass=m.alloy_single(100000,0.008,0.012,0.75,0.9)
        self.assertAlmostEqual((800+mass*0.75*0.9)/(100000+mass),0.012)
    def test_heat_balance(self):self.assertAlmostEqual(m.thermal_step(1600,100000,680,6800000,1,0,0,0,100),1610)
    def test_backwards(self):self.assertEqual(m.backward_temperature(1520,25,[15,25],[]),1585)
    def test_stokes_regime(self):
        self.assertGreater(m.stokes_rise(7000,4000,10e-6,0.006,3)['rise_time_s'],0)
        with self.assertRaises(ValueError):m.stokes_rise(7000,4000,0.001,0.006,3)
    def test_mixing_domain(self):
        with self.assertRaises(ValueError):m.mixing_2017(0.01,3,1.5,0.1,1e-5,7000,3000,0)
    def test_eye_out_of_domain(self):
        with self.assertRaises(ValueError):m.slag_eye_2017(20,3,0.1,1e-5,7000,3000,1.5,0.5)
    def test_bad_pressure(self):
        with self.assertRaises(ValueError):m.gas_actual(1,1873,0,273.15,101325)
    def test_sensitivity_not_confidence(self):self.assertIn('NOT_statistical',m.rate_sensitivity(100,0,0.01,0.02,10)['kind'])

class DatabaseTests(unittest.TestCase):
    def setUp(self):self.c=sqlite3.connect(Path(__file__).parent/'data/refining.sqlite')
    def tearDown(self):self.c.close()
    def test_integrity(self):self.assertEqual(self.c.execute('PRAGMA integrity_check').fetchone()[0],'ok')
    def test_foreign_keys(self):self.assertFalse(self.c.execute('PRAGMA foreign_key_check').fetchall())
    def test_no_fake_calibration(self):self.assertEqual(self.c.execute('SELECT count(*) FROM calibrations').fetchone()[0],0)
    def test_unknown_gas_preserved(self):
        self.assertEqual(self.c.execute("SELECT unit FROM observations WHERE case_id='S355H16' AND parameter='argon_volume'").fetchone()[0],'m3_unspecified')
    def test_historical_vintage(self):self.assertIn('2005',self.c.execute("SELECT original_data_vintage FROM sources WHERE source_id='S09'").fetchone()[0])
    def test_derived_gas(self):
        v=self.c.execute("SELECT value FROM observations WHERE case_id='VD105' AND parameter='argon_volume'").fetchone()[0]
        self.assertAlmostEqual(v,4.68)
    def test_case_source_agreement(self):
        self.assertEqual(self.c.execute('SELECT count(*) FROM observations o JOIN cases c USING(case_id) WHERE o.source_id<>c.source_id').fetchone()[0],0)
    def test_routes_equipment_valid(self):
        import json
        ids={r[0] for r in self.c.execute('SELECT equipment_id FROM equipment')}
        for r in self.c.execute('SELECT steps_json FROM routes'):self.assertTrue(set(json.loads(r[0]))<=ids)
    def test_quarantined_excluded(self):
        self.assertEqual(self.c.execute("SELECT count(*) FROM usable_reference_evidence WHERE evidence_tag='U'").fetchone()[0],0)
    def test_normalization_preserves_unknown_reference(self):
        row=self.c.execute("SELECT si_unit,reference_basis FROM normalized_evidence WHERE case_id='S355H16' AND parameter='argon_volume'").fetchone()
        self.assertEqual(row,('m3_unspecified','reference_state_unknown'))
    def test_normalization_wt_percent(self):
        row=self.c.execute("SELECT si_value FROM normalized_evidence WHERE case_id='CFDS2022' AND parameter='S_wt_pct'").fetchone()
        self.assertAlmostEqual(row[0],0.0165/100)

class IntegrationTests(unittest.TestCase):
    def test_cli_entrypoint(self):
        import subprocess,sys,json,os
        root=Path(__file__).parent
        proc=subprocess.run([sys.executable,str(root/'cli.py'),'stats'],cwd=root,capture_output=True,text=True,encoding='utf-8',env={**os.environ,'PYTHONIOENCODING':'utf-8'})
        self.assertEqual(proc.returncode,0,proc.stderr);self.assertGreater(json.loads(proc.stdout)['observations'],200)
    def test_composite_scenario(self):
        import json
        cfg=json.loads((Path(__file__).parent/'examples/lf_synthetic.json').read_text(encoding='utf-8'))
        r=simulate_lf(cfg)
        self.assertEqual(r['scenario_type'],'synthetic_scenario')
        self.assertAlmostEqual(r['trajectory'][-1]['mass_residual_kg'],0,places=9)
        self.assertAlmostEqual(r['total_normal_gas_m3'],50/6)
    def test_missing_closure_rejected(self):
        import json
        cfg=json.loads((Path(__file__).parent/'examples/lf_synthetic.json').read_text(encoding='utf-8'))
        del cfg['phases'][0]['interface_epsilon_factor']
        with self.assertRaises(KeyError):simulate_lf(cfg)

if __name__=='__main__':unittest.main()
