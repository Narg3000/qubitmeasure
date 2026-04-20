"""
Created on 12/24/2022

@author: Guang Yue
Based on spect_demo.py this file contains codes for setting up AWG and DIN, reload waveform
spectroscopy, Pulse calibration, Rabi, T1 T2 measurement.
"""
# lib import
# parameters for the measurement
# choose awg ch1 and ch2 for IQ of qubit pulse, ch3 and ch4 for IQ of cavity readout pulse
# Parameters.py for the above
import Parameters
import numpy as np
import keysightmeasure as km
import libwaveform as lw
import m9347a_lo as lo


class IQPulse:
    def __init__(self):
        self.delay_unit_time = 100  # ns
        self.delay = 100  # ns
        self.duration = 1000  # ns
        self.awg_ch = 1
        self.awg_range = 1  # the amplitude of the awg output, not the waveform Vp
        self.pulse_amp = 0.6  # Vp of pulse
        self.offset = 0
        self.phase = 0
        self.awg_trig = 1  # trigger of the awg channel
        self.delay_wave_id = 0
        self.pulse_wave_id = 0
        self.fre = 50
        self.wave_type = 'one_rect_pulse'

    def set_parameter(self, d_u, delay, duration, ch, awg_range, amp, offset, phase, trig):
        self.delay_unit_time = d_u
        self.delay = delay
        self.duration = duration
        self.awg_ch = ch
        self.awg_range = awg_range
        self.pulse_amp = amp
        self.awg_trig = trig
        self.offset = offset
        self.phase = phase


msys = Parameters.MSys()
msys.drive_i = IQPulse()
msys.drive_q = IQPulse()
msys.readout_i = IQPulse()
msys.readout_q = IQPulse()


# prepare awg and din
def setup_io():
    # open awg
    awg1 = km.open_awg(msys.chassis, msys.awg_slot)
    # prepare DIN
    din = km.open_din(msys.chassis, msys.din_slot)
    km.din_setup(din, msys.din_ch, msys.din_scale, msys.din_points, msys.din_cycles)
    msys.din = din
    msys.awg = awg1
    print('done open io and load delay waveforms 0-4')


# load waveforms for single channel
def load_one_ch(pulse):
    wf = lw.zero_waveform(pulse.delay_unit_time, pulse.offset / pulse.awg_range)
    km.load_wave_awg(msys.awg, wf, msys.awg_next_id)
    pulse.delay_wave_id = msys.awg_next_id
    msys.awg_next_id += 1
    wd = pulse.delay % pulse.delay_unit_time
    wf = lw.dc_waveform(wd, pulse.duration + wd, pulse.fre, np.pi / 2 * pulse.phase / 90.0,
                        pulse.pulse_amp / pulse.awg_range, pulse.offset / pulse.awg_range)
    km.load_wave_awg(msys.awg, wf, msys.awg_next_id)
    pulse.pulse_wave_id = msys.awg_next_id
    msys.awg_next_id += 1
    km.queue_delay_pulse(msys.awg, pulse)


# load delay waveforms and IQ waveform for drive and readout using AWG
def load_waves(d_delay, d_length, d_amp, r_delay, r_length, r_amp, trig, phase: float = None):
    if phase is None:
        phase = msys.cavity_mixer.phase
    msys.awg.waveformFlush()
    msys.awg_next_id = 0
    # AWG can only handle no less than 5 points. delay has to be bigger than 100ns
    msys.drive_i.set_parameter(100, d_delay, d_length, 1, msys.awg_qrange, d_amp, msys.qubit_mixer.i_offset, 0, trig)
    msys.drive_q.set_parameter(100, d_delay, d_length, 2, msys.awg_qrange, d_amp * msys.qubit_mixer.q_ratio,
                               msys.qubit_mixer.q_offset, phase, trig)
    msys.readout_i.set_parameter(100, r_delay, r_length, 3, msys.awg_crange, r_amp, msys.cavity_mixer.i_offset, 0, trig)
    msys.readout_q.set_parameter(100, r_delay, r_length, 4, msys.awg_crange, r_amp * msys.cavity_mixer.q_ratio,
                                 msys.cavity_mixer.q_offset, phase, trig)
    load_one_ch(msys.drive_i)
    load_one_ch(msys.drive_q)
    load_one_ch(msys.readout_i)
    load_one_ch(msys.readout_q)


# load only drive waves or readout waves
def load_drive(delay, length, amp, trig):
    load_waves(delay, length, amp, 100, 1000, 0, trig)


def load_readout(delay, length, amp, trig):
    load_waves(100, 1000, 0, delay, length, amp, trig)


# define HVI system and code
# setup HVI
def setup_hvi():
    # run HVI
    km.hvi_spectroscopy_code(msys)
    msys.hvi.load_to_hw()
    msys.hvi.run(msys.hvi.no_wait)
    msys.hvi.sync_sequence.scopes[msys.awg_eng].registers['max_cycle'].write(msys.din_cycles)
    msys.hvi.sync_sequence.scopes[msys.awg_eng].registers['finish_delay'].write(round(msys.finish_delay/10))
    msys.hvi.sync_sequence.scopes[msys.din_eng].registers['din_delay'].write(round(msys.delay_digitizer/10))
    print('Done load hvi code')


# run hvi process once and get the data
def one_run():
    msys.din.DAQstart(msys.din_ch)
    msys.hvi.sync_sequence.scopes[msys.awg_eng].registers['hvi_status'].write(1)  # start measurement
    # get data
    dataset = []
    for x in range(msys.din_cycles):
        data = msys.din.DAQread(msys.din_ch, msys.din_points, 1000)
        dataset.append(data)
    # print('data saved')
    msys.dataset = dataset


# Keep running awg without DIN
def test_awg():
    msys.hvi.sync_sequence.scopes[msys.awg_eng].registers['hvi_status'].write(3)


def pause():
    msys.hvi.sync_sequence.scopes[msys.awg_eng].registers['hvi_status'].write(0)


# stop hvi program and release hw
def stop_hvi():
    # input('press any key to stop program')
    msys.hvi.sync_sequence.scopes[msys.awg_eng].registers['hvi_status'].write(2)  # stop HVI program
    msys.hvi.release_hw()


# Stop all awg and din, close connection
def stop_measurement():
    km.awg_stop_all(msys.awg)
    km.din_stop_all(msys.din)
    msys.awg.close()
    msys.din.close()


def stop_all():
    stop_hvi()
    stop_measurement()


def reload_all():
    stop_all()
    setup_io()
    setup_hvi()


def test_pulses():
    while msys.hvi.sync_sequence.scopes['awg1Engine'].registers['hvi_status'].read() == 0:
        msys.hvi.sync_sequence.scopes['awg1Engine'].registers['hvi_status'].write(1)  # start measurement


# class for t2 pulse
class T2Pulse(IQPulse):
    def __init__(self):
        super().__init__()
        self.wave_type = 't2_rect_pulses'
        # special parameters for T2 measurement
        self.t_m = 10  # time between the Pi/2 pulse
        self.t_p2 = 500  # pulse length for Pi/2


# this class control pulses loading/reloading for AWG beside basic method.
class PulseControl:
    def __init__(self, msys):
        self.drive_i = None
        self.drive_q = None
        self.readout_i = None
        self.readout_q = None
        self.msys = msys
        self.unit_delay = 100  # AWG can only handle no less than 5 points. delay has to be bigger than 100ns
        self.drive_delay = 100
        self.pi_length = 500
        self.readout_delay = 90000
        self.readout_length = 2000
        self.t2_m = 2  # time between two Pi/2 pulse for T2 sequence
        self.drive_amp = 0.1
        self.readout_amp = 0.1

    def load_t2_ch(self, pulse, p_length, t2_m):
        wf = lw.zero_waveform(pulse.delay_unit_time, pulse.offset / pulse.awg_range)
        km.load_wave_awg(self.msys.awg, wf, self.msys.awg_next_id)
        pulse.delay_wave_id = self.msys.awg_next_id
        self.msys.awg_next_id += 1
        wd = pulse.delay % pulse.delay_unit_time
        wf = lw.dc_t2_waveform(wd, p_length/2, pulse.fre, np.pi / 2 * pulse.phase / 90.0,
                               pulse.pulse_amp / pulse.awg_range, pulse.offset / pulse.awg_range, t2_m)
        km.load_wave_awg(self.msys.awg, wf, self.msys.awg_next_id)
        pulse.pulse_wave_id = msys.awg_next_id
        msys.awg_next_id += 1
        km.queue_delay_pulse(self.msys.awg, pulse)

    def setup_t2_pulses(self):
        self.drive_i = T2Pulse()
        self.drive_q = T2Pulse()
        self.readout_i = IQPulse()
        self.readout_q = IQPulse()
        self.msys.awg.waveformFlush()
        self.msys.awg_next_id = 0
        self.drive_i.fre = self.msys.pulse_fre
        self.drive_q.fre = self.msys.pulse_fre
        self.readout_i.fre = self.msys.pulse_fre
        self.readout_q.fre = self.msys.pulse_fre

        self.drive_i.set_parameter(self.unit_delay, self.drive_delay, None, 1, self.msys.awg_qrange, self.drive_amp,
                                   self.msys.qubit_mixer.i_offset, 0,
                                   1)
        self.drive_q.set_parameter(self.unit_delay, self.drive_delay, None, 2, self.msys.awg_qrange,
                                   self.drive_amp * self.msys.qubit_mixer.q_ratio,
                                   self.msys.qubit_mixer.q_offset, self.msys.qubit_mixer.phase, 1)
        self.readout_i.set_parameter(self.unit_delay, self.readout_delay, self.readout_length, 3, self.msys.awg_crange,
                                     self.readout_amp, self.msys.cavity_mixer.i_offset, 0, 1)
        self.readout_q.set_parameter(self.unit_delay, self.readout_delay, self.readout_length, 4, self.msys.awg_crange,
                                     self.readout_amp * self.msys.cavity_mixer.q_ratio,
                                     self.msys.cavity_mixer.q_offset, self.msys.cavity_mixer.phase, 1)
        self.load_t2_ch(self.drive_i, self.pi_length, self.t2_m)
        self.load_t2_ch(self.drive_q, self.pi_length, self.t2_m)
        load_one_ch(self.readout_i)
        load_one_ch(self.readout_q)


"""
if __name__ == "__main__":
    setup_io()
    setup_hvi()
    one_run()
    hvi_stop()
    stop_measurement()
"""