import numpy as np
import matplotlib.pyplot as plt
import pyvisa
import serial

rm = pyvisa.ResourceManager()
print(rm.list_resources())

SMU_name, DMM_name = rm.list_resources()

SMU = rm.open_resource(SMU_name)
DMM = rm.open_resource(DMM_name)

print(SMU.query('*IDN?'))
print(DMM.query('*IDN?')) # this WOULD NOT work with the Fluke DMM, switched to RIGOL

# SMU.write('OUTP ON')                # Turns output on
SMU.write('SENS:REM ON')            # Connection type: 4-wire mode
SMU.write('SOUR:FUNC:MODE CURR')    # Output source function mode: current
SMU.write('SOUR:CURR 0.030')        # Sets current: 30 mA
SMU.write('SENS:VOLT:PROT 5.0')     # Sets compliance voltage: 5.0 V


print('SMU Curr:', float(SMU.query('MEAS:CURR:DC?')))
print('SMU Volt:', float(SMU.query('MEAS:VOLT:DC?')))



# SMU.write('SOUR:CURR 0.0')

# print(SMU.query('MEAS:VOLT:DC?'))
# print(SMU.query('MEAS:CURR:DC?'))


SMU.write('INIT')
# SMU.write('DISP:ENAB ON')


SMU.write('OUPT OFF')



'''
DMM Commands:
    DMM.query('MEAS:VOLT:DC?')
'''

print('DMM Volt:', float(DMM.query('MEAS:VOLT:DC?')))
