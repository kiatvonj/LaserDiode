import numpy as np
import matplotlib.pyplot as plt
import pyvisa
import time


def reprogram_experiment(SMU, DMM, count = 100, pulse_width = 500, aper_time = 50): # pulsewidth > 160us, reptime > 
    # Reprogram DMM first
    # DMM.write('CMDSET AGILENT')
    # DMM.write('SENS:VOLT:DC:NPLC 10')
    # DMM.write('SENS:VOLT:DC:RANG:AUTO 1')
    # DMM.write('SENS:VOLT:DC:RANG:UPP 5')
    
    # DMM.write('TRIG:COUNT 1')
    # DMM.write('TRIG:DELAY 0')
    # DMM.write('TRIG:SOUR:IMM')
    
    # Reprogram SMU
    SMU.write('SOUR:FUNC:MODE CURR')
    SMU.write('SOUR:CURR:LEV:IMM 0')
    SMU.write('SENS:VOLT:PROT:LEV 5')


    SMU.write('SENS:VOLT:DC:APER ' + str(aper_time) + 'e-6')
    
    SMU.write('SOUR:FUNC:SHAP PULS')
    SMU.write('SOUR:PULS:DEL 0')
    SMU.write('SOUR:PULS:WIDTH ' + str(pulse_width) + 'e-6')
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

def measure(SMU, DMM, pulse_amplitude, aper_time = 50):
    
    SMU.write('SOUR:CURR:TRIG ' + str(pulse_amplitude))
    
    
    
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
    
    print(pulse_width)
    
    # acq_delay = pulse_width - aper_time
    # dutyCycle = (pulsewidth - pulse_amplitude * smuCurrentRampTime) / reptime # For I-L Curve


    SMU.write('SOUR:PULS:WIDTH ' + str(pulse_width) + 'e-6')
    SMU.write('TRIG:ACQ:DEL ' + str(acq_delay) + 'e-6')
    SMU.write('SENS:VOLT:DC:APER ' + str(aper_time) + 'e-6')
    
    SMU.write('OUTP ON')
    
    SMU_dump(SMU)
    
    SMU.write('INIT:ALL')
    
    # DMM.write('INIT:IMM')
    # DMM.write('*WAI')
    # DMM_volt = DMM.query('*FETC?')
    
    SMU.write('*WAI')
    s = SMU.query('TRAC:STAT:DATA?')

    SMU_volt = float(s.split(',')[0])
    SMU_curr = float(s.split(',')[1])
    
    SMU.write('OUTP OFF')
    return [SMU_volt, SMU_curr]



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

cav_length = 1.5 # mm
temp = 15 # C

min_curr = 0
max_curr = 20e-3
dI = 0.5e-3

currents = np.arange(min_curr, max_curr + dI, dI)
SMU_volts = []
SMU_currs = []
# DMM_volt = []

reprogram_experiment(SMU, DMM)


for i in currents: 
    V, I = measure(SMU, DMM, i)
    SMU_volts.append(V)
    SMU_currs.append(I)
    print('For curr: ', i)
    print('SMU_curr = ', I)
    print('SMU_volt = ', V, '\n')
    
    time.sleep(0.1)


SMU.write('OUTP OFF')
SMU.write('*RST')
    
SMU_volts = np.array(SMU_volts)
SMU_currs = np.array(SMU_currs)

plt.figure()
plt.plot(SMU_currs, SMU_volts, 'k.')

plt.xlabel('I')
plt.ylabel('V')



np.savetxt('IV_{}_{}.csv'.format(cav_length, temp), 
           np.transpose(np.array([SMU_volts,SMU_currs])), delimiter = ',')
