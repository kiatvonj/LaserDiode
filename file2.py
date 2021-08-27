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

SMU.write('*RST')
SMU.timeout = 100000 # sets waiting time to timeeout in ms
DMM.timeout = 100000
SMU.write('SENS:REM ON')
SMU.write('SENS:FUNC ALL')


def pulse(SMU,pulse_width,pulse_amplitude):
    # FIXME add a wait before or after while the output is zero
    SMU.write('OUTP ON')
    SMU.write('SOUR:FUNC:MODE CURR')
    # SMU.write('SOUR:FUNC:')
    # SMU.write('SOUR:CURR:TRIG')
    SMU.write('SOUR:CURR:LEV:AMPL ' + str(pulse_amplitude))
    
    SMU.write('SENS:VOLT:RANGE:AUTO ON')
    SMU.write('SENS:VOLT:PROT:LEV 5')
    
    SMU.write('SENS:CURR:RANGE:AUTO ON')
    
    
    # print(SMU.query('FETC?'))
    # print(SMU.query('FETC:ARR:CURR?'))
    # print(SMU.query('TRAC:STAT:DATA?'))
    SMU_volt = float(SMU.query('MEAS:VOLT:DC?'))
    SMU_curr = float(SMU.query('MEAS:CURR:DC?'))
    SMU.write('SOUR:CURR:LEV:AMPL 0')
    # SMU.write('TRIG:SOUR TIM')
    # SMU.write('TRIG:TIME 1')
    # SMU.write('TRIG:COUN 1')
    # SMU.write('TRIG:TRAN:DEL 0')
    # SMU.write('TRIG:ACQ:DEL 0.1')
    
    print(SMU_volt)
    print(SMU_curr)
    # SMU.write('SOUR:WAIT ON')
    # SMU.write('SOUR:WAIT:AUTO OFF')
    # SMU.write('SOUR:WAIT:OFFS 0.001') # + str(pulse_width))
    

    
    


    # SMU.write('INIT')
    # SMU.write('OUTP OFF')
    time.sleep(0.1)
    return [SMU_volt,SMU_curr]

currents = np.arange(0,2,0.05)

DMM_volts = []
DMM_currs = []

for i in currents:
    foo = pulse(SMU,100,i)
    DMM_volts.append(foo[0])
    DMM_currs.append(foo[1])

# for i in range(10):
#     pulse(SMU, 100, 2)
    
    
SMU.write('OUTP OFF')

plt.plot(DMM_volts,DMM_currs,'k.')



