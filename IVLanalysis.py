
"""
messing around with data analysis for advanced project laser diode characterization
project

@author: samuelschonsberg
"""
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# photodiode: Thorlabs SM05PD1B

def data_readin(file):
    V = np.loadtxt(file,dtype=float,skiprows=1,usecols=0,delimiter=',') # voltage across LD
    I = np.loadtxt(file,dtype=float,skiprows=1,usecols=1,delimiter=',') # current through LD
    V_PD = np.loadtxt(file,dtype=float,skiprows=1,usecols=2,delimiter=',') # voltage out of PD
    return [V,I,V_PD]

def num_derivative(x,y):
    dydx = []
    for i in range(len(y)-1):
        dy = y[i+1] - y[i]
        dx = x[i+1] - x[i]
        dydx.append(dy/dx)
    return dydx

file_list = os.listdir('data_CavLen_Temp')
for i in file_list:
    if i == '.DS_Store':
        file_list.remove(i)

file_list.sort()
file_list = file_list[:4]

V_SMU = []
I_SMU = []
V_DMM = []
for i in file_list:
    V,I,Vpd = data_readin('data_CavLen_Temp/'+i)
    V_SMU.append(V)
    I_SMU.append(I)
    V_DMM.append(Vpd)
        

dots = ['k.','b.','r.','g.']
lines = ['k--','b--','r--','g--']
solid_lines = ['k-','b-','r-','g-']
labels = ['2mm, 15°C','2mm, 30°C','3mm, 15°C','3mm, 30°C']



# making basic IV and IL plots
# plt.figure()
# plt.xlabel('Voltage Across LD (V)')
# plt.ylabel('Current Through LD (I)')
# for i in range(len(file_list)):
#     plt.plot(V_SMU[i],I_SMU[i],dots[i],label=labels[i])
# plt.legend()

fig, ax1 = plt.subplots()
ax2 = fig.add_axes([.375,.3,.3,.55])
ax1.set_xlim(0,1.75)
ax1.set_ylim(0,2.1)
ax2.set_xlim(1.3,1.6)
ax2.set_ylim(0,1.2)
ax1.set_xlabel('Voltage Across LD (V)')
ax1.set_ylabel('Injection Current (A)')
for i in range(4):
    ax1.plot(V_SMU[i],I_SMU[i],solid_lines[i],label=labels[i])
    ax2.plot(V_SMU[i],I_SMU[i],solid_lines[i])


rectangle = patches.Rectangle((1.3, 0), .3, 1.2, linewidth=1, edgecolor='gray',
                              facecolor='none')
ax1.add_patch(rectangle)
ax1.legend()

plt.figure()
plt.xlabel('Current Through LD (I)')
plt.ylabel('Voltage Out of PD (V)')
for i in range(len(file_list)):
    plt.plot(I_SMU[i],V_DMM[i],dots[i],label=labels[i])
plt.legend()



# making a plot of dynamic series resistance
#   from what I found online, this is defined as dV/dI where I is the injection
#   current and V is the resultant voltage across the diode
R_series = []

fig, ax1 = plt.subplots()
ax2 = ax1.twinx()
ax1.set_xlabel('Injection Current (A)')
ax1.set_ylabel('Voltage Across LD (V)')
ax2.set_ylabel('Series Resistance (Ω)')
ax1.set_ylim(0,2.6)
ax2.set_ylim(0,2.6)
for i in range(len(file_list)):
    dVdI = num_derivative(I_SMU[i], V_SMU[i])
    R_series.append(dVdI)
    ax1.plot(I_SMU[i],V_SMU[i],lines[i])
    ax2.plot(I_SMU[i][2:],dVdI[1:],solid_lines[i],label=labels[i])
plt.legend()



# finding power out in watts
# FIXME: don't know if this is actually how I'm supposed to calc this
# for now, I'm assuming the power is spread uniformly over the sphere's interior,
#   so I divide the power measured by the photodiode by the its active surface and
#   multiply by the surface area of the integrating sphere
# also, I'm assuming that the back end of the laser diode is not coated in a
#   reflective coating, so that half the light is emitted into the sphere, and
#   the other half is emitted out the back of the diode

responsivity = 0.5 # A/W
R_load = 10000 # ohms

Pout = [] # power output by LD into integrating sphere (might only be 1/2 the true Pout)
for i in V_DMM:
    P_detector = i/(responsivity*R_load)
    P_out = 2 * (8107.23/13) * P_detector #factor of 2 assuming the back side of the LD
    # isn't coated, second factor is SA of sphere/SA of detector
    Pout.append(P_out)



# finding slope efficiencies for each
start_idx = [170,194,144,162] # index where lasing starts

slope_efficiencies = []
efficiency_intercepts = []
print('Slope Efficiencies:')
for i in range(len(file_list)):
    slope_efficiency, intercept = np.polyfit(I_SMU[i][start_idx[i]:],
                                             Pout[i][start_idx[i]:],deg=1)
    slope_efficiencies.append(slope_efficiency)
    efficiency_intercepts.append(intercept)
    print(labels[i] + ':',round(slope_efficiency,4))



# find threshold currents using the slope efficiencies/intercepts
slope_efficiencies = np.array(slope_efficiencies)
efficiency_intercepts = np.array(efficiency_intercepts)

I_thresh = -efficiency_intercepts/slope_efficiencies

plt.figure()
plt.xlabel('Current Through LD (A)')
plt.ylabel('Power Out of LD into Integrating Sphere (W)')
plt.xlim(1.25,2.05)
plt.ylim(0,0.22)
print('\nThreshold Currents:')
for i in range(len(file_list)):
    plt.plot(I_SMU[i],Pout[i],dots[i],label=labels[i],alpha=0.3)
    Is = np.linspace(I_thresh[i],2.1,1000)
    plt.plot(Is, Is*slope_efficiencies[i] + efficiency_intercepts[i],lines[i])
    print(labels[i]+':',round(I_thresh[i],2))
plt.legend()

# using slope efficiencies to find differential quantum efficiency
q = 1.602e-19 # electron charge (C)
h = 6.626e-34 # planck's constant (J*s)
nu = 3e8 / 800e-9 # frequency of radiation (Hz)

eta_d = ( q/(h*nu) ) * slope_efficiencies # differential quantum efficiency

print('\nDifferential Quantum Efficiencies:')
for i in range(len(file_list)):
    print(labels[i]+':',round(eta_d[i],4))
    

# using eta_d and L, find injection efficiency and internal optical loss (for a given temp)
#   For T=15°C: make fit y=mx + b
inv_eta_d_15 = 1/eta_d[:2] # units?
L = np.array([2e-3,3e-3]) # m
m,b = np.polyfit(L,inv_eta_d_15,deg=1)

eta_i_15 = 1/b
alpha_i_15 = np.log(1/.33)/b

print('\nFor T=15°C:')
print('Injection Efficiency =',round(eta_i_15,4))
print('Net Internal Optical Loss =',round(alpha_i_15,4))

#   For T=30°C: make fit y=nx + c
inv_eta_d_30 = 1/eta_d[2:]
n,c = np.polyfit(L,inv_eta_d_30,deg=1)

eta_i_30 = 1/c
alpha_i_30 = np.log(1/.33)/c

print('\nFor T=30°C:')
print('Injection Efficiency =',round(eta_i_30,4))
print('Net Internal Optical Loss =',round(alpha_i_30,4))

Ls = np.linspace(1.9e-3,3.1e-3,1000)

plt.figure()
plt.plot(L*1000,inv_eta_d_15,'ro',
         label='T=15°C, $\\eta_i$='+str(round(eta_i_15,4))+', $\\langle \\alpha_i \\rangle$='+str(round(alpha_i_15,4))+'m$^{-1}$')
plt.plot(Ls*1000,Ls*m + b,'r--')

plt.plot(L*1000,inv_eta_d_30,'bo',label='T=30°C, $\\eta_i$='+str(round(eta_i_30,4))+', $\\langle \\alpha_i \\rangle$='+str(round(alpha_i_30,4))+'m$^{-1}$')
plt.plot(Ls*1000,Ls*n + c,'b--')
plt.xlabel('Cavity Length (mm)')
plt.ylabel(r'Inverse Differential Quantum Efficiency, $1/\eta_d$')
plt.legend()




# using temperatures and threshold currents, find the characteristic temperature (for a given cavity length)
#   For L=2mm: fit y=gx + f
I_thresh_2 = I_thresh[:2]
T = np.array([15+273.15,30+273.15]) # temperatures in K
g,f = np.polyfit(T,np.log(I_thresh_2),deg=1)

T0_2 = 1/g # characteristic temp for L=2mm
I0_2 = np.exp(f)

print('\nFor L=2mm:')
print('Characteristic Temperature =',round(T0_2,2))

#   For L=3mm: fit y=ux + v
I_thresh_3 = I_thresh[2:]
u,v = np.polyfit(T,np.log(I_thresh_3),deg=1)

T0_3 = 1/u
I0_3 = np.exp(v)

print('\nFor L=3mm:')
print('Characteristic Temperature =',round(T0_3,2))

Ts = np.linspace(np.log(283.15),np.log(308.15),1000)

plt.figure()
plt.plot(T,I_thresh_2,'ko',label='L=2mm, $T_0$='+str(round(T0_2,2))+'K')
plt.plot(np.exp(Ts),I0_2*np.exp(np.exp(Ts)/T0_2),'k--')

plt.plot(T,I_thresh_3,'go',label='L=3mm, $T_0$='+str(round(T0_3,2))+'K')
plt.plot(np.exp(Ts),I0_3*np.exp(np.exp(Ts)/T0_3),'g--')
plt.xlabel('Temperature (K)')
plt.ylabel('Threshold Current (A)')
plt.legend()




