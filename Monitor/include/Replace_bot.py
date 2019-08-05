import re
import string
import os

Replace_file = "Replace_compare.txt"
Orignal_file = "Original_compare.txt"
BACKUP_NAME = "BACKUP"

class Replace_section_flow():

    def __init__ (self, origin_list = None, replace_list = None):
        print ("Replace flow")
        self.original_list = []
        self.replace_list = []

        if origin_list == None:
            self.original_list = self.gettext_list(Orignal_file)
        else:
            self.original_list = origin_list
            
        if replace_list == None:
            self.replace_list = self.gettext_list(Replace_file)
        else:
            self.replace_list = replace_list
        #print (self.original_list)
        
    def gettext_list(self, file_name):
        output_list = []
        with open(file_name, 'r') as f:
            for line in f.readlines():
                output_list.append(line)
        return output_list

    def replace_mechanism(self, file_name):
        #----------------------Checking orignal section is exist
        original_list = self.original_list
        replace_list = self.replace_list
        fail_line = {}
        
        #Replace flow
        replace_file = open(BACKUP_NAME, 'w')
        with open(file_name, 'r') as f:
            for line in f.readlines():

                match_flag = False
                
                #Find match line
                for i, ori_line in enumerate(original_list):
                    replace_line = replace_list[i]
                    if line[-1:] == '\n' and ori_line[-1:] != '\n':
                        ori_line = ori_line + '\n'
                        replace_line = replace_line + '\n'
                        
                    if line[-1:] != '\n' and ori_line[-1:] == '\n':
                        ori_line = ori_line[:-1]
                        replace_line = replace_line[:-1]
                        
                    if (ori_line == line):
                        if (ori_line != replace_line):
                            match_flag = True

                            for j, c in enumerate(ori_line):
                                if c != replace_line[j]:
                                    replace_file.write(replace_line[j])
                                else:
                                    replace_file.write(line[j])

                            #print (replace_line)
                        fail_line[str(i)] = True

                #Keep original line
                if match_flag == False:
                    replace_file.write(line)
                
        replace_file.close()

        #----------------------Rename file
        try:
            os.remove(file_name)
            os.rename(BACKUP_NAME, file_name)
        except:
            print ("==================================" + file_name + "==================================")
            print ("Rename file name error")

        #----------------------Show fail line
        match_flag = False
        for i, ori_line in enumerate(original_list):
            if str(i) not in fail_line:
                if match_flag == False:
                    match_flag = True
                    print ("==================================" + file_name + "==================================")
                print ori_line
        

    def loop_file_replace_mechanism(self, file_path):
        header_file_list = []

        for f in os.listdir(file_path):
            if (f[-2:] == '.h'):
                header_file_list.append(file_path + '/' + f)

        for f in header_file_list:
            self.replace_mechanism(f)

        print ("Replace script Done~")
        
'''
def main():
    obj = Replace_section_flow()
    #obj.loop_file_replace_mechanism("./tp_initial_code")
    obj.replace_mechanism("./PA5464A_BOE6D24_tp_initial_code_20180615.h")
    pass

if __name__ == "__main__":
    main()
'''
