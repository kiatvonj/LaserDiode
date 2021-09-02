import numpy as np
import matplotlib.pyplot as plt
import pyvisa
import time
# import serial

def reprogram_experiment(SMU, DMM, count = 100, aper_time = 50, init_pulse_width = 500): # pulsewidth > 160us, reptime > 
    # Reprogram DMM first
    DMM.write('CMDSET AGILENT')
    DMM.write('SENS:VOLT:DC:NPLC 10')
    DMM.write('SENS:VOLT:DC:RANG:AUTO 1')
    DMM.write('SENS:VOLT:DC:RANG:UPP 5')
    
    DMM.write('TRIG:COUNT 3')
    DMM.write('TRIG:DELAY 0.05')
    DMM.write('TRIG:SOUR:IMM')
    
    # Reprogram SMU
    SMU.write('SOUR:FUNC:MODE CURR')
    SMU.write('SOUR:CURR:LEV:IMM 0')
    SMU.write('SENS:VOLT:PROT:LEV 5')

    # Set initial conditions for trigger pulse
    SMU.write('SENS:VOLT:DC:APER ' + str(aper_time) + 'e-6')
    
    SMU.write('SOUR:FUNC:SHAP PULS')
    SMU.write('SOUR:PULS:DEL 0')
    SMU.write('SOUR:PULS:WIDTH ' + str(init_pulse_width) + 'e-6')
    SMU.write('SOUR:CURR:LEV:TRIG 1.0')
    
    SMU.write('TRIG:ALL:COUNT ' + str(count))
    SMU.write('TRIG:ACQ:DEL 0')
    SMU.write('TRIG:ACQ:TIM 0')
    SMU.write('TRIG:TRAN:DEL 0')
    SMU.write('TRIG:TRAN:TIM 0')
    return

def SMU_dump(SMU):
    SMU.write('TRAC:FEED:CONT NEV')
    SMU.write('TRAC:CLE')
    SMU.write('TRAC:FEED SENS')
    SMU.write('TRAC:FEED:CONT NEXT')
    return

def measure(SMU, DMM, pulse_amplitude, DMM_acq_delay = 0.05, aper_time = 50):
    
    # set DMM trigger acquisition delay
    DMM.write('TRIG:DELAY ' + str(DMM_acq_delay))

    # Set peak currents for pulse amplitude
    SMU.write('SOUR:CURR:TRIG ' + str(pulse_amplitude))
    
    # Hardcode pulse widths and acquisition delays based on peak current
    pulse_width = 250 
    acq_delay = 180
    if pulse_amplitude > 1.5:
        pulse_width = 350
        acq_delay = 300
    if pulse_amplitude > 1.55:
        pulse_width = 400
        acq_delay = 350
    if pulse_amplitude > 1.75:
        pulse_width = 500
        acq_delay = 440
    
    pulse_width = 500
    acq_delay = 440
    # print(pulse_width)
    
    # acq_delay = pulse_width - aper_time
    # dutyCycle = (pulsewidth - pulse_amplitude * smuCurrentRampTime) / reptime # For I-L Curve

    # Set pulse width, acquisition delay (measurement time), and aper time (integration window)
    SMU.write('SOUR:PULS:WIDTH ' + str(pulse_width) + 'e-6')
    SMU.write('TRIG:ACQ:DEL ' + str(acq_delay) + 'e-6')
    SMU.write('SENS:VOLT:DC:APER ' + str(aper_time) + 'e-6')
    
    # Initiate SMU
    SMU.write('OUTP ON')
    SMU_dump(SMU)
    SMU.write('INIT:ALL')
    
    # tau0 = time.time()
    
    # Initiate Multimeter
    DMM.write('INIT')
    
    # Read SMU measurements
    SMU.write('*WAI')
    s = SMU.query('TRAC:STAT:DATA?')
    
    # Check time of SMU measurement and wait if measurment took < 2s
    # tpassed = time.time()-tau0
    # offtime = 2 - tpassed
    # if offtime > 0:
    #     time.sleep(offtime)
    
    # DMM.write('WAI')
    v = DMM.query('FETC?')
    print('DMM volts: ',v)
    v = v.split(',')
    
    


    SMU_volt = float(s.split(',')[0])
    SMU_curr = float(s.split(',')[1])
    DMM_volt = float(v[0]) # (float(v[0]) + float(v[1]) + float(v[2])) / 3

    return [SMU_volt, SMU_curr, DMM_volt]


def pulse_map(trig_time,pulse_width,acq_delay, curr_peak):
    SMU.write('SENS:REM ON')            # Connection type: 4-wire mode

    
    # trig_time = 1.5    # seconds
    # pulse_width = 0.5  # seconds
    trans_delay = (trig_time/2-pulse_width/2) # seconds
    pulse_delay = pulse_width/2  # seconds
    # acq_delay =  trig_time/2  # seconds
    
    rise_time = 75e-6 # seconds
    mtime = pulse_width - 2*rise_time
     
    
    # DMM.write('CONF:VOLT:DC AUTO')
    # DMM.write('CALC:STAT ON')
    
    # Defining function: pulse shape w/ base and peak values
    SMU.write('SOUR:FUNC:MODE CURR') # set source output to current
    SMU.write('SOUR:FUNC:SHAP PULS') # set output shape to pulse
    SMU.write('SOUR:CURR:LEV:IMM 1e-3')         # set base value of the pulse
    SMU.write('SOUR:CURR:LEV:TRIG ' + str(curr_peak)) # set peak value of the pulse
    
    # Defining total trigger time and count
    # SMU.write('TRIG:SOUR TIM')  # sets the timer trigger source
    # SMU.write('TRIG:TIM ' + str(trig_time))  # sets trigger interval in seconds
    SMU.write('TRIG:ALL:COUN 10')    # sets the trigger count to 3
    
    
    # Defining pulse time after start of trigger and pulse width (Need to be < TRIG:TIM )
    SMU.write('TRIG:TRAN:DEL 0')# + str(trans_delay)) # sets the transient delay
    SMU.write('SOUR:PULS:DEL 75e-6')# + str(pulse_delay)) # set pulse delay (in seconds)
    SMU.write('SOUR:PULS:WIDT ' + str(pulse_width)) # set pulse width (in seconds)
    
    # Defining Acquisition time (measurement) after start of trigger
    SMU.write('TRIG:ACQ:DEL '+ str(acq_delay))   # sets the acquisition delay (in seconds)
    SMU.write('TRIG:ACQ:TIM 0')
    SMU.write('TRIG:TRAN:TIM 0')
    
    SMU.write('SENS:FUNC ALL ') # sets the measurement type to all
    
    SMU.write('SENS:VOLT:RANG:AUTO ON') # automatic range measurement (?)
    SMU.write('SENS:VOLT:DC:APER 100e-6')# + str(mtime))  # sets the measurement aperture time (integration time for point measurement)
    SMU.write('SENS:VOLT:PROT:LEV 5')    # sets the compliance limit
    
    SMU.write('SENS:CURR:RANG:AUTO ON') # automatic range measurement
    
    
    DMM.write('TRIG:COUN 1')
    # DMM.write('TRIG:DEL ' + str(acq_delay))
    DMM.write('TRIG:DEL 0.2')
    
    SMU.write('OUTP ON')    # turns the output source on
    SMU.write('INIT')       # starts pulse output and spot measurements
    DMM.write('INIT')

    
    SMU.write('FETC:ARR:VOLT?')
    voltage = np.array(str(SMU.read()).split(','), dtype=float)
    SMU.write('FETC:ARR:CURR?')
    current = np.array(str(SMU.read()).split(','), dtype=float)
    DMM_voltage = float(DMM.query('FETC?'))
    

    return (voltage,current,DMM_voltage)

def DMM_delay_map():
    return



rm = pyvisa.ResourceManager()
print(rm.list_resources())

# name1, name2 = rm.list_resources()

# if 'MY' in name1:
#     SMU_name = name1
#     DMM_name = name2
# else:
#     SMU_name = name2
#     DMM_name = name1

SMU_name = 'USB0::0x0957::0x8B18::MY51143520::0::INSTR'
DMM_name = 'USB0::0x1AB1::0x0C94::DM3O151200124::0::INSTR'

SMU = rm.open_resource(SMU_name)
DMM = rm.open_resource(DMM_name)

print(SMU.query('*IDN?'))
print(DMM.query('*IDN?'))            # this WOULD NOT work with the Fluke DMM, switched to RIGOL
print('\n')

SMU.write('*RST')
DMM.write('*RST')


# currents = np.linspace(0,0.05,10)
# actual_currents = []
# SMU_volt = []
# DMM_volt = []

# for i in currents:
# current = str(i)



SMU.timeout = 100000 # sets waiting time to timeeout in ms
DMM.timeout = 100000



# pulse_width = 100e-6 # second
# trigger_length = 0.2     # pulse_width*5 # second
# curr_peak = 400e-3



# trig_start_to_pulse_delay = np.linspace(0,trigger_length/2-pulse_width,5) # sample points from 0 to start of pulse rise
# pulse_sample = np.linspace(trigger_length/2-pulse_width,trigger_length/2+pulse_width,15)
# end_pulse_to_end_trigger = np.linspace(trigger_length/2+pulse_width,trigger_length,5)
# acq_delays = np.linspace(0,trigger_length,20)
# acq_delays = np.concatenate((trig_start_to_pulse_delay,pulse_sample,end_pulse_to_end_trigger))



# reptime = 2000
# curr_peak = 1.75

# pulse_width = 400 # us

# acq_delays = np.arange(200, 350, 2.5)

# volts = []
# currs = []
# DMM_volts = []

# for i in acq_delays:
#     reprogram_experiment(SMU, DMM, pulse_width, reptime, i )
#     V, I = measure(SMU, DMM, curr_peak, pulse_width, reptime, i)
#     volts.append(V)
#     currs.append(I)
#     time.sleep(0.1)


# for i in acq_delays:
#     voltage, current, DMM_voltage = pulse_map(trigger_length,pulse_width,i, curr_peak)
    
#     volts.append(voltage)
#     currs.append(current)
#     DMM_volts.append(DMM_voltage)
#     time.sleep(10*pulse_width+1)
    
SMU.write('OUTP OFF')
SMU.write('*RST')
    
# volts = np.array(volts)
# currs = np.array(currs)
# # print(volts[:,0])


# plt.figure()
# plt.plot(acq_delays, volts, 'k.')
# # plt.plot(acq_delays,volts[:,0],'k.')
# # plt.plot(acq_delays,volts[:,1], 'r.')
# # plt.plot(acq_delays,volts[:,2])
# # plt.plot(acq_delays,volts[:,3])
# # plt.plot(acq_delays,volts[:,4])
# # plt.plot(acq_delays,volts[:,5])
# # plt.plot(acq_delays,volts[:,6])
# # plt.plot(acq_delays,volts[:,7])
# # plt.plot(acq_delays,volts[:,8])
# # plt.plot(acq_delays,volts[:,9])
# plt.xlabel('Time (s)')
# plt.ylabel('SMU Voltage')


# plt.figure()
# plt.plot(acq_delays,currs,'k.')
# # plt.plot(acq_delays,currs[:,0],'k.')
# # plt.plot(acq_delays,currs[:,1], 'r.')
# # plt.plot(acq_delays,currs[:,2])
# # plt.plot(acq_delays,currs[:,3])
# # plt.plot(acq_delays,currs[:,4])
# # plt.plot(acq_delays,currs[:,5])
# # plt.plot(acq_delays,currs[:,6])
# # plt.plot(acq_delays,currs[:,7])
# # plt.plot(acq_delays,currs[:,8])
# # plt.plot(acq_delays,currs[:,9])
# plt.xlabel('Time (s)')
# plt.ylabel('SMU Current')
# # plt.ylim(0, 1.5*curr_peak)
# # plt.savefig('../PulseMapsTesting/PW_{0:.1e}_TL_{1:.1e}_CP_{2:.1e}.png'.format(pulse_width, trigger_length, curr_peak))



# plt.figure()
# plt.plot(acq_delays,DMM_volts)
# plt.ylabel('DMM Voltage')
# plt.xlabel('Acquisition Times')








# volt1, curr1 = pulse_map(1.5,1,1.5/2)


