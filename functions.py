from time import sleep
from daqhats import mcc118, OptionFlags, HatIDs, HatError
from daqhats_utils import select_hat_device, enum_mask_to_string, \
    chan_list_to_mask
from datetime import datetime, timedelta
import os
import csv  # this is the import to make csv file creation simple.
import errno
import pandas as pd
import matplotlib.pyplot as plt
from config import *
import sys, tempfile, os
from subprocess import call
import numpy as np
#from scipy.fft import fft, fftfreq


def input_thread(a_list):
	input()
	a_list.append(True)



def read_thread(a_list):
    address = select_hat_device(HatIDs.MCC_118)
    hat = mcc118(address)
    channel_mask = chan_list_to_mask(channels)
    num_channels = len(channels)
    samples_per_channel = 0
    options = OptionFlags.CONTINUOUS
    total_samples_read = 0
    read_request_size = READ_ALL_AVAILABLE
    timeout = 5.0
    hat.a_in_scan_start(channel_mask, samples_per_channel, scan_rate, options)
    data = np.empty((0,num_channels+1), float)
    time_counter = 0
    while True:
        read_result = hat.a_in_scan_read_numpy(read_request_size, timeout)
        actual_scan_rate = hat.a_in_scan_actual_rate(num_channels, scan_rate)
        # Check for an overrun error
        if read_result.hardware_overrun:
            print('\n\nHardware overrun\n')
            break
        elif read_result.buffer_overrun:
            print('\n\nBuffer overrun\n')
            break

        samples_read_per_channel = int(len(read_result.data) / num_channels)
        total_samples_read += samples_read_per_channel
        totalSamples = len(read_result.data)

        if samples_read_per_channel > 0:
            index = samples_read_per_channel * num_channels - num_channels
            myArray = np.empty((0, num_channels+1), float)
            for i in range(0, totalSamples, num_channels):
                row = np.empty((0, num_channels), float)
                row = np.append(row, time_counter+1.0/scan_rate)
                for j in range(num_channels):
                    row = np.append(row, read_result.data[i + j])
                time_counter += 1.0/scan_rate
                myArray = np.concatenate((myArray, [row]), axis=0)

            data = np.concatenate((data, myArray), axis=0)

        if a_list:
            hat.a_in_scan_stop()
            hat.a_in_scan_cleanup()
			save_data(data)
            break
            sleep(0.1)

		
def save_data(data):
    try:
        if os.path.exists(basepath):
            if not (os.path.exists(mypath)):
                os.mkdir(mypath)
        else:
            os.mkdir(basepath)
            os.chdir(basepath)
            os.mkdir(mypath)
    except OSError as exc:
        raise

    os.chdir(mypath)
    fileDateTime = datetime.strftime(datetime.now(), "%Y_%B_%d_%H%M%S")
    fileDateTime = mypath + "/" + fileDateTime + ".csv"
    np.savetxt(fileDateTime, X= data, delimiter = ',', header = 't,V1,V2', comments ='')
    print('File saved at: '+ fileDateTime + '\n')


def plot_data():
    print('files in working dir: \n')
    files = [f for f in os.listdir(mypath) if os.path.isfile(os.path.join(mypath,f))]
    files.sort()
    print('\n'.join('{}: {}'.format(*k) for k in enumerate(files)))
    selected_files = input('Select files you want to plot --> comma separated numbers ')
    selected_files = selected_files.split(",")
    fig = plt.figure()
    gs = fig.add_gridspec(2,hspace=0.1)
    axs = gs.subplots(sharex=True)
    fig.suptitle('Sharing both axes')
    for number in selected_files:
        df = pd.read_csv(mypath + "/"+files[int(number)])
        axs[0].plot(df['t'],df['V1'], marker='x')
        axs[1].plot(df['t'],df['V2'])
        #axs[2].plot(df['time'], df['voltage2'])
        #axs[3].plot(df['time'], df['power'])
        #axs[4].plot(df['time'], df['wire_speed'])
        for ax in axs:
            ax.label_outer()
    plt.show()
    
def live_fft(data, scan_rate):
	while True:
		N = 100
		T = 1.0/scan_rate
		t = np.linespace(0.0,N*T, N, endpoint=False)
		y = data[:]
		
		
	
	
