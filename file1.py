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

SMU.write('SOUR:FUNC:MODE CURR') # set source output to current
SMU.write('SOUR:FUNC:SHAP PULS') # set output shape to pulse
SMU.write('SOUR:CURR 0')         # set base value of the pulse
SMU.write('SOUR:CURR:TRIG 0.05') # set peak value of the pulse

SMU.write('SOUR:PULS:DEL .25') # set pulse delay (500 us)
SMU.write('SOUR:PULS:WIDT .5') # set pulse width (1 ms)

SMU.write('SENS:FUNC ALL ') # sets the measurement type to all

SMU.write('SENS:VOLT:RANG:AUTO ON') # automatic range measurement (?)
SMU.write('SENS:VOLT:APER 0.1')  # sets the measurement aperture time
SMU.write('SENS:VOLT:PROT 5')    # sets the compliance limit

SMU.write('SENS:CURR:RANG:AUTO ON') # automatic range measurement

SMU.write('TRIG:TRAN:DEL 0.5') # sets the transient delay
SMU.write('TRIG:ACQ:DEL 1.2')   # sets the acquisition delay

SMU.write('TRIG:SOUR TIM')  # sets the timer trigger source
SMU.write('TRIG:TIM 2')  # sets trigger interval to 4 ms
SMU.write('TRIG:COUN 3')    # sets the trigger count to 3

SMU.write('OUTP ON')    # turns the output source on
SMU.write('INIT')       # starts pulse output and spot measurements


SMU.write('FETC:ARR:VOLT?')
print(SMU.read())
SMU.write('FETC:ARR:CURR?')
print(SMU.read())

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


