import numpy as np
import matplotlib.pyplot as plt
import pyvisa
import time
import os
import argparse
from playsound import playsound


def reprogram_experiment(SMU, DMM, count, DMM_count, DMM_aper_time): # pulsewidth > 160us, reptime > 
    # Reprogram DMM first
    DMM.write('CMDSET AGILENT')
    DMM.write('SENS:VOLT:DC:NPLC 10')
    DMM.write('SENS:VOLT:DC:RANG:AUTO 1')
    DMM.write('SENS:VOLT:DC:RANG:UPP 5')
    DMM.write('SENS:VOLT:DC:APER ' + str(DMM_aper_time))

    DMM.write('TRIG:COUNT ' + str(DMM_count))
    DMM.write('TRIG:DELAY 0.05')
    DMM.write('TRIG:SOUR:IMM')
    
    # Reprogram SMU
    SMU.write('SOUR:FUNC:MODE CURR')
    SMU.write('SOUR:CURR:LEV:IMM 0')
    SMU.write('SENS:VOLT:PROT:LEV 5')

    # Set initial conditions for trigger pulse
    SMU.write('SENS:VOLT:DC:APER 50e-6')
    
    SMU.write('SOUR:FUNC:SHAP PULS')
    SMU.write('SOUR:PULS:DEL 0')
    SMU.write('SOUR:PULS:WIDTH 500e-6')
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

def measure(SMU, DMM, pulse_amplitude, pulse_width, acq_delay, aper_time, DMM_count):
    
    # Set peak currents for pulse amplitude
    SMU.write('SOUR:CURR:TRIG ' + str(pulse_amplitude))
    
    # Hardcode pulse widths and acquisition delays and keep constant


    # acq_delay = pulse_width - aper_time
    # dutyCycle = (pulsewidth - pulse_amplitude * smuCurrentRampTime) / reptime # For I-L Curve

    # Set pulse width, acquisition delay (measurement time), and aper time (integration window)
    SMU.write('SOUR:PULS:WIDTH ' + str(pulse_width) + 'e-6')
    SMU.write('TRIG:ACQ:DEL ' + str(acq_delay) + 'e-6')
    SMU.write('SENS:VOLT:DC:APER ' + str(aper_time) + 'e-6')
    
    # Initiate SMU
    SMU.write('OUTP ON')
    SMU_dump(SMU)
    SMU.write('INIT:ALL')
    
    # tau0 = time.time()
    
    # Initiate Multimeter
    DMM.write('INIT')
    
    # Read SMU measurements
    SMU.write('*WAI')
    s = SMU.query('TRAC:STAT:DATA?')
    
    # Check time of SMU measurement and wait if measurment took < 2s
    # tpassed = time.time()-tau0
    # offtime = 2 - tpassed
    # if offtime > 0:
    #     time.sleep(offtime)
    
    # DMM.write('WAI')
    Ls = DMM.query('FETC?')
    print('DMM volts: ', Ls)
    Ls = Ls.split(',')
    
    SMU_volt = float(s.split(',')[0])
    SMU_curr = float(s.split(',')[1])
    
    Ls_tot = 0
    for i in range(len(Ls)):
        Ls_tot += float(Ls[i])
    DMM_volt = Ls_tot / int(DMM_count)

    return [SMU_volt, SMU_curr, DMM_volt]



parser = argparse.ArgumentParser()
parser.add_argument("-L", "--cavlen", type=float, help="Specify cavity length for data file (in mm)", required=True)
parser.add_argument("-T", "--temp", type=float, help="Specify temperature for data file (in C)", required=True)
parser.add_argument("-N", "--count", type=int, help="Number of pulses per current", default = 2000)
parser.add_argument("-D", "--DMMcount", type=int, help="Number of trigger counts for DMM", default = 5)
parser.add_argument("-p", "--pulsewidth", type=int, help="Set pulse width (def=500 us)", default = 500)
parser.add_argument("-a", "--acqdelay", type=int, help="Set acquisition delay (def=440 us)", default = 440)
parser.add_argument("--apertime", type=float, help="Set aperture time (def=50 us)", default = 50)
parser.add_argument("--DMMapertime", type=float, help="Set DMM aperture time (def=1 ms)", default = 1e-3)
parser.add_argument("--minI", type=float, help="Set minimum current for sweep (in A)", default = 0)
parser.add_argument("--maxI", type=float, help="Set maximum current for sweep (in A)", default = 2)
parser.add_argument("--dI", type=float, help="Set current increment for sweep (in A)", default = 0.05)
parser.add_argument("-s", "--submarine", action="store_false", help="Play submarine sound", default = True)
args = parser.parse_args()

if args.submarine == False:
    if os.path.exists('C:\\Users\\sschons2\\Documents\\GitHub\\submarine.mp3'):
        playsound('C:\\Users\\sschons2\\Documents\\GitHub\\submarine.mp3')


data_dir = './data_CavLen_Temp/'
if not os.path.exists(data_dir):
    os.mkdir(data_dir)


rm = pyvisa.ResourceManager()
print(rm.list_resources())


# name1, name2 = rm.list_resources()

# if 'MY' in name1:
#     SMU_name = name1
#     DMM_name = name2
# else:
#     SMU_name = name2
#     DMM_name = name1

SMU_name = 'USB0::0x0957::0x8B18::MY51143520::0::INSTR'
DMM_name = 'USB0::0x1AB1::0x0C94::DM3O151200124::0::INSTR'

SMU = rm.open_resource(SMU_name)
DMM = rm.open_resource(DMM_name)

print(SMU.query('*IDN?'))
print(DMM.query('*IDN?'))            # this WOULD NOT work with the Fluke DMM, switched to RIGOL
print('\n')

SMU.write('*RST')
DMM.write('*RST')

SMU.write('SENS:REM ON') # sets to 4-wire mode (increases accuracy at low res/curr)
SMU.timeout = 100000 # sets waiting time to timeeout in ms
DMM.timeout = 100000

CL = args.cavlen # mm
T = args.temp # C

minI = args.minI
maxI = args.maxI
dI = args.dI

currents = np.arange(minI, maxI + dI, dI)
SMU_volts = []
SMU_currs = []
DMM_volts = []

reprogram_experiment(SMU, DMM, args.count, args.DMMcount, args.DMMapertime)


for i in range(len(currents)): 
    V, I, L = measure(SMU, DMM, currents[i], args.pulsewidth, args.acq_delay, args.apertime, args.DMMcount)
    SMU_volts.append(V)
    SMU_currs.append(I)
    print('For curr: ', currents[i])
    print('SMU_curr = ', I)
    print('SMU_volt = ', V)
    print('DMM_volt = ', L, '\n')
    DMM_volts.append(L)
    
    if i % 10 == 0:
        np.savetxt('./data_CavLen_Temp/IVL_{0:.2f}_{1:.2f}.csv'.format(CL, T), 
                    np.transpose(np.array([SMU_volts,SMU_currs, DMM_volts])), fmt = '%s', delimiter = ',')


    # Wait 2s in between currents
    time.sleep(2)


SMU.write('OUTP OFF')
SMU.write('*RST')

SMU_currs.insert(0,'SMU Curr (A)')
SMU_volts.insert(0,'SMU Volt (V)')
DMM_volts.insert(0, 'DMM Volt (V)')

SMU_currs = np.array(SMU_currs)
SMU_volts = np.array(SMU_volts)
DMM_volts = np.array(DMM_volts)


np.savetxt('./data_CavLen_Temp/IVL_{0:.2f}_{1:.2f}.csv'.format(CL, T), 
            np.transpose(np.array([SMU_volts,SMU_currs, DMM_volts])), fmt = '%s', delimiter = ',')






