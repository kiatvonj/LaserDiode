import numpy as np
import matplotlib.pyplot as plt
import os
import re
from numpy import genfromtxt

plot_dir = './plots/'
if not os.path.exists(plot_dir):
    os.mkdir(plot_dir)

data_dir = './data_CavLen_Temp/'

CL = []
T = []

I = []
V = []
L = []

for name in os.listdir(data_dir):
    if 'IVL_' in name:
        params = re.findall("\d+\.\d+", name)
        CL.append(float(params[0]))
        T.append(float(params[1]))


for i in range(len(CL)):
    data_file = data_dir + 'IVL_{0:.2f}_{1:.2f}.csv'.format(CL[i], T[i])
    data = genfromtxt(data_file, delimiter = ',', skip_header = 1)
    I.append(data[:,1])
    V.append(data[:,0])
    L.append(data[:,2])
    
plt.rcParams["font.family"] = "Times New Roman"

plt.figure('IV Curve')
for i in range(len(CL)):
    plt.scatter(V[i], I[i], s = 3, color = 'C' + str(i))#, label = '{:.1f} mm, {:.2f} C'.format(CL[i],T[i]))
    plt.plot(V[i], I[i], color = 'C' + str(i), label = '{:.1f} mm, {:.2f} C'.format(CL[i],T[i]))
plt.xlabel('Voltage (V)')
plt.ylabel('Current (A)')
# plt.grid()
plt.axvline(0, color = 'grey', alpha = 0.5)
plt.axhline(0, color = 'grey', alpha = 0.5)
plt.legend()
plt.savefig(plot_dir + 'IVcurve.pdf')


plt.figure()
for i in range(len(CL)):
    plt.scatter(I[i], L[i], s = 3, color = 'C' + str(i), label = '{:.1f} mm, {:.2f} C'.format(CL[i],T[i]))
plt.xlabel('Current (A)')
plt.ylabel('Optical Power (V)')
# plt.grid()
plt.axvline(0, color = 'grey', alpha = 0.5)
plt.axhline(0, color = 'grey', alpha = 0.5)
plt.legend()
plt.savefig(plot_dir + 'ILcurve.pdf')

plt.show()
