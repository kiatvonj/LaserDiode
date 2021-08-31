import numpy as np
import matplotlib.pyplot as plt
import time 
import os
from numpy import genfromtxt
import argparse


parser = argparse.ArgumentParser()
parser.add_argument("-L", "--cavlen", type=float, help="Specify cavity length for data file (in mm)", required=True)
parser.add_argument("-T", "--temp", type=float, help="Specify temperature for data file (in C)", required=True)
args = parser.parse_args()

CL = args.cavlen
T = args.temp


data_dir = './data_CavLen_Temp/'
data_file = data_dir + 'IVL_{0:.2f}_{1:.2f}.csv'.format(CL, T)
data = genfromtxt(data_file, delimiter = ',', skip_header = 1)

plot_dir = './plots/'
if not os.path.exists(plot_dir):
    os.mkdir(plot_dir)


I = data[:,1]
V = data[:,0]
L = data[:,2]

plt.rcParams["font.family"] = "Times New Roman"

plt.figure('IV Curve')
plt.plot(V, I, 'k.')
plt.xlabel('Voltage (V)')
plt.ylabel('Current (A)')
plt.savefig(plot_dir + 'IV_{0:.2f}_{1:.2f}.pdf'.format(CL, T))


plt.figure()
plt.plot(I, L, 'k.')
plt.xlabel('Current (A)')
plt.ylabel('Optical Power (V)')
plt.savefig(plot_dir + 'IL_{0:.2f}_{1:.2f}.pdf'.format(CL, T))

plt.show()
