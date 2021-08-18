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


SMU.write('SOUR:FUNC:MODE CURR')
SMU.write('SOUR:CURR 0.010')
# SMU.write('FORM:ELEM:SENS RES, STAT')
SMU.write('OUTP ON')
# SMU.write('SENS:FUNC:ALL')
# SMU.write('SENS:FUNC:""VOLT""')
# SMU.write('SENS:FUNC:""CURR""')
# SMU.write('SENS:RES:OCOM ON')

SMU.write('MEAS:VOLT?')
SMU.write('initiate')


# print('SMU VOLT:', SMU.read('MEAS:VOLT?'))

'''
DMM Commands:
    DMM.query('MEAS:VOLT:DC?')
'''

print(float(DMM.query('MEAS:VOLT:DC?')))
