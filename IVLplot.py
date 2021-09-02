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
plt.figure()
epsilon = 0.001     # error of spacing between power points for best-fit line
for i in range(len(CL)):
    I0 = np.array(I[i])
    L0 = np.array(L[i])
    plt.scatter(I0, L0, s = 3, color = 'C' + str(i), label = '{:.1f} mm, {:.2f} C'.format(CL[i],T[i]))

    # Making best-fit line based on spacing of power points
    ind3 = 0
    for j in range(len(I0)-1):
        if abs(L0[j+1]-L0[j]) > epsilon:
            ind3 = j+1 
            break
    slope, intercept = best_fit(I0[ind3:],L0[ind3:])

    rgrsn_line = [(slope*x)+intercept for x in np.asarray(I0)]
    plt.plot(I0, rgrsn_line, color = 'C' + str(i), alpha = 0.5)

    print('\n For CL = {:.1f} mm, T = {:.2f} C'.format(CL[i], T[i]))
    print('Threshold Ith = {} A \n'.format(-intercept/slope))

plt.xlabel('Current (A)')
plt.ylabel('Optical Power (V)')
plt.axvline(0, color = 'grey', alpha = 0.5)
plt.axhline(0, color = 'grey', alpha = 0.5)
# plt.xlim(1,2)
plt.ylim(0)
plt.legend(loc = 2)
plt.savefig(plot_dir + 'ILcurve.pdf')


plt.show()

