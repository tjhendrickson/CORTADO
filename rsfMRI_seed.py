#!/opt/Anaconda2/bin/python

import nibabel.cifti2
import pandas as pd
import os
import cifti
import pdb
import csv
import numpy as np
from glob import glob

class SeedIO:
    def __init__(self,output_dir,cifti_file, parcel_file, parcel_name, seed_ROI_name):
        # path that data will be written to
        self.output_dir = output_dir
        # inputted cifti file
        self.cifti_file = cifti_file
        # inputted atlas/parcellation file
        self.parcel_file = parcel_file
        # shorthand name chosen for parcel file
        self.parcel_name = parcel_name
        # seed ROI name used for analysis
        self.seed_ROI_name = seed_ROI_name
        
        # create output folder if it does not exist
        if not os.path.isdir(self.output_dir):
            os.makedirs(self.output_dir)
        # determine fmriname
        self.fmriname = os.path.basename(cifti_file).split('.')[0]
                
        # read parcel labels into list to query later
        read_parcel_file = cifti.read(self.parcel_file)
        parcel_file_label_tuple = read_parcel_file[1][0][0][1]
        parcel_labels = []
        
        for value in parcel_file_label_tuple:
                if not '???' in parcel_file_label_tuple[value][0]:
                        parcel_labels.append(parcel_file_label_tuple[value][0])
        self.parcel_labels = [str(r) for r in parcel_labels]
        # determine regressor filename
        if not type(self.seed_ROI_name) == str:
            separator = "-"
            seed_ROI_merged_string = separator.join(self.seed_ROI_name)
            self.regressor_file = seed_ROI_merged_string + '-Regressor.txt'
        else:
            self.regressor_file = self.seed_ROI_name + '-Regressor.txt'

    def write_regressor(self):
        print('rsfMRI_seed.py: Create regressor file ')
        print('\t-Output folder: ' + self.output_dir)
        print('\t-Cifti file: ' + self.cifti_file)
        print('\t-Parcel file: ' + self.parcel_file)
        print('\t-Seed ROI name: ' + str(self.seed_ROI_name))
        
        # does CIFTI file exist?
        try:
            read_cifti = open(self.cifti_file)
            read_cifti.close()
        except IOError:
            print("file does not exist")
            
        # is entered CIFTI file actually a CIFTI file?
        try:
            cifti_load = nibabel.cifti2.cifti2.load(self.cifti_file)
        except:
            print("file does not look like a cifti file")
    
        cifti_file_basename = os.path.basename(self.cifti_file)
        cifti_prefix = cifti_file_basename.split(".dtseries.nii")[0]
        os.system("/opt/workbench/bin_rh_linux64/wb_command -cifti-parcellate %s %s %s %s" 
                  % (self.cifti_file, 
                     self.parcel_file, 
                     "COLUMN", 
                     os.path.join(self.output_dir,cifti_prefix) + "_"+self.parcel_name + ".ptseries.nii"))
        cifti_file = os.path.join(self.output_dir,cifti_prefix) + "_"+self.parcel_name +".ptseries.nii"
        self.cifti_file = cifti_file
        # does CIFTI file exist?
        try:
            read_cifti = open(cifti_file)
            read_cifti.close()
        except IOError:
            print("file does not exist")    
        # is entered CIFTI file actually a CIFTI file?
        try:
            cifti_load = nibabel.cifti2.cifti2.load(cifti_file)
        except:
            print("file does not look like a cifti file")
        # path that regressor file will be outputted to
        regressor_file_path = os.path.join(self.output_dir,self.regressor_file)
        #create regressor file
        df = pd.DataFrame(cifti_load.get_fdata())
        df.columns = self.parcel_labels
        if type(self.seed_ROI_name) == str:
            df.to_csv(regressor_file_path,header=False,index=False,columns=[self.seed_ROI_name],sep=' ')
        else:
            df['avg'] = df[self.seed_ROI_name].mean(axis=1)
            df.to_csv(regressor_file_path,header=False,index=False,columns=['avg'],sep=' ')
        # figure out what name of regressor file should be
        print('\t-Regressor file: %s' %regressor_file_path)
        print('\n') 
        return regressor_file_path

    def create_text_output(self,ICAstring,text_output_dir,level):
        # find first level CORTADO folder for given participant and session
        seed=self.regressor_file.split('-Regressor.txt')[0]
        print('rsfMRI_seed.py: Create Text Output ')
        print('\t-Text output folder: %s' %str(text_output_dir))
        print('\t-Cifti file: %s' %str(self.cifti_file))
        print('\t-Parcel file: %s' %str(self.parcel_file))
        print('\t-Parcel name: %s' %str(self.parcel_name))
        print('\t-Seed ROI name/s: %s' %str(self.seed_ROI_name))
        print('\t-The fmri file name: %s' %str(self.fmriname))
        print('\t-ICA String to be used to find FEAT dir, if any: %s' %str(ICAstring))
        print('\t-Analysis level to output data from: %s' %str(level))
        
        # if file exists and subject and session have yet to be added, add to file
        if level == 1:
            output_text_file = os.path.join(text_output_dir,"_".join(self.fmriname.split('_')[2:])+"_"+self.parcel_name+ICAstring+'_level'+ str(level)+'_seed'+seed+".csv")
        elif level == 2:
            output_text_file = os.path.join(text_output_dir,"rsfMRI_combined_"+self.fmriname.split('_bold_')[1] + self.parcel_name+ICAstring+'_level'+ str(level)+'_seed'+seed+".csv")
        print('\t-Output file: %s' %str(output_text_file))
        print('\n')
        if level == 1:
            CORTADO_dir = os.path.join(self.output_dir,self.fmriname+"_"+self.parcel_name+ICAstring+'_level' + str(level)+'_seed'+seed+".feat")
            zstat_data_file = os.path.join(CORTADO_dir,"ParcellatedStats","zstat1.ptseries.nii")
        elif level == 2:
            CORTADO_dir = glob(os.path.join(self.output_dir,"rsfMRI_combined_*.feat"))[0]
            zstat_data_file = os.path.join(CORTADO_dir,"ParcellatedStats_fixedEffects","zstat1.ptseries.nii")
        zstat_data_img = nibabel.cifti2.load(zstat_data_file)
        # if file does not exist write header to it, otherwise continue
        try:
            read_output_text_file = open(output_text_file,'r')
            read_output_text_file.close()
        except:
            # file exists and is accessible, ensure that to be appended data does not yet exist on it
            fieldnames = self.parcel_labels
            # append subject and session ID to fieldname list
            if os.path.basename(self.output_dir).split('-')[0] == 'ses':
                fieldnames.insert(0,'Session ID')
                fieldnames.insert(0,'Subject ID')
            # if doesn't exist create headers and add subject/session data to file
            with open(output_text_file,'w') as output_text_file_open:
                writer = csv.writer(output_text_file_open)
                writer.writerow(fieldnames)
        # find participant if it exists
        row_data = np.squeeze(zstat_data_img.get_fdata()).tolist()
        if os.path.basename(self.output_dir).split('-')[0] == 'ses':
            session_id = str(os.path.basename(self.output_dir).split('-')[1])
            row_data.insert(0,session_id)
            subject_id = str(self.output_dir.split('sub-')[1].split('/')[0])    
            row_data.insert(0,subject_id)
        else:
            subject_id = str(os.path.basename(self.output_dir).split('-')[1])
            row_data.insert(0,subject_id)
        # create dataframe of output text file
        output_text_file_df = pd.read_csv(output_text_file)
        if session_id:
            if len(output_text_file_df.loc[(output_text_file_df['Session ID']==session_id) & (output_text_file_df['Subject ID']==subject_id)]) == 0:
                with open(output_text_file,'a') as append_output_text_file:
                    writer = csv.writer(append_output_text_file)
                    writer.writerow(row_data)
            else:
                print('WARNING: Session ID %s already exists within text output file %s. Not writing to file.' %(str(session_id),output_text_file))
        else:
            if len(output_text_file_df[output_text_file_df['Subject ID']==subject_id]) == 0:
                with open(output_text_file,'a') as output_text_file:
                    writer = csv.writer(append_output_text_file)
                    writer.writerow(row_data)
            else:
                print('WARNING: Subject ID %s already exists within text output file %s. Not writing to file.' %(str(subject_id),output_text_file))
                            
                    
                    
                    









