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



SMU.write('SENS:REM ON')            # Connection type: 4-wire mode
SMU.write('SOUR:FUNC:MODE CURR')    # Output source function mode: current
SMU.write('SOUR:CURR 0.00')          # Sets current: 30 mA
SMU.write('SENS:VOLT:PROT 5.0')     # Sets compliance voltage: 5.0 V

SMU.write('OUTP ON')                # Turns output on (supposedly, doesn't seem to do anything)

print('SMU Curr:', float(SMU.query('MEAS:CURR:DC?')))
print('SMU Volt:', float(SMU.query('MEAS:VOLT:DC?')))

print('DMM Volt:', float(DMM.query('MEAS:VOLT:DC?')))


# SMU.write('INIT')


print('\n')



currents = np.linspace(0,0.05,10)
actual_currents = []
SMU_volt = []
DMM_volt = []

for i in currents:
    current = str(i)
    # SMU.write('SOUR:CURR '+current)        # Sets current to i
    
    SMU.write('SOUR:FUNC:SHAP PULS')        
    SMU.write('SOUR:PULS:DEL 1E-3')        
    SMU.write('SOUR:PULS:WIDT 0.5')        
    SMU.write('SOUR:CURR 0')        
    SMU.write('SOUR:CURR:TRIG '+ current)        
    
    # SMU.write('SENS:CURR:APER .25')
    # SMU.write('SENS:VOLT:APER .25')

    
    SMU.write('INIT')
    # SMU.write('TRIG:SING')

    

    SMU.write('OUTP ON')

    SMU.write('SENS:FUNC:OFF:ALL')
    SMU.write('SENS:FUNC ""CURR""')
    
    SMU.write('SENS:WAIT OFF')
    SMU.write('TRIG:SOUR TIM')
    SMU.write('TRIG:TIM 1E-3')
    SMU.write('TRIG:ACQ:DEL 2E-5')

    actual_currents.append(float(SMU.query('MEAS:CURR:DC?')))
    SMU_volt.append(float(SMU.query('MEAS:VOLT:DC?')))
    DMM_volt.append(float(DMM.query('MEAS:VOLT:DC?')))
    
    print(SMU.query('MEAS:CURR?'))
    
    # SMU.write('SOUR:WAIT ON')
    # SMU.write('SOUR:WAIT:AUTO OFF')
    # SMU.write('SOUR:WAIT:OFFS 10E-6')
    
    # SMU.write('SOUR:CURR 0.0')             # Sets current to 0
    
    


SMU.write(':OUTP OFF')
SMU.write('*RST')


print('ACTUAL_CURR: ', actual_currents)
print('SMU_VOLT: ', SMU_volt)
print('DMM_VOLT: ', DMM_volt)

plt.figure()
plt.plot(actual_currents, SMU_volt, 'k.')
plt.plot(actual_currents, DMM_volt, 'b.')
plt.show()



'''
SMU Commands:
    SMU.query('MEAS:CURR:DC?')
    SMU.query('MEAS:VOLT:DC?')
    DMM.query('MEAS:VOLT:DC?')


DMM Commands:
    DMM.query('MEAS:VOLT:DC?')
'''


