#!/opt/Anaconda2/bin/python

import nibabel.cifti2
import pandas as pd
import os
import cifti

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
                
        # read parcel labels into list to query later
        read_parcel_file = cifti.read(self.parcel_file)
        parcel_file_label_tuple = read_parcel_file[1][0][0][1]
        parcel_labels = []
        for value in parcel_file_label_tuple:
                if not '???' in parcel_file_label_tuple[value][0]:
                        parcel_labels.append(parcel_file_label_tuple[value][0])
        self.parcel_labels = parcel_labels
        # determine regressor filename
        if not type(self.seed_ROI_name) == str:
            separator = "-"
            seed_ROI_merged_string = separator.join(self.seed_ROI_name)
            self.regressor_file = seed_ROI_merged_string + '-Regressor.txt'
        else:
            self.regressor_file = self.seed_ROI_name + '-Regressor.txt'

    def write_regressor(self):
        print('output_dir: ' + self.output_dir)
        print('cifti_file: ' + self.cifti_file)
        print('parcel_file: ' + self.parcel_file)
        print('seed_ROI_name: ' + str(self.seed_ROI_name))
        # figure out what name of regressor file should be
        print('regressor_file: ' + self.regressor_file)
        
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
        return regressor_file_path 
    def create_text_output(self,ICAoutputs,preprocessing_type,fmriname,text_output_format,parcel_name,level):
        # find first level CORTADO folder for given participant and session
        seed=self.regressor_file.split('-Regressor.txt')[0]
        if ICAoutputs == 'YES':
            if preprocessing_type == 'HCP':
                ICAString="_FIXclean"
            elif preprocessing_type == "fmriprep":
                ICAString="_AROMAclean"
        else:
            ICAString=""
        
        CORTADO_dir = os.path.join(self.output_dir,fmriname+"_"+parcel_name+ICAString+'_level' + str(level)+'_seed'+seed+".feat")
        zstat_data_file = os.path.join(CORTADO_dir,"ParcellatedStats","zstat1.ptseries.nii")
        zstat_data_img = nibabel.cifti2.load(zstat_data_file)
        # set outputs suffixes
        if text_output_format == "CSV" or text_output_format == "csv":
            # if file exists and subject and session have yet to be added, add to file
            output_text_file = os.path.join(args.output_dir,"_".join(fmriname.split('_')[2:])+"_"+parcel_name+ICAString+'_level1_seed'+seed_ROI_merged_string+".csv")
            # prevent race condition by using "try" statement
            try:
                read_output_text_file = open(output_text_file,'r')
            except:
                # if doesn't exist create headers and add subject/session data to file
                write_output_text_file = open(output_text_file,'w')
                
                read_parcel_file = cifti.read(parcel_file)
                parcel_file_label_tuple = read_parcel_file[1][0][0][1]
                fieldnames = []
                for value in parcel_file_label_tuple:
                    if not '???' in parcel_file_label_tuple[value][0]:
                        fieldnames.append(parcel_file_label_tuple[value][0])
                # append subject and session ID to fieldname list
                fieldnames.insert(0,'Session ID')
                fieldnames.insert(0,'Subject ID')
            # file exists and is accessible, ensure that data does not yet exist on it 
            read_output_text_file = pd(output_text_file,'r')
            
            # now append
            F.flock(read_output_text_file, F.LOCK_EX)
            with open(output_text_file,'w') as f:
                    pass







