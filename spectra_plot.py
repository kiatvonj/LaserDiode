
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
    wavelength = np.loadtxt(filename,dtype=float,delimiter=',',skiprows=33,usecols=0,max_rows=3645)
    intensity = np.loadtxt(filename,dtype=float,delimiter=',',skiprows=33,usecols=1,max_rows=3645)
    return [wavelength,intensity]

def smooth(lamdas,intens,smooth_check):
    # lamdas, intens = read_spectrum_data(filename)
    # plt.plot(lamdas,intens/max(intens))
    # plt.xlim(760,840)
    # plt.show(block=True)
    
    # smooth_check = input('Does this spectrum look like it needs smoothing? (Y/N)\n')
    # FIXME: find a way to loop through the smoothing multiple times until the user is satisfied
    if smooth_check == 'Y':
        new_lamdas = [] # blue spectrum was very noisy in a spiky way, so I'm averaging every
                  #  two points
        new_intens = []
        for i in range(len(lamdas)//3):
            wl_foo = (lamdas[3*i]+lamdas[3*i+1]+lamdas[3*i+2])/3
            new_lamdas.append(wl_foo)
            val_foo = (intens[3*i]+intens[3*i+1]+intens[3*i+2])/3
            new_intens.append(val_foo)
        return [np.array(new_lamdas), np.array(new_intens)]
    elif smooth_check == 'N':
        return [lamdas,intens]


def plot_spectra(filename, scale_factor = 1):   
    lamdas, intens = read_spectrum_data(filename)
    
    s = filename.split('_')
    label1 = 'L='+s[-3]+'mm, T='+s[-2]+'°C, I='+s[-1][:4]+'A'
    label = 'I='+s[-1][:4]+' A'
    
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
    
    print('For '+label1+':')
    print('FWHM:',round(FWHM,2))
    print('Peak at',round(lamda_peak,2))
    print('\n')
    # plt.title('FWHM:',FWHM)
    
    plt.xlabel('Wavelength (nm)')
    plt.ylabel('Intensity (a.u.)')
    plt.xlim(780,820)
    plt.ylim(0,3.1)
    # plt.tick_params(left=False)
    plt.yticks(ticks = [])
    plt.legend(loc='upper left')
    return FWHM

plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams.update({'font.size': 9})
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300

# FWHMs = []
# for i in os.listdir('data_spectra'):
#     FWM = plot_spectra('data_spectra/'+i)
plot_directory = 'plots/'

file_list = os.listdir('data_spectra')
file_list.sort()

for i in file_list:
    if i == '.DS_Store':
        file_list.remove(i)

plt.figure(figsize = (3.5, 3))
for i in range(len(file_list[:3])):
    plot_spectra('data_spectra/'+file_list[i],i+1)
    plt.savefig(plot_directory+'Spectra_2.00_15.00.pdf', bbox_inches='tight')
    plt.savefig(plot_directory+'Spectra_2.00_15.00.png', bbox_inches='tight')
    
plt.figure(figsize = (3.5, 3))
for i in range(len(file_list[3:6])):
    plot_spectra('data_spectra/'+file_list[i+3],i+1)
    plt.savefig(plot_directory+'Spectra_2.00_30.00.pdf', bbox_inches='tight')
    plt.savefig(plot_directory+'Spectra_2.00_30.00.png', bbox_inches='tight')


plt.figure(figsize = (3.5, 3))
for i in range(len(file_list[6:9])):
    plot_spectra('data_spectra/'+file_list[i+6],i+1)
    plt.savefig(plot_directory+'Spectra_3.00_15.00.pdf', bbox_inches='tight')
    plt.savefig(plot_directory+'Spectra_3.00_15.00.png', bbox_inches='tight')

    
plt.figure(figsize = (3.5, 3))
for i in range(len(file_list[9:12])):
    plot_spectra('data_spectra/'+file_list[i+9],i+1)
    plt.savefig(plot_directory+'Spectra_3.00_30.00.pdf', bbox_inches='tight')
    plt.savefig(plot_directory+'Spectra_3.00_30.00.png', bbox_inches='tight')

# FIXME find a way to add an option to smooth spectra. Maybe iterate through each in
#       the directory and prompt the user (Does this need smoothing? (Y/N) )



# make a nice-looking plot to highlight linewidth differences as current increases
#   offset the center of each spectrum

plt.figure(figsize = (3.5, 3))

lamdas, below_thresh = read_spectrum_data('data_spectra/'+file_list[9])
at_thresh = read_spectrum_data('data_spectra/'+file_list[10])[1]
above_thresh = read_spectrum_data('data_spectra/'+file_list[11])[1]

below_lamdas, below_thresh = smooth(lamdas,below_thresh,'Y')
# below_lamdas, below_thresh = smooth(below_lamdas,below_thresh,'Y')

plt.plot(below_lamdas-40,below_thresh/max(below_thresh)*1, label='< Threshold')
plt.plot(lamdas,at_thresh/max(at_thresh)*1.5, label = '= Threshold')
plt.plot(lamdas+40,above_thresh/max(above_thresh)*2, label = '> Threshold')
plt.yticks(ticks = [])
plt.xticks(ticks = [])
plt.ylabel('Intensity (a.u.)')
plt.xlabel('Wavelength (shifted a.u.)')
plt.xlim(700,900)
plt.ylim(0,2.1)
plt.legend()
# plt.savefig(plot_directory+'Example_Spectra.pdf', bbox_inches='tight')
# plt.savefig(plot_directory+'Example_Spectra.png', bbox_inches='tight')











