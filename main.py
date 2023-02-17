from  functions import input_thread,read_thread,plot_data,save_data
import os
from config import *

from threading import Thread, Event
import threading
from time import sleep
import numpy as np
from config import channels

EDITOR = os.environ.get('EDITOR','vim') #that easy!

def main():
    while True:
        a_list = []
        num_channels = len(channels)
        
        keyboard_input = input('C to CHANGE config.py \nENTER to START scan \nP to PLOT data')
        os.system('clear')
        if keyboard_input == "":
            t_input = Thread(target=input_thread, args=(a_list, ), name = 'input_thread')
            t_input.start()
            t_measurement = Thread(target=read_thread, args=(a_list,), name = 'measurement_thread')
            t_measurement.start()
        
        if keyboard_input == "p":
            plot_data()
        
        if keyboard_input =='c':
            call([EDITOR, 'config.py'])

            
        print('ENTER to STOP scan')
        
        while not a_list:
            sleep(1)
        
    
if __name__ == '__main__':
    main()
