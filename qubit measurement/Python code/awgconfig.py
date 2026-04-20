# %%  Import modules
import keysightSD1 as Sd1
import lib.libwaveform as lw

# %% Set channel, amplitude (vpp?) and slot
ch = 1
amp = .5

# %% Open the AWG
awg = Sd1.SD_AOU()
awgid = awg.openWithSlot("", 1, 4)
if awgid < 0:
    print("AWG open error:", awgid)
else:
    print("AWG Module opened:", awgid)
    print("Module name:", awg.getProductName())
    print("slot:", awg.getSlot())
    print("Chassis:", awg.getChassis())

#%% Stop the AWG
awg.AWGstop(1)

#%% empty waveform queue
awg.AWGflush(ch)

#%% Empty stored waveforms
awg.waveformFlush()

# %% Set AWG output
# ENABLE AWG OUT
#Sd1.SD_Waveshapes, AOU_AWG, AOU_SINUSOIDAL,AOU_TRIANGULAR,AOU_SQUARE,AOU_DC,AOU_AWG, AOU_PARTNER
# the partner channel may be useful for doing IQ pulses
awg.channelWaveShape(ch, Sd1.SD_Waveshapes.AOU_AWG)
awg.channelAmplitude(ch, amp) # Amp in volts

# %% set FG output
#Sd1.SD_Waveshapes, AOU_AWG, AOU_SINUSOIDAL,AOU_TRIANGULAR,AOU_SQUARE,AOU_DC,AOU_AWG, AOU_PARTNER
# the partner channel may be useful for doing IQ pulses
awg.channelWaveShape(ch, Sd1.SD_Waveshapes.AOU_SINUSOIDAL)
awg.channelAmplitude(ch, amp) # Amp in volts
awg.channelFrequency(ch, 1.5e7)
awg.channelOffset(ch, 0)
awg.AWGqueueConfig(ch, 1)


# %% Start
awg.AWGstart(ch)

#%% Prepare the waveform to be loaded
# Hard pulse,
wfd = lw.dc_waveform(100, 1000, 10, 0, 1, 0)

# %% Gauss waveform
# Gaussian waveform
wfg40 = lw.g_waveform(500,1000, 40,100,0,1,0)
wfg20 = lw.g_waveform(500,1000, 20,100,0,1,0)


#%% Waveform Object
# Prepare the Wave object.
gwave40 = Sd1.SD_Wave()
gwave20 = Sd1.SD_Wave()
# WaveformType 0 is 16 bit analog waveform
gID40 = gwave40.newFromArrayDouble(0, wfg40)
gID20 = gwave20.newFromArrayDouble(0, wfg20)
print(gID40, gID20)
#%% Waveform Object
# Prepare the Wave object.
dwave = Sd1.SD_Wave()
# WaveformType 0 is 16 bit analog waveform
dID=dwave.newFromArrayDouble(0, wfd)
print(dID)
# %% Set the trigger to output a signal

awg.triggerIOconfig(0)
#awg.triggerIOwrite(0,1)
# PXImask is just zero and to enable marker out on the front panel the LSB needs to be set to 1
awg.AWGqueueMarkerConfig(2,3,0,0b01,1,0,50,0)

#%% Load waves to the output
awg.AWGstop(ch)
awg.waveformFlush()
awg.AWGflush(ch)
awg.waveformLoad(gwave20, 0)
awg.waveformLoad(gwave40, 1)

# %% Queue waves and output
# Set the output to free run when
awg.AWGqueueWaveform(2, 0, 0, 0, 0, 0)  # ic, iw, HVI trigger, delay, cycle, prescaler
#awg.AWGqueueWaveform(2, 0, 0,0,10,0)
# this sets the AWG trigger mode, 0 for automatically running, 1 for software trigger,
#awg.AWGqueueConfig(1, 1)  # queue repeat in cyclic mode
awg.AWGqueueConfig(2,1)
#awg.AWGqueueSyncMode(1, 0)  # sync to CLKSYS
awg.AWGqueueSyncMode(2,0)
awg.AWGstart(2)


  #%% STOP
awg.AWGstopMultiple(0b1111)

#%% Flush queue
awg.AWGflush(1)
awg.AWGflush(2)
#%%
awg.waveformFlush()
#%% Close AWG
awg.close()
