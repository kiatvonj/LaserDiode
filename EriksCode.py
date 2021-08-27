import numpy as np
import matplotlib.pyplot as plt
import pyvisa
import time


def reprogram_experiment(SMU, DMM, pulsewidth, reptime): # pulsewidth > 160us, reptime > 
    # Reprogram DMM first
    DMM.write('CMDSET AGILENT')
    DMM.write('SENS:VOLT:DC:NPLC 10')
    DMM.write('SENS:VOLT:DC:RANG:AUTO 1')
    DMM.write('SENS:VOLT:DC:RANG:UPP 5')
    
    DMM.write('TRIG:COUNT 1')
    DMM.write('TRIG:DELAY 0.2')
    DMM.write('TRIG:SOUR:IMM')
    
    # Reprogram SMU
    SMU.write('SOUR:FUNC:MODE CURR')
    SMU.write('SOUR:CURR:LEV:IMM 0')
    SMU.write('SENS:VOLT:PROT:LEV 5')
    
    risetime =  100 # us
    mtime = pulsewidth - 2*risetime
    SMU.write('SENS:VOLT:DC:APER ' + str(mtime) + 'e-6')
    
    SMU.write('SOUR:FUNC:SHAP PULS')
    SMU.write('SOUR:PULS:DEL 0')
    SMU.write('SOUR:PULS:WIDTH ' + str(pulsewidth) + 'e-6')
    SMU.write('SOUR:CURR:LEV:TRIG 1.0')
    
    nevents = 2e6 // reptime # 2 seconds total divided by the reptime
    SMU.write('TRIG:ALL:COUNT ' + str(nevents))
    SMU.write('TRIG:ACQ:DEL ' + str(risetime) + 'e-6')
    SMU.write('TRIG:ACQ:TIM ' + str(reptime) + 'e-6')
    SMU.write('TRIG:TRAN:DEL 0')
    SMU.write('TRIG:TRAN:TIM ' + str(reptime) + 'e-6')
    return

# FIXME: subtract bias level from PD measurements

def SMU_dump(SMU):
    SMU.write('TRAC:FEED:CONT NEV')
    SMU.write('TRAC:CLE')
    SMU.write('TRAC:FEED SENS')
    SMU.write('TRAC:FEED:CONT NEXT')
    return

def measure(SMU, DMM, pulse_amplitude, pulsewidth, reptime):
    smuCurrentRampTime = 60 # us/A
    
    SMU.write('OUTP ON')
    
    acqInitHoldoff = 25 # us
    SMU.write('SOUR:CURR:LEV:TRIG ' + str(pulse_amplitude))
    
    acqHoldoff = acqInitHoldoff + pulse_amplitude * smuCurrentRampTime
    acqAper = pulsewidth - acqInitHoldoff - 2*pulse_amplitude * smuCurrentRampTime
    
    if acqAper < 50:
        print('uh fix your aperture time, its less than 50 us!')
        
    # acqAper = 50
    
    dutyCycle = (pulsewidth - pulse_amplitude * smuCurrentRampTime) / reptime
    SMU.write('TRIG:ACQ:DEL ' + str(acqHoldoff) + 'e-6')
    SMU.write('SENS:VOLT:DC:APER ' + str(acqAper) + 'e-6')
    
    SMU_dump(SMU)
    
    SMU.write('INIT:ALL')
    
    # DMM.write('INIT:IMM')
    # DMM.write('*WAI')
    # DMM_volt = DMM.query('*FETC?')
    
    SMU.write('*WAI')
    s =SMU.query('TRAC:STAT:DATA?')

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

SMU.timeout = 100000 # sets waiting time to timeeout in ms
DMM.timeout = 100000


reptime = 2000
pulsewidth = 500
amplitude = 0.05

for i in range(2):
    reprogram_experiment(SMU, DMM, pulsewidth, reptime)
    print(measure(SMU, DMM, amplitude, pulsewidth, reptime)[0])


# width_list = np.arange(100,500,100)
# ampl_list = np.arange(0.01,0.4,0.05)

# for i in width_list:    
#     reprogram_experiment(SMU, DMM, i, reptime)
    
#     for j in ampl_list:
#         print('pulse_widt: ', i, ' pulse_amp: ', round(j,5))
#         print(measure(SMU, DMM, j, i, reptime))
#         print('\n')
        
    



# def current_list(max_current):
#     width_list = np.arange(100,800,50)
#     cur_list = []
#     for i in width_list:
#         reprogram_experiment(SMU, DMM, i, 2000)
#         cur_list.append(measure(SMU, DMM, max_current, i, 2000)[1])
#     cur_list = np.array(cur_list)
    
#     plt.plot(width_list, cur_list/max(cur_list), 'o-')
#     return

# current_list(0.2)
# current_list(0.4)



















# SMU.write('*RST')
# DMM.write('*RST')


