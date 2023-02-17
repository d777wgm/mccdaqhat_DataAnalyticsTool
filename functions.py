from threading import Thread, Event
import threading
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



def input_thread(a_list):
	input()
	a_list.append(True)


def read_thread(a_list, data):
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
            new_index = 0
            myArray = [] # create an empty array
            for i in range(0, totalSamples, num_channels):
                myArray.append([])
                #myArray.append([])  # add a row to the array (COLUMN)
                for j in range(num_channels):
                    # append a num_channels of data to the array (ROW)
                    myArray[new_index].append(read_result.data[i + j])
                new_index += 1
            
            for row in myArray:
                data.append(row)

        if a_list:
            hat.a_in_scan_stop()
            hat.a_in_scan_cleanup()
            break
        sleep(0.1)


def save_data(data, fileDateTime):
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
    csvfile = open(fileDateTime, "w+")
    csvwriter = csv.writer(csvfile)
    csvwriter.writerows(csv_header)
    csvwriter.writerows(data)  # Write the array to file
    csvfile.flush
    csvfile.close()

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
        axs[0].plot(df['V1'], marker='x')
        axs[1].plot(df['V2'])
        #axs[2].plot(df['time'], df['voltage2'])
        #axs[3].plot(df['time'], df['power'])
        #axs[4].plot(df['time'], df['wire_speed'])
        for ax in axs:
            ax.label_outer()
    plt.show()
