from __future__ import print_function

import wx
import adb
import re
import time
from time import sleep
from threading import Thread
import os
import sys

sys.path.append('./include')
from Replace_bot import Replace_section_flow

'''================================
            DEFINE
================================'''
PATH_OPCODE = [ "REG_PATH",
                "DIAG_PATH",
                "HX_FOLDER_PATH",
                "WRITE_REG_NUM",
                "PORT_NUM",
                "OTHER_FUNCTION"]

DEFINE_FILE = "./DEFINE_SETTING"

DIFF_DIAG = 1
DC_DIAG = 2
SRAM_DIFF_DIAG = 11
SRAM_DC_DIAG = 12

'''================================
            Class
================================'''
class Panel_info():

    def __init__(self, adb):
        #Echo command
        self.DIAG_PATH = ''
        self.REG_PATH = ''
        self.HX_FOLDER_PATH = ''
        
        self.setting_path()
        
        self.ECHO_DIAG = "echo %s > " + self.DIAG_PATH
        self.CAT_DIAG = "cat " + self.DIAG_PATH
        
        self.ECHO_WRITE_REGISTER = "echo w:x%s:x%s > " + self.REG_PATH
        self.ECHO_READ_REGISTER = "echo r:x%s > " + self.REG_PATH
        self.CAT_READ_REGISTER = "cat " + self.REG_PATH

        self.PULL_HX_FILE = "adb pull " + self.HX_FOLDER_PATH

        #Local object & variable
        self.adb = adb

        self.diag_raw_data = ""
        self.diag_line = []
        
        self.channel_num = []
        self.raw_data_start = 0
        self.raw_data_end = 0

        self.current_diag = 0
        self._running = True
        self.thread_raw_data = None
        self._switch_raw_data_read_status = True
        
        #Get info & Test connect
        if self.echo_raw_data(1) == True: #get diff info
            print ("Success connect!")
        else:
            print ("Please reconnect usb!")
        diag_trigger = self.ECHO_DIAG % (str(0))
        self.adb.shell(diag_trigger, "SHELL")
        
    def setting_path(self):
        with open(DEFINE_FILE, 'rb') as r:
            for line in r.readlines():
                if line.find("#") >= 0:
                    continue
                l = line.split()
                l = (''.join(l))
                l = l.split('=')
                if len(l) >= 2:
                    if l[0] in PATH_OPCODE:
                        path = l[1]
                        if path[0] != '/':
                            path = '/' + path
                        if path[-1] == '/':
                            path = path[:-1]
                        #Assign path
                        if l[0] == "REG_PATH":
                            self.REG_PATH = path
                        elif l[0] == "DIAG_PATH":
                            self.DIAG_PATH = path
                        elif l[0] == 'HX_FOLDER_PATH':
                            self.HX_FOLDER_PATH = path
                        
    def echo_raw_data(self, diag):
        diag_trigger = self.ECHO_DIAG % (str(diag))
        echo_diag = self.CAT_DIAG

        raw_data = self.adb.shell(diag_trigger, "SHELL")
        raw_data = self.adb.shell(echo_diag, "SHELL")

        #split echo raw data
        self.diag_line = re.split("\n", raw_data)
        self.channel_num = ""
        
        if len(self.diag_line) > 3:
            self.channel_num = [int(i) for i in re.split(",| |\r",self.diag_line[0]) if i.isdigit()] #get the rx tx num
        
            self.raw_data_start = len(self.diag_line[0]) + len(self.diag_line[1]) - 2
            self.raw_data_end = raw_data.find("ChannelEnd")

        #print info
        print ("Panel channel = ", self.channel_num)
        if self.channel_num != "":
            return True
        else:
            return False

    def disable_diag(self):
        diag_trigger = self.ECHO_DIAG % (0)
        self.adb.shell(diag_trigger, "SHELL")

    def pull_hx_file(self):
        feed_back = self.adb.shell(self.PULL_HX_FILE)
        return feed_back

    def read_register(self, reg_address):
        read_reg_info = ""
        reg_address_list = reg_address.split()
        
        #Deal with reg_address without space
        if len(reg_address_list) > 0:
            if len(reg_address_list[0]) == 8:
                reg_address = reg_address_list[0]
            elif len(reg_address_list[0]) == 10 and (reg_address_list[0][0:2] == "0x" or reg_address_list[0][0:2] == "0X"):
                reg_address = reg_address_list[0][2:]
            else:
                reg_address = ""
        else:
            reg_address = ""
            
        if len(reg_address) == 8:
            cmd = self.ECHO_READ_REGISTER % (reg_address)

            self.adb.shell(cmd, "SHELL")
            read_reg_info = self.adb.shell(self.CAT_READ_REGISTER, "SHELL")
            
        return read_reg_info

    def write_register(self, reg_address, write_value):
        read_reg_info = ""
        reg_address_list = reg_address.split()

        print (reg_address_list)
        
        #Deal with reg_address without space
        if len(reg_address_list) > 0:
            if len(reg_address_list[0]) == 8:
                reg_address = reg_address_list[0]
            elif len(reg_address_list[0]) == 10 and (reg_address_list[0][0:2] == "0x" or reg_address_list[0][0:2] == "0X"):
                reg_address = reg_address_list[0][2:]
            else:
                reg_address = ""
        else:
            reg_address = ""
            
        print ("Result:" + reg_address)
        
        #Deal with value for set as 8 digit
        while len(write_value) < 8 and len(write_value) != 0:
            write_value = "0" + write_value

        if len(reg_address) == 8 and len(write_value) != 0:
            cmd = self.ECHO_WRITE_REGISTER % (reg_address, write_value)
            self.adb.shell(cmd, "SHELL")
        
    '''Section for thread
    It should check the adb shell command resource (self.adb.shell)
    The resource should not call at same time'''
    #Loop raw data 
    def loop_run_raw_data(self, diag, Logging_func):
        while self._running == True:
            if self._switch_raw_data_read_status == True:
                raw_data = self.get_raw_data(diag)
                print (raw_data, end='\r')

                Logging_func(raw_data)
                
        self._running = True
        self._switch_raw_data_read_status = True
        
    def get_raw_data(self, diag):
        diag_trigger = self.ECHO_DIAG % (str(diag))
        echo_diag = self.CAT_DIAG

        if self.current_diag != diag:
            raw_data = self.adb.shell(diag_trigger, "SHELL")
            self.current_diag = diag

        raw_data = self.adb.shell(echo_diag, "SHELL")
        
        return raw_data[self.raw_data_start:self.raw_data_end]
    
    #script running
    def running_coordination_script(self, from_list, to_list):
        #exception
        if from_list == None or to_list == None:
            return 0
        
        for i in range(len(from_list)):
            path_cmd = str(from_list[i][0]) + ' ' \
                        + str(from_list[i][1]) + ' ' \
                        + str(to_list[i][0]) + ' ' \
                        + str(to_list[i][1]) + ' '
            cmd = "input swipe " + path_cmd
            self.adb.shell(cmd, "SHELL")
            
    #Section flag api
    def terminate_raw_data(self):
        self._running = False

    def clear_current_diag(self):
        self.current_diag = 0
        
    def switch_read_status(self):
        if self._switch_raw_data_read_status == True:
            self._switch_raw_data_read_status = False
        else:
            self._switch_raw_data_read_status = True
        
class ADB_Frame(wx.Frame):
    
    def __init__(self):
        print ("Create ADB GUI")
        wx.Frame.__init__(self, parent = None, title = "ADB monitor", size = (450, 400))
        self.counter = 1000
        self.device_ip = ""
        self.device_ip_port = ""

        self.OTHER_FUNCTION_DEFINE = 0
        self.WRITE_REG_NUM = 0
        self.PORT_NUM = "5555"
        self.setting_frame()
        
        #Create the adb 
        self.adb_tool = adb

        #check two devices
        devices = (self.adb_tool.shell("adb devices"))
        device_list = devices.split()
        if devices.find("192.168") > 0 and device_list.count("device") > 1:
            print ("Disconnect wifi adb")
            self.adb_tool.shell("adb disconnect")

        self.panel_info = Panel_info(self.adb_tool)
        devices = (self.adb_tool.shell("adb devices"))
        print (devices)
        
        #Create panel
        self.box_sizer = wx.BoxSizer(wx.HORIZONTAL)  #wx.HORIZONTAL wx.VERTICAL        
        self.panel = wx.Panel(self)

        self.bind_component()
        self.component_arrangement()      
        
        self.panel.SetSizerAndFit(self.box_sizer)

        #Thread raw data
        self.data_diag = DIFF_DIAG
        self.logging_flag = False
        self.logging_status = 0
        self.logging_file = None
        self.thread_raw_data = Thread(target = self.panel_info.loop_run_raw_data, args = (self.data_diag, self.Logging_func))

        self.thread_run_script = Thread(target = self.panel_info.running_coordination_script, args = (None, None,))
        
        #Wifi connect
        self.wifi_connect_status = 0 #
        
    def setting_frame(self):
        with open(DEFINE_FILE, 'rb') as r:
            for line in r.readlines():

                l = line.split()
                l = (''.join(l))
                l = l.split('=')
                if len(l) >= 2:
                    if l[0] in PATH_OPCODE:
                        value = l[1]
                        
                        #Assign value
                        if l[0] == "WRITE_REG_NUM":
                            self.WRITE_REG_NUM = int(value)
                        elif l[0] == "PORT_NUM":
                            if (len(value) >= 4):
                                self.PORT_NUM = str(value)
                        elif l[0] == "OTHER_FUNCTION":
                            self.OTHER_FUNCTION_DEFINE = int(value)
    def bind_component(self):        
        #Connect Button        
        self.connect_btn = wx.Button(parent = self.panel, label = "Wifi Connect")
        self.Bind(wx.EVT_BUTTON, self.Btn_connect_func, self.connect_btn)

        self.disconnect_btn = wx.Button(parent = self.panel, label = "Wifi Disconnect")
        self.Bind(wx.EVT_BUTTON, self.Btn_disconnect_func, self.disconnect_btn)

        
        self.connect_again_btn = wx.Button(parent = self.panel, label = "C", size = (25, 25))
        self.Bind(wx.EVT_BUTTON, self.Btn_connect_again_func, self.connect_again_btn)

        #morgen add
        self.driver_version = wx.ToggleButton(parent=self.panel, label="Driver V2", size=(60, 25))
        self.Bind(wx.EVT_TOGGLEBUTTON, self.Btn_driver_version, self.driver_version)

        self.wifi_connect_status_text = wx.StaticText(self.panel, label = "Wifi Disconnect")

        self.wifi_connect_status_text.SetForegroundColour((255, 0, 0))
                
        #Raw data observe        
        self.read_raw_data_btn = wx.Button(parent = self.panel, label = "Read")
        self.Bind(wx.EVT_BUTTON, self.Btn_raw_data_func, self.read_raw_data_btn)

        self.raw_data_diff_rb1 = wx.RadioButton(self.panel, 11, label = 'DIFF', style = wx.RB_GROUP) 
        self.raw_data_dc_rb2 = wx.RadioButton(self.panel, 22, label = 'DC')
        self.raw_data_dc_rb3 = wx.RadioButton(self.panel, 33, label = '')
        self.customize_diag = wx.TextCtrl(  self.panel,
                                            size = (50,25),
                                            style = wx.TE_MULTILINE)
        
        self.Bind(wx.EVT_RADIOBUTTON, self.Raw_data_choose, self.raw_data_diff_rb1)
        self.Bind(wx.EVT_RADIOBUTTON, self.Raw_data_choose, self.raw_data_dc_rb2)
        self.Bind(wx.EVT_RADIOBUTTON, self.Raw_data_choose, self.raw_data_dc_rb3)
        
        self.stop_raw_data_btn = wx.Button(parent = self.panel, label = "Stop",size = (50,25))
        self.Bind(wx.EVT_BUTTON, self.Btn_stop_raw_data_func, self.stop_raw_data_btn)

        self.toggle_sram_read_btn = wx.ToggleButton(parent = self.panel, label = "S", size = (25, 25))
        self.Bind(wx.EVT_TOGGLEBUTTON, self.Raw_data_choose, self.toggle_sram_read_btn)

        self.toggle_logging_btn = wx.ToggleButton(parent = self.panel, label = "log", size = (25, 25))
        self.Bind(wx.EVT_TOGGLEBUTTON, self.Logging_flag_func, self.toggle_logging_btn)

        #Register write        
        self.register_write_btn_list = {}
        for i in range(self.WRITE_REG_NUM):
            bt = wx.Button(parent = self.panel, label = "Register Write")
            address_obj = wx.TextCtrl(  self.panel,
                                        size = (160,26),
                                        style = wx.TE_MULTILINE)
            value_obj = wx.TextCtrl(    self.panel,
                                        size = (160,26),
                                        style = wx.TE_MULTILINE)

            self.register_write_btn_list[bt.Id] = {'address'    : address_obj,
                                                   'value'      : value_obj,
                                                   'bt'         : bt}

            self.Bind(wx.EVT_BUTTON, self.Btn_reg_write_func, bt)
       
        #Register read        
        self.register_read_btn = wx.Button(parent = self.panel, label = "Register Read")
        self.register_read_btn.SetForegroundColour((0, 20, 255))
        self.Bind(wx.EVT_BUTTON, self.Btn_reg_read_func, self.register_read_btn)

        self.reg_address = wx.TextCtrl( self.panel,
                                        size = (160,70),
                                        style = wx.TE_MULTILINE)
        
        self.reg_data = wx.StaticText(  self.panel,
                                        label = "0")
        
        #Other adb command  
        self.power_key_btn = wx.Button(parent = self.panel, label = "Power key")
        self.Bind(wx.EVT_BUTTON, self.Btn_power_key_func, self.power_key_btn)
        self.screen_shot_btn = wx.Button(parent = self.panel, label = "Screen Shot")
        self.Bind(wx.EVT_BUTTON, self.Btn_screen_shot_func, self.screen_shot_btn)
        self.pull_hx_file_btn = wx.Button(parent = self.panel, label = "Pull HX FILE")
        self.Bind(wx.EVT_BUTTON, self.Btn_pull_hx_file_func, self.pull_hx_file_btn)
        self.reboot_btn = wx.Button(parent = self.panel, label = "Reboot")
        self.Bind(wx.EVT_BUTTON, self.Btn_reboot_func, self.reboot_btn)
        self.check_device_btn = wx.Button(parent = self.panel, label = "Check device")
        self.Bind(wx.EVT_BUTTON, self.Btn_check_device_func, self.check_device_btn)
            
        #other function        
        if (self.OTHER_FUNCTION_DEFINE == 1):
            self.swipe_from_page = wx.TextCtrl( self.panel,
                                                size = (100,500),
                                                style = wx.TE_MULTILINE)
            self.swipe_to_page = wx.TextCtrl( self.panel,
                                                size = (100,500),
                                                style = wx.TE_MULTILINE)
            self.swipe_run_btn = wx.Button(parent = self.panel, label = "Run script")
            self.Bind(wx.EVT_BUTTON, self.Btn_run_script_func, self.swipe_run_btn)
        elif self.OTHER_FUNCTION_DEFINE == 2:
        
            self.original_text = wx.TextCtrl( self.panel,
                                                    size = (800,300),
                                                    style = wx.TE_MULTILINE)
            self.replace_text = wx.TextCtrl( self.panel,
                                                    size = (800,300),
                                                    style = wx.TE_MULTILINE)
            self.replace_folder_path = wx.DirPickerCtrl( self.panel,
                                                         wx.ID_ANY,
                                                         wx.EmptyString,
                                                         u"Select a folder",
                                                         (0, 0),
                                                         wx.DefaultSize,
                                                         wx.DIRP_DEFAULT_STYLE)
            self.replace_run_btn = wx.Button(parent = self.panel, label = "Replace")
            self.Bind(wx.EVT_BUTTON, self.Btn_run_replace_func, self.replace_run_btn)
            
    def component_arrangement(self):
        space = 10
        
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.othersizer = wx.BoxSizer(wx.VERTICAL)
        self.advancedsizer = None

        #=====================================Sizer
        hsize = wx.BoxSizer(wx.HORIZONTAL)
        hsize.Add(self.connect_btn, 0, wx.ALIGN_LEFT)
        hsize.AddSpacer(space)
        hsize.Add(self.disconnect_btn, 0, wx.ALIGN_LEFT)
        hsize.AddSpacer(space)
        hsize.Add(self.wifi_connect_status_text, 0, wx.ALIGN_LEFT)
        hsize.AddSpacer(space)
        hsize.Add(self.connect_again_btn, 0, wx.ALIGN_LEFT)
        hsize.Add(self.driver_version, 0, wx.ALIGN_LEFT)#morgen add
        self.sizer.Add(hsize, 0, wx.ALIGN_TOP)
        
        self.sizer.AddSpacer(space)
        #=================
        hsize = wx.BoxSizer(wx.HORIZONTAL)
        hsize.Add(self.read_raw_data_btn, 0, wx.ALIGN_LEFT)
        hsize.AddSpacer(space)
        hsize.Add(self.raw_data_diff_rb1, 0, wx.ALIGN_LEFT)
        hsize.AddSpacer(space * 2)
        hsize.Add(self.raw_data_dc_rb2, 0, wx.ALIGN_LEFT)
        hsize.AddSpacer(space * 2)
        hsize.Add(self.raw_data_dc_rb3, 0, wx.ALIGN_LEFT)
        hsize.Add(self.customize_diag, 0, wx.ALIGN_LEFT)
        hsize.AddSpacer(space)
        hsize.Add(self.stop_raw_data_btn, 0, wx.ALIGN_LEFT)
        hsize.AddSpacer(space)
        hsize.Add(self.toggle_sram_read_btn, 0, wx.ALIGN_LEFT)
        hsize.AddSpacer(space)
        hsize.Add(self.toggle_logging_btn, 0, wx.ALIGN_LEFT)
        self.sizer.Add(hsize, 0, wx.ALIGN_TOP)
        
        self.sizer.AddSpacer(space)
        #=================
        for key in self.register_write_btn_list:
            hsize = wx.BoxSizer(wx.HORIZONTAL)
            hsize.Add((self.register_write_btn_list[key]['bt']), 0, wx.ALIGN_LEFT)
            hsize.AddSpacer(space)
            hsize.Add((self.register_write_btn_list[key]['address']), 0, wx.ALIGN_LEFT)
            hsize.AddSpacer(space)
            hsize.Add((self.register_write_btn_list[key]['value']), 0, wx.ALIGN_LEFT)
            self.sizer.Add(hsize, 0, wx.ALIGN_TOP)
            
            self.sizer.AddSpacer(space)
        #=================
        hsize = wx.BoxSizer(wx.HORIZONTAL)
        hsize.Add(self.register_read_btn, 0, wx.ALIGN_LEFT)
        hsize.AddSpacer(space)
        hsize.Add(self.reg_address, 0, wx.ALIGN_LEFT)
        self.sizer.Add(hsize, 0, wx.ALIGN_TOP)
        
        self.sizer.AddSpacer(space)
        #=================
        hsize = wx.BoxSizer(wx.HORIZONTAL)
        hsize.Add(self.reg_data, 0, wx.ALIGN_LEFT)
        self.sizer.Add(hsize, 0, wx.ALIGN_TOP)

        self.sizer.AddSpacer(space)
        #=====================================othersizer
        self.othersizer.Add(self.power_key_btn, 0, wx.TOP)
        self.othersizer.AddSpacer(space)
        self.othersizer.Add(self.screen_shot_btn, 0, wx.TOP)
        self.othersizer.AddSpacer(space)
        self.othersizer.Add(self.pull_hx_file_btn, 0, wx.TOP)
        self.othersizer.AddSpacer(space)
        self.othersizer.Add(self.reboot_btn, 0, wx.TOP)
        self.othersizer.AddSpacer(space)
        self.othersizer.Add(self.check_device_btn, 0, wx.TOP)
        self.box_sizer.AddSpacer(space)

        #=====================================advancesizer
        if (self.OTHER_FUNCTION_DEFINE == 1):
            self.advancedsizer = wx.BoxSizer(wx.HORIZONTAL)
            self.advancedsizer.Add(self.swipe_from_page, 0, wx.TOP)
            self.advancedsizer.Add(self.swipe_to_page, 0, wx.TOP)
            self.advancedsizer.Add(self.swipe_run_btn, 0, wx.TOP)
        elif self.OTHER_FUNCTION_DEFINE == 2:
            self.advancedsizer = wx.BoxSizer(wx.VERTICAL)
            self.advancedsizer.Add(self.original_text, 0, wx.TOP)
            self.advancedsizer.Add(self.replace_text, 0, wx.TOP)
            self.advancedsizer.Add(self.replace_folder_path, 0, wx.TOP)
            self.advancedsizer.Add(self.replace_run_btn, 0, wx.TOP)

        #=====================================
        self.box_sizer.Add(self.sizer, 0, wx.ALIGN_LEFT)
        self.box_sizer.AddSpacer(space)
        self.box_sizer.Add(self.othersizer, 0, wx.ALIGN_LEFT)
        self.box_sizer.AddSpacer(space)
        if self.advancedsizer != None:
            self.box_sizer.Add(self.advancedsizer, 0, wx.ALIGN_LEFT)
            self.box_sizer.AddSpacer(space)
        
        
    def Btn_connect_func(self, event):
        #print ("Click")
        self.thread_wifi_connect = Thread(target = self.wait_unplugin_connect_func)
        self.thread_wifi_connect.start()
        
    def Btn_disconnect_func(self, event):
        #print ("DisClick")
        print (self.adb_tool.shell("adb disconnect"))
        self.wifi_connect_status_text.SetLabel("Wifi Disconnect")
        self.wifi_connect_status_text.SetForegroundColour((255, 0, 0))
        self.wifi_connect_status = 0
        self.device_ip = ""
        self.device_ip_port = ""
        
    def Btn_connect_again_func(self, event):
        cmd = "adb connect %s:%s" %(self.device_ip, self.PORT_NUM)
        print (cmd)
        response = (self.adb_tool.shell(cmd))
        print (response)
        
    def Btn_raw_data_func(self, event):
        #print ("Click")
        self.panel_info.clear_current_diag()
        self.Raw_data_choose(event)
        
        if self.thread_raw_data.is_alive():
            self.panel_info.terminate_raw_data()
            self.thread_raw_data.join()
            
            self.thread_raw_data = Thread(target = self.panel_info.loop_run_raw_data, args = (self.data_diag, self.Logging_func))
        else:
            self.thread_raw_data = Thread(target = self.panel_info.loop_run_raw_data, args = (self.data_diag, self.Logging_func))
            
        self.thread_raw_data.start()

    def Btn_stop_raw_data_func(self, event):
        if self.panel_info.current_diag != 0:
            self.panel_info.clear_current_diag()
            self.panel_info.switch_read_status()
            
        self.panel_info.disable_diag()
        
    def Raw_data_choose(self, event):

        sram_read_flag = self.toggle_sram_read_btn.GetValue()
        diff_read_flag = self.raw_data_diff_rb1.GetValue()
        dc_read_flag = self.raw_data_dc_rb2.GetValue()
        customize_read_flag = self.raw_data_dc_rb3.GetValue()
        
        #print ("READ SRAME = " + str(sram_read_flag) + ", DIFF read = " + str(diff_read_flag) + ", DC read = " + str(dc_read_flag))

        cus_diag_num = 0
        for i in range(self.customize_diag.GetNumberOfLines()):
            cus_diag_num = self.customize_diag.GetLineText(i)

        try:
            cus_diag_num = int(cus_diag_num)
        except:
            print ("Diag error not number, set diag as 0")
            cus_diag_num = 0
            
        if self.toggle_sram_read_btn.GetValue() == False:
            if diff_read_flag == True:
                self.data_diag = DIFF_DIAG
            elif dc_read_flag == True:
                self.data_diag = DC_DIAG
            elif customize_read_flag == True:
                self.data_diag = cus_diag_num
            else:
                self.data_diag = DIFF_DIAG
        else:            
            if diff_read_flag == True:
                self.data_diag = SRAM_DIFF_DIAG
            elif dc_read_flag == True:
                self.data_diag = SRAM_DC_DIAG
            elif customize_read_flag == True:
                self.data_diag = cus_diag_num
            else:
                self.data_diag = SRAM_DIFF_DIAG
    #morgen add
    def Btn_driver_version(self, event):
        if self.driver_version.GetValue() == True:
            print("Select driver V2")
        else:
            print("Select driver V1")

    def Logging_flag_func(self, event):
        if self.toggle_logging_btn.GetValue() == False:
            self.logging_flag = False
            if self.logging_status == 1:
                self.logging_file.close()
                self.logging_status = 0
        else:
            self.logging_flag = True

    def Logging_func(self, rawdata):

        if self.logging_flag == True:
            #create file
            if self.logging_status == 0: 
                name = time.strftime("%Y%m%d_%H-%M-%S", time.localtime()) + ".txt"
                self.logging_file = open(name, 'wb')
                self.logging_status = 1
            #write logging rawdata
            self.logging_file.write(rawdata)
            
        else:
            if self.logging_status == 1:
                self.logging_file.close()
            self.logging_status = 0
       
    def Btn_reg_read_func(self, event):

        read_reg_info = ""

        for i in range(self.reg_address.GetNumberOfLines()):
            reg_address = (self.reg_address.GetLineText(i)) #get reg address
        
            reg_info = self.panel_info.read_register(reg_address)

            #read only the single line
            reg_info = reg_info[:83] + "\n"
            read_reg_info += reg_info
        
        self.reg_data.SetLabel(read_reg_info)           #output return value
        
    def Btn_reg_write_func(self, event):
            
        reg_address_obj = self.register_write_btn_list[event.Id]['address'] #get reg address
        write_value_obj = self.register_write_btn_list[event.Id]['value']   #get reg address
        n = min(reg_address_obj.GetNumberOfLines(), write_value_obj.GetNumberOfLines())
        for i in range(n):
            reg_address = reg_address_obj.GetLineText(i)
            write_value = write_value_obj.GetLineText(i)
            
            self.panel_info.write_register(reg_address, write_value)

    def Btn_check_device_func(self, event):
        res = self.adb_tool.shell("adb devices")
        print (res)
        
    def Btn_reboot_func(self, event):
        self.adb_tool.shell("adb reboot")
        
    def Btn_power_key_func(self, event):
        self.adb_tool.shell(None, "KEYEVENT", 26)

    def Btn_screen_shot_func(self, event):
        print ("Screen Shot...")
        name = time.strftime("%Y%m%d_%H-%M-%S", time.localtime()) + ".png"
        cmd = "adb wait-for-device shell screencap -p /sdcard/%s" % (name)
        self.adb_tool.shell(cmd)
        cmd = "adb pull /sdcard/%s" % (name)
        self.adb_tool.shell(cmd)
        print ("Screen Shot Done")

    def Btn_pull_hx_file_func(self, event):
        print ("Pull HX File...")
        feed_back = self.panel_info.pull_hx_file()
        print (feed_back)

    def Btn_run_replace_func(self, event):
        folder_path = self.replace_folder_path.GetPath()
        original_text_list = []
        replace_text_list= []
        
        for i in range(self.original_text.GetNumberOfLines()):
            line = self.original_text.GetLineText(i) + '\n'
            original_text_list.append(line)

        for i in range(self.replace_text.GetNumberOfLines()):
            line = self.replace_text.GetLineText(i) + '\n'
            replace_text_list.append(line)

        #Replace bot
        if (os.path.isdir(folder_path) == True):
            obj = Replace_section_flow(original_text_list, replace_text_list)
            obj.loop_file_replace_mechanism(folder_path)
        
    def Btn_run_script_func(self, event):
        print ("Running script...")

        width_pix = 0
        height_pix = 0
        from_list = []
        to_list = []
        
        #check the device is connecting and get resolution
        resolution = (self.adb_tool.shell("adb shell wm size"))
        if resolution.find("null") == True:
            print ("Device is connect!!!")
            return

        #TODO: it chould enable the thread
        resolution = resolution.split()
        resolution = resolution[2].split('x')
        width_pix = int(resolution[0])
        height_pix = int(resolution[1])

        n = min(self.swipe_from_page.GetNumberOfLines(), self.swipe_from_page.GetNumberOfLines())
        #print (n)
        for i in range(n):
            from_coor = self.swipe_from_page.GetLineText(i)
            to_coor = self.swipe_to_page.GetLineText(i)
            from_coor = self.obj_split(from_coor)
            to_coor = self.obj_split(to_coor)

            if len(from_coor) == 2 and len(to_coor) == 2:
                from_x = int(from_coor[0])
                from_y = int(from_coor[1])
                to_x = int(to_coor[0])
                to_y = int(to_coor[1])
                if (from_x >= 0 and from_x < width_pix
                    and from_y >= 0 and from_y < height_pix
                    and to_x >= 0 and to_x < width_pix
                    and to_y >= 0 and to_y < height_pix):
                    from_list.append([from_x, from_y])
                    to_list.append([to_x, to_y])
        
        #running script
        if self.thread_run_script.is_alive():
            self.thread_run_script.join()
        self.thread_run_script = Thread(target = self.panel_info.running_coordination_script, args = (from_list, to_list,))            
        self.thread_run_script.start()
        
    def wait_unplugin_connect_func(self):
        
        print ("Start...")
        self.wifi_connect_status = 1
        device_info = (self.adb_tool.shell("adb devices"))
        try:
            device_list = device_info.split()
            device_list.remove("List")
            device_list.remove("of")
            device_list.remove("devices")
            device_list.remove("attached")
            device_list.remove("device")
        except:
            print("Please connect device")
            return False
        
        device_name = device_list[0]
        print (device_name)
        self.wifi_connect_status_text.SetLabel("Start Connect...")
        self.wifi_connect_status_text.SetForegroundColour((255, 0, 0))

        #Get device ip & set port
        cmd = "adb -s %s shell ip -f inet addr show wlan0" %(device_name)
        ip = self.adb_tool.shell(cmd)
        ip = ip[ip.find("inet 1") + 5:ip.find("/")]
        print (ip)
        cmd = "adb -s %s tcpip %s" % (device_name, self.PORT_NUM)
        print (self.adb_tool.shell(cmd))
        if self.wifi_connect_status == 0:
            return
        
        #Connect
        self.device_ip = ip
        self.device_ip_port = str(ip) + ":" + self.PORT_NUM
        cmd = "adb connect %s:%s" %(self.device_ip, self.PORT_NUM)
        
        response = ""
        reconnect = 0
        while response.find("already") < 0 and self.wifi_connect_status != 0:
            response = (self.adb_tool.shell(cmd))
            print (response)
        if self.wifi_connect_status == 0:
            return
        
        #Polling wait unplugin
        devices = (self.adb_tool.shell("adb devices"))
        response = ""

        print ("Unplugin")
        self.wifi_connect_status_text.SetLabel("Please Unplugin...")
        self.wifi_connect_status_text.SetForegroundColour((255, 0, 0))
        
        while devices.find(device_name) > 0 and self.wifi_connect_status != 0:
            devices = (self.adb_tool.shell("adb devices"))

        if self.wifi_connect_status == 0:
            return
        
        #Connect
        cmd = "adb connect %s:%s" %(self.device_ip, self.PORT_NUM)
        while response.find("already") < 0 and self.wifi_connect_status != 0:
            response = (self.adb_tool.shell(cmd))
            print (response)
        if self.wifi_connect_status == 0:
            return
        
        print ("Wifi Connect Done")
        self.wifi_connect_status_text.SetLabel("Wifi Connect")
        self.wifi_connect_status_text.SetForegroundColour((50, 128, 50))
        
    def __del__(self):
        print ("ADB Stop")
        self.panel_info.terminate_raw_data()
        self.wifi_connect_status = 0
        self.adb_tool.shell("adb disconnect")

        if self.logging_status == 1:
            self.logging_file.close()
        self.logging_status = 0
        

    def obj_split(self, obj):
        obj = obj.replace(',', ' ')
        obj = obj.replace('.', ' ')
        obj = obj.replace('(', ' ')
        obj = obj.replace(')', ' ')
        obj = obj.replace('/', ' ')
        obj = obj.replace('\\', ' ')
        obj = obj.replace('-', ' ')
        obj = obj.replace('_', ' ')
        
        obj = obj.split()
        return obj
                        
def main():
    
    app = wx.App(False)
    
    frame = ADB_Frame()
    frame.Show()

    app.MainLoop()
    
if __name__ == "__main__":
    main()

