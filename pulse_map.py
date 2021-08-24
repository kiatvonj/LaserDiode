import numpy as np
import matplotlib.pyplot as plt
import pyvisa
# import serial

rm = pyvisa.ResourceManager()
print(rm.list_resources())

name1, name2 = rm.list_resources()

if 'MY' in name1:
    SMU_name = name1
    DMM_name = name2
else:
    SMU_name = name2
    DMM_name = name1


SMU = rm.open_resource(SMU_name)
DMM = rm.open_resource(DMM_name)

print(SMU.query('*IDN?'))
print(DMM.query('*IDN?'))            # this WOULD NOT work with the Fluke DMM, switched to RIGOL
print('\n')

SMU.write('*RST')


# currents = np.linspace(0,0.05,10)
# actual_currents = []
# SMU_volt = []
# DMM_volt = []

# for i in currents:
# current = str(i)



SMU.timeout = 10000 # sets waiting time to timeeout in ms
DMM.timeout = 10000

def pulse_map(trig_time,pulse_width,acq_delay):
    SMU.write('SENS:REM ON')            # Connection type: 4-wire mode
    
    curr_peak = 400e-3
    
    # trig_time = 1.5    # seconds
    # pulse_width = 0.5  # seconds
    trans_delay = trig_time*0.4 # (trig_time/2-pulse_width) # seconds
    pulse_delay = trig_time*0.1 # pulse_width/2  # seconds
    # acq_delay =  trig_time/2  # seconds
     
    
    # DMM.write('CONF:VOLT:DC AUTO')
    # DMM.write('CALC:STAT ON')
    
    # Defining function: pulse shape w/ base and peak values
    SMU.write('SOUR:FUNC:MODE CURR') # set source output to current
    SMU.write('SOUR:FUNC:SHAP PULS') # set output shape to pulse
    SMU.write('SOUR:CURR 0')         # set base value of the pulse
    SMU.write('SOUR:CURR:TRIG ' + str(curr_peak)) # set peak value of the pulse
    
    # Defining total trigger time and count
    SMU.write('TRIG:SOUR TIM')  # sets the timer trigger source
    SMU.write('TRIG:TIM ' + str(trig_time))  # sets trigger interval in seconds
    SMU.write('TRIG:COUN 10')    # sets the trigger count to 3
    
    
    # Defining pulse time after start of trigger and pulse width (Need to be < TRIG:TIM )
    SMU.write('TRIG:TRAN:DEL ' + str(trans_delay)) # sets the transient delay
    SMU.write('SOUR:PULS:DEL ' + str(pulse_delay)) # set pulse delay (in seconds)
    SMU.write('SOUR:PULS:WIDT ' + str(pulse_width)) # set pulse width (in seconds)
    
    # Defining Acquisition time (measurement) after start of trigger
    SMU.write('TRIG:ACQ:DEL ' + str(acq_delay))   # sets the acquisition delay (in seconds)
    
    
    SMU.write('SENS:FUNC ALL ') # sets the measurement type to all
    
    SMU.write('SENS:VOLT:RANG:AUTO ON') # automatic range measurement (?)
    SMU.write('SENS:VOLT:APER 0.1')  # sets the measurement aperture time
    SMU.write('SENS:VOLT:PROT 5')    # sets the compliance limit
    
    SMU.write('SENS:CURR:RANG:AUTO ON') # automatic range measurement
    
    
    # DMM.write('TRIG:COUN 1')
    # DMM.write('TRIG:DEL ' + str(acq_delay))
    
    
    SMU.write('OUTP ON')    # turns the output source on
    SMU.write('INIT')       # starts pulse output and spot measurements
    # DMM.write('INIT')

    
    SMU.write('FETC:ARR:VOLT?')
    voltage = np.array(str(SMU.read()).split(','), dtype=float)
    SMU.write('FETC:ARR:CURR?')
    current = np.array(str(SMU.read()).split(','), dtype=float)
    # DMM_voltage = float(DMM.query('FETC?'))
    

    return (voltage,current) #,DMM_voltage)


pulse_width = 0.001 # second
trigger_length = 0.3 # pulse_width*5 # second

trig_start_to_pulse_delay = np.linspace(0,trigger_length/2-pulse_width,5) # sample points from 0 to start of pulse rise
pulse_sample = np.linspace(trigger_length/2-pulse_width,trigger_length/2+pulse_width,15)
end_pulse_to_end_trigger = np.linspace(trigger_length/2+pulse_width,trigger_length,5)
# acq_delays = np.linspace(0,trigger_length,20)
acq_delays = np.concatenate((trig_start_to_pulse_delay,pulse_sample,end_pulse_to_end_trigger))

# acq_delays = np.arange(.49,.51,0.001)

volts = []
currs = []
DMM_volts = []

for i in acq_delays:
    voltage, current = pulse_map(trigger_length,pulse_width,i)
    volts.append(voltage)
    currs.append(current)
    # DMM_volts.append(DMM_voltage)
    
SMU.write('OUTP OFF')
SMU.write('*RST')
    
volts = np.array(volts)
currs = np.array(currs)
print(volts[:,0])


plt.figure()
plt.plot(acq_delays,volts[:,0],'k.')
plt.plot(acq_delays,volts[:,1], 'r.')
plt.plot(acq_delays,volts[:,2])
plt.plot(acq_delays,volts[:,3])
plt.plot(acq_delays,volts[:,4])
plt.plot(acq_delays,volts[:,5])
plt.plot(acq_delays,volts[:,6])
plt.plot(acq_delays,volts[:,7])
plt.plot(acq_delays,volts[:,8])
plt.plot(acq_delays,volts[:,9])
plt.xlabel('Time (s)')
plt.ylabel('SMU Voltage')

plt.figure()
plt.plot(acq_delays,currs[:,0],'k.')
plt.plot(acq_delays,currs[:,1], 'r.')
plt.plot(acq_delays,currs[:,2])
plt.plot(acq_delays,currs[:,3])
plt.plot(acq_delays,currs[:,4])
plt.plot(acq_delays,currs[:,5])
plt.plot(acq_delays,currs[:,6])
plt.plot(acq_delays,currs[:,7])
plt.plot(acq_delays,currs[:,8])
plt.plot(acq_delays,currs[:,9])


plt.xlabel('Time (s)')
plt.ylabel('SMU Current')










# volt1, curr1 = pulse_map(1.5,1,1.5/2)


