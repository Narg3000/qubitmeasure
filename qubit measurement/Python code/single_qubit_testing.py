# measurements
# %% import library
import matplotlib.pyplot as plt
import dataprocess as dp
import basicqubit as bq
import iqmixercal as iqcal
import libmeasurement as lm

# %%
path = 'C:\\Users\\dvh-collab-user\\Desktop\\AutumnBau\\data\\'
# %% setup LO qubit channel
bq.lo.set_fre(1, 7)
bq.lo.set_power(1, 10)
bq.lo.lo_enable(1, 1)
# %% cavity channel
bq.lo.set_fre(2, 6.1948)
bq.lo.set_power(2, 10)
bq.lo.lo_enable(2, 1)
# %% prepare measurement program
bq.setup_io()
# %%
bq.setup_hvi()
# %%
bq.stop_all()
# %%
scan = lm.Scan(bq, path, 'tmp')
# %% load parameter
scan.datalog.load_parameters()
bq.reload_all()
# %% IQ mixer calibration readout mixer
stat = iqcal.CalState(bq, 'readout', 0.6, True)
# %% HVI pulse mode
stat.__init__(bq, 'readout', 0.6, False)
# %% cal qubit mixer
stat.__init__(bq, 'qubit', 0.6, True)
# %% HVI pulse
stat.__init__(bq, 'qubit', 0.6, False)
# %% update part of parameters to default
bq.msys.finish_delay = 100000
bq.msys.delay_digitizer = 88000
bq.msys.din_points = 4000
bq.msys.din_cycles = 1000
bq.msys.istart = 1000
bq.msys.iend = 2500
bq.msys.reset_if()
bq.reload_all()
# %% load pulse
bq.load_waves(100, 100, 0, 90000, 2000, 0.6, 1)
# %% parameter for IQ mixer cal pulse mode.
bq.msys.finish_delay = 11000
bq.reload_all()
# %% test daq readout
bq.one_run()
avg = dp.listavg(bq.msys.dataset, bq.msys.din_factor)
plt.plot(avg)
# %% save parameters
scan.datalog.save_parameters()
# %% load parameter
scan.datalog.load_parameters()
# %% test readout signal
scan.name = '-test_readout'
scan.d_delay = 100
scan.d_length = 100
scan.d_amp = 0
scan.r_delay = 90000
scan.r_length = 2000
scan.r_amp = 0.05
bq.msys.istart = 1000
bq.msys.iend = 2500
scan.test_readout(100000)
# %% measure cavity
bq.lo.set_fre(1,7.85)
bq.lo.lo_enable(1,1)
scan.name = '-cavity'
scan.setscanfre(6.5, 0.001, 7.0)
scan.r_delay = 90000
scan.r_length = 2000
scan.r_amp = 0.05
scan.d_delay = 100
scan.d_length = 100
scan.d_amp = 0
scan.loch = 2
scan.scanlo()
plt.plot(scan.fre, scan.datamag)
# %% scan S21 vs power
scan.name = '-cavity_power'
scan.r_delay = 90000
scan.r_length = 2000
scan.loch = 2
scan.setscanfre(7.8, 0.005, 8.0)
scan.setpowerrange(0.8, 0.1, 1.4)
scan.cavity_power()
# %% run search qubit fre
scan.name = '-qubit-search'
scan.r_amp = 0.05
scan.d_amp = 0.2
scan.setscanfre(400, 0.01, 430)
scan.ifch = 'drive'
scan.d_delay = 80000
scan.d_length = 10000
scan.r_delay = 90000
scan.r_length = 2000
scan.scanif(comm='search for qubit fre.')
bq.msys.reset_if()
# %% power Rabi, search for Pi pulse

# %% measure Rabi oscillation: vary drive pulse length
# bq.msys.din_cycles = 15000
# bq.reload_all()
scan.name = '-time_rabi'
scan.r_amp = 0.05
scan.d_amp = 0.2
scan.r_delay = 90000
scan.r_length = 2000
scan.time_rabi(10, 20, 50000, 90000)
# %% measure T1, vary t between Pi pulse and readout
scan.name = '-t1'
scan.r_amp = 0.1
scan.d_amp = 0.3
scan.r_delay = 90000
scan.r_length = 2000
scan.t1(10, 100, 10010, 302)
# %% measure T2, vary t between two Pi/2 pulse
scan.name = '-t2'
pulse_gen = bq.PulseControl(bq.msys)
pulse_gen.unit_delay = 100
pulse_gen.pi_length = 335
pulse_gen.readout_delay = 90000
pulse_gen.readout_length = 2000
pulse_gen.drive_amp = 0.3
pulse_gen.readout_amp = 0.1
scan.t2(10, 20, 5000, pulse_gen)
# %% test
pulse_gen = bq.PulseControl(bq.msys)
pulse_gen.unit_delay = 100
pulse_gen.pi_length = 269
pulse_gen.readout_delay = 90000
pulse_gen.readout_length = 2000
pulse_gen.drive_amp = 0.3
pulse_gen.readout_amp = 0
pulse_gen.drive_delay = 90000
pulse_gen.t2_m = 150
pulse_gen.setup_t2_pulses()
# %%
bq.one_run()
avg = dp.listavg(bq.msys.dataset, bq.msys.din_factor)
plt.plot(avg)
