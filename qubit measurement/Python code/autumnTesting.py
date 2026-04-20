"""
Hi there this is my testing code to get a better idea of how the code works and
the system goes together.
"""

# Testing AWG output
# %% Imports
import matplotlib.pyplot as plt
import dataprocess as dp
import basicqubit as bq
import iqmixercal as iqcal
import libmeasurement as lm

# %% Setup basic qubit and change some parameters

path = "C:\\Users\\dvh-collab-user\\Desktop\\AutumnBau\\data\\"

# %% Setup the oscillators and whatnot
# Readout
bq.lo.set_fre(2, 6.1948)
bq.lo.set_power(2, 10)
bq.lo.lo_enable(2, 1)

# %% Drive
bq.lo.set_fre(1, 6.1948)
bq.lo.set_power(1, 10)
bq.lo.lo_enable(1, 1)

# %% Edit the default equipment buildout.
# Change AWG to slot 4 (i.e. AWG3)
bq.msys.awg_slot = 4

# %% Prepare program, this loads everything we are working on
bq.setup_io()
# %% HVI setup
bq.setup_hvi()
# %% Define the scan thingy
scan = lm.Scan(bq, path, 'tmp')
# %% load parameter
scan.datalog.load_parameters()
bq.reload_all()
# %% now the dynamic stuff...

bq.msys.finish_delay = 100000
bq.msys.delay_digitizer = 88000
bq.msys.din_points = 4000
bq.msys.din_cycles = 1000
bq.msys.istart = 1000
bq.msys.iend = 2500
bq.msys.reset_if()
bq.reload_all()

# %% Load waveforms

bq.load_waves(100, 100, 0, 90000,
              2000, 0.6, 1, phase=0)

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
scan.setscanfre(6.5, 0.01, 7.0)
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

# %%
bq.stop_all()
