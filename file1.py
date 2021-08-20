import numpy as np
import matplotlib.pyplot as plt
import pyvisa
import time

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



# currents = np.linspace(0,0.05,10)
# actual_currents = []
# SMU_volt = []
# DMM_volt = []

# for i in currents:
# current = str(i)

SMU.write('*RST')
SMU.write('SENS:REM ON')            # Connection type: 4-wire mode


#### Trying the pulse spot measurement example code from B2900 programming manual

SMU.timeout = 10000 # sets waiting time to timeeout in ms
DMM.timeout = 10000

curr_peak = 30e-3

trig_time = 1.5    # seconds
pulse_width = 0.5  # seconds
trans_delay = (trig_time-pulse_width)/2 # seconds
pulse_delay = 0  # seconds
acq_delay =  trig_time/2  # seconds
 

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
SMU.write('TRIG:COUN 1')    # sets the trigger count to 3


# Defining pulse time after start of trigger and pulse width (Need to be < TRIG:TIM )
SMU.write('TRIG:TRAN:DEL ' + str(trans_delay)) # sets the transient delay
SMU.write('SOUR:PULS:DEL ' + str(pulse_delay)) # set pulse delay (in seconds)
SMU.write('SOUR:PULS:WIDT ' + str(pulse_width)) # set pulse width (in seconds)

# Defining Acquisition time (measurement) after start of trigger
SMU.write('TRIG:ACQ:DEL ' + str(acq_delay))   # sets the acquisition delay (in seconds)


SMU.write('SENS:FUNC ALL ') # sets the measurement type to all

SMU.write('SENS:VOLT:RANG:AUTO ON') # automatic range measurement (?)
# SMU.write('SENS:VOLT:RANG 5') 
SMU.write('SENS:VOLT:APER 0.1')  # sets the measurement aperture time
SMU.write('SENS:VOLT:PROT 5')    # sets the compliance limit

SMU.write('SENS:CURR:RANG:AUTO ON') # automatic range measurement
# SMU.write('SENS:CURR:RANG 0.1') 
# SMU.write('SENS:CURR:APER 0.1')  # sets the measurement aperture time
# SMU.write('SENS:CURR:PROT 0.1')    # sets the compliance limit


# DMM.write('TRIG:SOUR AUTO')
# DMM.write('TRIG:AUTO:INTE 2')
DMM.write('TRIG:COUN 1')
DMM.write('TRIG:DEL ' + str(acq_delay))

SMU.write('OUTP ON')    # turns the output source on
SMU.write('INIT')       # starts pulse output and spot measurements
t1 = time.time()
DMM.write('INIT')





SMU.write('FETC:ARR:VOLT?')
print(SMU.read())
SMU.write('FETC:ARR:CURR?')
print(SMU.read())

# print(DMM.query('CALC:AVER:MAX?'))
# DMM.write('CALC:STAT OFF')

t2 = time.time()
print(t2-t1)
print(DMM.query('FETC?'))


SMU.write('OUTP OFF')
SMU.write('*RST')
















'''
SMU Commands:
    SMU.query('MEAS:CURR:DC?')
    SMU.query('MEAS:VOLT:DC?')
    DMM.query('MEAS:VOLT:DC?')


DMM Commands:
    DMM.query('MEAS:VOLT:DC?')
'''


