import numpy as np
import matplotlib.pyplot as plt
import os
import re
from numpy import genfromtxt
from mpl_toolkits.axes_grid.inset_locator import (inset_axes, InsetPosition, mark_inset)

def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx]   

def best_fit(x,y):
    m = (((np.mean(x)*np.mean(y)) - np.mean(x*y))/
        ((np.mean(x)*np.mean(x)) - np.mean(x*x)))
    b = np.mean(y) - m*np.mean(x)
    return m, b

def V_to_P(V):
    responsivity = 0.5e-3 # A/mW
    R_load = 10e3         # V/A
    return V/(responsivity * R_load)

# Make plots dir if not exist
plot_dir = './plots/'
if not os.path.exists(plot_dir):
    os.mkdir(plot_dir)

# Location of data
data_dir = './data_CavLen_Temp/'

# Initialize lists of cavity lengths and temp
CL = []
T = []

# Initialize lists of I, V, L
I = []
V = []
L = []

# Fill in appropriate Cl and T based on name of data file
for name in os.listdir(data_dir):
    if 'IVL_' in name and 'old' not in name:
        params = re.findall("\d+\.\d+", name)
        CL.append(round(float(params[0]), 2))
        T.append(round(float(params[1]), 2))

# Fill I, V, L data
for i in range(len(CL)):
    data_file = data_dir + 'IVL_{0:.2f}_{1:.2f}.csv'.format(CL[i], T[i])
    data = genfromtxt(data_file, delimiter = ',', skip_header = 1)
    I.append(data[:,1])
    V.append(data[:,0])
    L.append(data[:,2])
    
I = np.array(I)
V = np.array(V)
L = np.array(L)


# Set fonts on plot 
plt.rcParams["font.family"] = "Times New Roman"

# IV Curve
fig, ax1 = plt.subplots()
for i in range(len(CL)):
    ax1.scatter(V[i], I[i], s = 3, color = 'C' + str(i))#, label = '{:.1f} mm, {:.2f} C'.format(CL[i],T[i]))
    ax1.plot(V[i], I[i], color = 'C' + str(i), label = '{:.1f} mm, {:.2f} C'.format(CL[i],T[i]))
ax1.set_xlabel('Voltage (V)')
ax1.set_ylabel('Current (A)')
ax1.set_xlim(0)
ax1.set_ylim(0)
ax1.legend(loc=2)
# Making inset for zoomed in portion
ax2 = plt.axes([0,0,1,1])
ip = InsetPosition(ax1, [0.38,0.35,0.4,0.6])
ax2.set_axes_locator(ip)
maxV = 0
minV = 100
mark_inset(ax1, ax2, loc1=1, loc2=3, fc="none", ec='0.5')
for i in range(len(CL)):
    V0 = np.array(V[i])
    I0 = np.array(I[i])
    point1 = find_nearest(V0, 1.3)
    point2 = find_nearest(V0, 1.55)
    ind1 = int(np.where(V0 == point1)[0])
    ind2 = int(np.where(V0 == point2)[0])
    
    if minV > point1:
        minV = point1
    if maxV < point2:
        maxV = point2

    ax2.scatter(V0[0:ind2], I0[0:ind2], s = 3, color = 'C' + str(i))#, label = '{:.1f} mm, {:.2f} C'.format(CL[i],T[i]))
    ax2.plot(V0[0:ind2], I0[0:ind2], color = 'C' + str(i), label = '{:.1f} mm, {:.2f} C'.format(CL[i],T[i]))

ax2.set_ylim(0)
ax2.set_xlim(minV, maxV)
plt.savefig(plot_dir + 'IVcurve.pdf')


# IL Curve
fig, ax3 = plt.subplots()
epsilon = 0.001     # error of spacing between power points for best-fit line
slope_V = []
int_V = []
for i in range(len(CL)):
    I0 = np.array(I[i])
    L0 = np.array(L[i])
    ax3.scatter(I0, L0, s = 3, color = 'C' + str(i), label = '{:.1f} mm, {:.2f} C'.format(CL[i],T[i]))

    # Making best-fit line based on spacing of power points
    ind3 = 0
    for j in range(len(I0)-1):
        if abs(L0[j+1]-L0[j]) > epsilon:
            ind3 = j
            break
    slope, intercept = best_fit(I0[ind3:],L0[ind3:])
    slope_V.append(slope)
    int_V.append(intercept)

    rgrsn_line = [(slope*x)+intercept for x in np.asarray(I0)]
    ax3.plot(I0, rgrsn_line, color = 'C' + str(i), alpha = 0.5)

ax3.set_xlabel('Current (A)')
ax3.set_ylabel('Optical Power (V)')
ax3.axvline(0, color = 'grey', alpha = 0.5)
ax3.axhline(0, color = 'grey', alpha = 0.5)
ax3.set_xlim(1,2)
ax3.set_ylim(0)
ax3.legend(loc = 2)


P = V_to_P(L)
Pmin = V_to_P(0)
Pmax = V_to_P(1)

ax4 = ax3.twinx()
ax4.scatter(I[0], P[0], s = 0)
ax4.set_ylim(Pmin, Pmax)
ax4.set_ylabel('Optical Power (mW)', rotation = 90)

plt.savefig(plot_dir + 'ILcurve.pdf')




# ANALYSIS SECTION
CL = np.array(CL)
CL_uniq = np.unique(CL)
slope_V = np.array(slope_V)
int_V = np.array(int_V)
slope_P = V_to_P(slope_V) * 1e-3 # Back to W/A

q = 1.602176634e-19  # Charge of e (C)
h = 6.62607015e-34   # Planck (J s)
c = 3e8              # Speed of light (m/s)
lamda = 800e-9       # Wavelength of emitted light (m)
nu = c/lamda         # Freq of light (1/s)

nd = (q/(h*nu))*slope_P  # FIXME: NEED TO FIGURE OUT ACTUAL POWER OUTPUT FROM INT SPHERE

nd_15 = []
nd_30 = []
for i in range(len(T)):
    if '15' in str(T[i]):
        nd_15.append(nd[i])
        nd_30.append(nd[i+1])

nd_15 = np.array(nd_15)
nd_30 = np.array(nd_30)
print(CL_uniq)
print(nd_15)


plt.figure()
plt.scatter(CL_uniq, 1/nd_15, s = 10, color = 'C0') 
plt.scatter(CL_uniq, 1/nd_30, s = 10, color = 'C1') 

slope_15, intercept_15 = best_fit(CL_uniq, 1/nd_15)
rgrsn_line_15 = [(slope_15*x)+intercept_15 for x in np.asarray(np.arange(0,5))]
plt.plot(np.arange(0,5), rgrsn_line_15, color = 'C0', linestyle = '--', alpha = 0.5, label = 'T = 15 C')

slope_30, intercept_30 = best_fit(CL_uniq, 1/nd_30)
rgrsn_line_30 = [(slope_30*x)+intercept_30 for x in np.asarray(np.arange(0,5))]
plt.plot(np.arange(0,5), rgrsn_line_30, color = 'C1', linestyle = '--', alpha = 0.5, label = 'T = 30 C')

plt.xlabel('Cavity Length, L (mm)')
plt.ylabel(r'(Diff. Quantum Efficiency)$^{-1}$, $\eta_d^{-1}$')
plt.legend()
plt.xlim(0, 3.5)
plt.ylim(0)

ni = np.array([1/intercept_15, 1/intercept_30])

R = 0.33            # Reflectance in LD
alpha = np.array([slope_15*ni[0]*np.log(1/R), slope_30*ni[1]*np.log(1/R)])


for i in range(len(CL)):
    print('\n For CL = {:.1f} mm, T = {:.2f} C \n'.format(CL[i], T[i]))
    print('Threshold Curr: Ith = {} A'.format(-int_V[i]/slope_V[i]))
    print('{:<10s}{:>4s}{:^2s}{:<}')
    print('Diff. Quant. Eff: nd = {}'.format(nd[i]))
    print('Injection Eff: ni = {}'.format(ni[i%2]))
    print('Net Internal Optical Loss: alpha = {}'.format(alpha[i%2]))

plt.show()