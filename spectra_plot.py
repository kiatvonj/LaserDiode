
"""
Playing around with nLight laser diode spectra for PHYS 610 Advanced Lab

@author: samuelschonsberg
"""

import numpy as np
import matplotlib.pyplot as plt
import os

def find_nearest(array, value): # returns an index nearest to specified value in an array
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx


def read_spectrum_data(filename):
    wavelength = np.loadtxt(filename,dtype=float,delimiter=',',skiprows=33,usecols=0,max_rows=3648)
    intensity = np.loadtxt(filename,dtype=float,delimiter=',',skiprows=33,usecols=1,max_rows=3648)
    return [wavelength,intensity]

# def smooth_check(filename):
#     lamdas, intens = read_spectrum_data(filename)
#     plt.plot(lamdas,intens/max(intens))
#     plt.xlim(760,840)
#     plt.show(block=True)
    
#     smooth_check = input('Does this spectrum look like it needs smoothing? (Y/N)\n')
#     # FIXME: find a way to loop through the smoothing multiple times until the user is satisfied
#     if smooth_check == 'Y':
#         new_lamdas = [] # blue spectrum was very noisy in a spiky way, so I'm averaging every
#                  #  two points
#         new_intens = []
#         for i in range(len(lamdas)//3):
#             wl_foo = (lamdas[3*i]+lamdas[3*i+1]+lamdas[3*i+2])/3
#             new_lamdas.append(wl_foo)
#             val_foo = (intens[3*i]+intens[3*i+1]+intens[3*i+2])/3
#             new_intens.append(val_foo)
#         return [np.array(new_lamdas), np.array(new_intens)]
#     elif smooth_check == 'N':
#         return [lamdas,intens]
#     else:
#         print('Bad user, enter Y or N')
#         return

def plot_spectra(filename, scale_factor = 1):   
    lamdas, intens = read_spectrum_data(filename)
    
    s = filename.split('_')
    label = 'L='+s[-3]+'mm, T='+s[-2]+'°C, I='+s[-1][:4]+'A'
    
    plt.plot(lamdas,intens/max(intens) * scale_factor,label=label)
    # plt.plot(lamdas,intens/max(intens),'k-')
    # plt.axhline(0.5,color='red',linestyle='--')
    
    
    idx_max = find_nearest(intens, max(intens))
    lamda_peak = lamdas[idx_max]
    plt.axvline(lamdas[idx_max],linestyle='--',color = 'C'+str(scale_factor-1))
    # calculatin the FWHM
    idx1 = 0
    for i in intens/max(intens):
        if i < 0.5:
            idx1 += 1
        else:
            break
    
    idx2 = 0
    for i in reversed(intens/max(intens)):
        if i < 0.5:
            idx2 += 1
        else:
            break
    
    FWHM = lamdas[-idx2] - lamdas[idx1]
    
    print('FWHM:',round(FWHM,2))
    print('Peak at',round(lamda_peak,2))
    # plt.title('FWHM:',FWHM)
    plt.rcParams["font.family"] = "Times New Roman"
    plt.xlabel('Wavelength (nm)')
    plt.ylabel('Intensity (a.u.)')
    plt.xlim(760,840)
    # plt.tick_params(left=False)
    plt.yticks(ticks = [])
    plt.legend()
    return FWHM

# FWHMs = []
# for i in os.listdir('data_spectra'):
#     FWM = plot_spectra('data_spectra/'+i)

file_list = os.listdir('data_spectra')
file_list.sort()

plt.figure()
for i in range(len(file_list[:3])):
    plot_spectra('data_spectra/'+file_list[i],i+1)
    
plt.figure()
for i in range(len(file_list[3:6])):
    plot_spectra('data_spectra/'+file_list[i+3],i+1)

plt.figure()
for i in range(len(file_list[6:9])):
    plot_spectra('data_spectra/'+file_list[i+6],i+1)
    
plt.figure()
for i in range(len(file_list[9:12])):
    plot_spectra('data_spectra/'+file_list[i+9],i+1)
# FIXME find a way to add an option to smooth spectra. Maybe iterate through each in
#       the directory and prompt the user (Does this need smoothing? (Y/N) )

