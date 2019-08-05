from __future__ import print_function

from mpl_toolkits.mplot3d import axes3d
from matplotlib import cm
import matplotlib.pyplot as plt
import numpy as np
import time
import keyboard
from threading import Thread
import linecache

class Plot_flow():

    def __init__ (self, rx_num, tx_num):

        print ("Plot 3D")

        self.fig = None
        self.ax = None

        self.rx_num = rx_num
        self.tx_num = tx_num
        # Make the X, Y meshgrid.
        xs = np.linspace(0, tx_num - 1, tx_num)
        ys = np.linspace(0, rx_num - 1, rx_num)
        self.X, self.Y = np.meshgrid(xs, ys)
        
        self.wframe = None
        
    def plot_function(self, frame_array):

        if (int(frame_array.shape[0]) != self.rx_num or int(frame_array.shape[1]) != self.tx_num):
            print ("Size error ", "rawdata size = ", frame_array.shape[0], frame_array.shape[1])
            print ("Size error ", "RX/TX   size = ", self.rx_num, self.tx_num)
            return
        
        if self.fig == None:
            self.fig = plt.figure()
            self.ax = self.fig.add_subplot(111, projection='3d')
        
        # If a line collection is already remove it before drawing.
        if self.wframe:
            self.ax.collections.remove(self.wframe)

        self.wframe = self.ax.plot_wireframe(self.X, self.Y, frame_array, rstride = 1, cstride = 1, cmap = cm.Reds) #rstride & cstride -> Downsampling
        #self.wframe = self.ax.plot_surface(self.X, self.Y, frame_array, rstride = 1, cstride = 1, cmap = cm.Reds) #https://matplotlib.org/users/colormaps.html
        
        plt.pause(0.001)
        #plt.show()
        
        #self.fig.waitforbuttonpress()    

    def close(self):
        plt.close()
        self.fig = None
        self.ax = None
    
class Rawdata_plot_mechanism():

    def __init__ (self, filename):

        self.tx_num = 0
        self.rx_num = 0
        self.line_cursor = 0
        self.filename = filename
        self.file_lines = 0
        
        self.rawdata_array = []
        self.frame_list = []
        
        #check file available
        try:
            with open(self.filename, 'r') as f:
                for l in f.readlines():
                    self.file_lines += 1
        except:
            print ("File open error")
            return
        
        self.get_rx_tx_num()
        self.plt_obj = Plot_flow(self.rx_num, self.tx_num)
        
        self.thread_plot_thread = Thread(target = self.get_keyboard_event, args = ([self.plt_obj, self.search_rawdata]))

    def auto_animation_drawing(self):

        frame_array = None
        frame_list = []

        #read raw data
        with open(self.filename, 'r') as f:
            for line in f.readlines():

                #Split to single data
                data_row = line.split()
                assign_list = []
                
                #Transfer data to int data only
                for data in data_row:
                    try:
                        assign_list.append(int(data))
                    except:
                        pass
                             
                #Change type as np.array
                if len(assign_list) != 0:
                    if len(assign_list) > self.tx_num:
                        assign_list.pop()
                    frame_list.append(assign_list)
                    
                #Plot
                if len(assign_list) == 0 and frame_list != []:
                    if len(frame_list) > self.rx_num:
                        frame_list.pop()
                    frame_array = np.array(frame_list)
                    #print (frame_array)
                    self.plt_obj.plot_function(frame_array)
                    frame_list = []

        self.plt_obj.close()

    def parse_raw_data(self):

        frame_array = None
        frame_list = []
        raw_data = ""
        
        cur_line = self.line_cursor

        line = linecache.getline(self.filename, cur_line)
        data_row = line.split()
        
        while len(data_row) > 0:

            #Split to single data
            line = linecache.getline(self.filename, cur_line)

            raw_data += line
            data_row = line.split()
            assign_list = []
                            
            #Transfer data to int data only
            for data in data_row:
                try:
                    assign_list.append(int(data))
                except:
                    pass
                                
            #Change type as np.array
            if len(assign_list) != 0:
                if len(assign_list) > self.tx_num:
                    assign_list.pop()
                frame_list.append(assign_list)
                                
            #get raw data
            if len(assign_list) == 0 and frame_list != []:
                if len(frame_list) > self.rx_num:
                    frame_list.pop()
                frame_array = np.array(frame_list)
                #print (frame_array)
                #print (frame_list)
                break
                            
            cur_line += 1
            
        return frame_array, raw_data
            
    def search_rawdata(self, direction):

        frame_array = []
        frame_list = []
        
        if direction == 'previous':
            self.line_cursor -= 1
            
            while self.line_cursor >= 0:
                line = linecache.getline(self.filename, self.line_cursor)
                data_row = line.split()
                
                if len(data_row) > 0 and data_row[0].find('[00]') >= 0:
                    frame_array, frame_list = self.parse_raw_data()
                    #print (frame_array)
                    break
                    
                self.line_cursor -= 1

            #avoid less than 0
            if self.line_cursor < 0:
                self.line_cursor = 0
            
        if direction == 'forward':
            self.line_cursor += 1
            
            while self.line_cursor <= self.file_lines:
                line = linecache.getline(self.filename, self.line_cursor)
                data_row = line.split()
                
                if len(data_row) > 0 and data_row[0].find('[00]') >= 0:
                    frame_array, frame_list = self.parse_raw_data()
                    #print (frame_array)
                    break
                self.line_cursor += 1
                
            #avoid over max line
            if self.line_cursor > self.file_lines:
                self.file_lines = self.line_cursor

        return frame_array, frame_list
                
    def get_rx_tx_num(self):
        status = 0
        with open(self.filename, 'r') as f:
            for line in f.readlines():
                data_row = line.split()
                if len(data_row) > 0:
                    #get TX NUM
                    if data_row[-1].find('[') >= 0 and data_row[-1].find(']') > 0:
                        tx = (int(data_row[-1][1:-1]))
                        self.tx_num = tx
                        status += 1
                        
                    #get RX NUM
                    if data_row[0].find('[') >= 0 and data_row[0].find(']') > 0:
                        rx = (int(data_row[0][1:-1]))
                        if rx > self.rx_num:
                            self.rx_num = rx
                if status == 2:
                    break
                
    def dynamic_plot(self):
        self.line_cursor = 0
        linecache.clearcache()
        self.thread_plot_thread.start()        
        
    def get_keyboard_event(self, plt_obj, search_rawdata):

        while True:
            try:
                if keyboard.is_pressed('4'):
                    self.rawdata_array, rawdata = search_rawdata('previous')
                    print (rawdata)
                    time.sleep(0.1)
                elif keyboard.is_pressed('6'):
                    self.rawdata_array, rawdata = search_rawdata('forward')
                    print (rawdata)
                    time.sleep(0.1)
                elif keyboard.is_pressed('esc'):
                    print ("Exit")
                    break
                else:
                    if self.rawdata_array != []:
                        plt_obj.plot_function(self.rawdata_array) #keep drawing
                
            except:
                print ("break")
                break

    def __del__(self):
        self.plt_obj.close()
        
def main():
    RawPlot_obj = Rawdata_plot_mechanism("20190625_11-02-26.txt")
    #RawPlot_obj.auto_animation_drawing()
    RawPlot_obj.dynamic_plot()
    pass
if __name__ == "__main__":
    main()
