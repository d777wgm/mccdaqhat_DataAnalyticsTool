from  functions import input_thread,read_thread,plot_data,save_data
import os
from config import *
from datetime import datetime, timedelta

EDITOR = os.environ.get('EDITOR','vim') #that easy!

def main():
    while True:
        a_list = []
        data = []
        fileDateTime = datetime.strftime(datetime.now(), "%Y_%B_%d_%H%M%S")
        fileDateTime = mypath + "/" + fileDateTime + ".csv"
        
        keyboard_input = input('C to CHANGE config.py \nENTER to START scan \nP to PLOT data')
        os.system('clear')
        if keyboard_input == "":
            t_input = Thread(target=input_thread, args=(a_list, ), name = 'input_thread')
            t_input.start()
            t_measurement = Thread(target=read_thread, args=(a_list,data,), name = 'measurement_thread')
            t_measurement.start()
        
        if keyboard_input == "p":
            plot_data()
        
        if keyboard_input =='c':
            call([EDITOR, 'config.py'])

            
        print('ENTER to STOP scan')
        
        while not a_list:
            sleep(1)
            
        print('File saved at: '+ fileDateTime + '\n')
        save_data(data, fileDateTime)
        
    
if __name__ == '__main__':
    main()
