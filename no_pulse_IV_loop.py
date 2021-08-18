
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
print(DMM.query('*IDN?')) # this WOULD NOT work with the Fluke DMM, switched to RIGOL

SMU.write('SENS:REM ON')            # Connection type: 4-wire mode
SMU.write('SOUR:FUNC:MODE CURR')    # Output source function mode: current
SMU.write('SOUR:CURR 0.00')          # Sets current: 30 mA
SMU.write('SENS:VOLT:PROT 5.0')     # Sets compliance voltage: 5.0 V

currents = np.linspace(0,0.05,10)
actual_currents = []
SMU_volt = []
DMM_volt = []

for i in currents:
    current = str(i)
    SMU.write('SOUR:CURR '+current)        # Sets current to i

    
    t1 = time.time()
    SMU.write('OUTP ON')
    
    actual_currents.append(float(SMU.query('MEAS:CURR:DC?')))
    SMU_volt.append(float(SMU.query('MEAS:VOLT:DC?')))
    DMM_volt.append(float(DMM.query('MEAS:VOLT:DC?'))) # this is slow, ~5sec

    
    SMU.write('SOUR:CURR 0.0')             # Sets current to 0
    t2 = time.time()
    
    time.sleep(1)
    
    print('Time this loop:',(t2-t1))


SMU.write(':OUPT OFF')
SMU.write('*RST')


print('ACTUAL_CURR: ', actual_currents)
print('SMU_VOLT: ', SMU_volt)
print('DMM_VOLT: ', DMM_volt)

plt.figure()
plt.plot(actual_currents, SMU_volt, 'k.')
plt.plot(actual_currents, DMM_volt, 'b.')
plt.show()


'''
DMM Commands:
    DMM.query('MEAS:VOLT:DC?')
'''


