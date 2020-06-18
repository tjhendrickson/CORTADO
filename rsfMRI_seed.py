#!/opt/Miniconda3/bin/python

import nibabel.cifti2
import pandas as pd
import os
import cifti
import csv
import numpy as np
from glob import glob
import subprocess
from subprocess import Popen, PIPE
from nilearn.connectome import ConnectivityMeasure
from sklearn.covariance import GraphicalLassoCV

class seed_analysis:
    def __init__(self,output_dir,cifti_file, parcel_file, parcel_name, seed_ROI_name,level,pipeline,ICAstring,vol_finalfile,confound,smoothing,regname,fmriname,fmrifoldername):
        '''
        Class initialization for seed based analysis. The primary purpose of this class is to:
        1) Performs tests on arguments cifti_file and parcel_file to ensure inputted arguments are in the expected format
        2) Intialize important variables that will be used for downstream child classes 'regression' and 'connectivity'
        '''
        # path that data will be written to
        self.output_dir = output_dir
        # inputted cifti file
        self.cifti_file = cifti_file
        self.shortfmriname=self.cifti_file.split("/")[-2]
        # inputted atlas/parcellation file
        self.parcel_file = parcel_file
        # shorthand name chosen for parcel file
        self.parcel_name = parcel_name
        # seed ROI name used for analysis
        self.seed_ROI_name = seed_ROI_name
        
        # level of analysis to be done
        self.level = level
        
        #arguments that may change depending on analysis level
        self.pipeline = pipeline
        self.ICAstring = ICAstring
        self.vol_fmritcs = vol_finalfile
        self.confound = confound
        self.smoothing = smoothing
        self.regname = regname
        self.fmriname = fmriname
        self.fmrifoldername = fmrifoldername
        
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
        
        # do tests on cifti file and load
        if self.level == 1:
            self.cifti_tests()
            
        if not type(self.seed_ROI_name) == str:
            separator = "-"
            self.seed_ROI_string = separator.join(self.seed_ROI_name)
        else:
            self.seed_ROI_string = self.seed_ROI_name
    
    def cifti_tests(self):
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
        cifti_prefix = cifti_file_basename.split(".")[0]
        cifti_suffix = '.'.join(cifti_file_basename.split('.')[1:])
        os.system("/opt/workbench/bin_rh_linux64/wb_command -cifti-parcellate %s %s %s %s" 
                  % (self.cifti_file, 
                     self.parcel_file, 
                     "COLUMN", 
                     os.path.join(self.output_dir,cifti_prefix) + "_"+self.parcel_name + cifti_suffix))
        cifti_file = os.path.join(self.output_dir,cifti_prefix) + "_"+self.parcel_name + cifti_suffix
        self.cifti_file = cifti_file
        # does CIFTI file exist?
        try:
            read_cifti = open(cifti_file)
            read_cifti.close()
        except IOError:
            print("file does not exist")    
        # is entered CIFTI file actually a CIFTI file?
        try:
            self.cifti_load = nibabel.cifti2.cifti2.load(cifti_file)
        except:
            print("file does not look like a cifti file")
                  
class regression(seed_analysis):
    def __init__(self):
        '''
        Child class of seed_analysis. This performs regression on resting state data by:
        1) Extracting seed ROI/parcel timeseries
        2) Include the extracted timeseries as a regressor/explanatory to a GLM driven by FSL and HCP tools
        3) Use the targeted ROI timeseries as the dependent measure
        4) Calculate the parameter estimate as a proxy measure of seed based connectivity
        '''
        
        # hardcoded arguments
        self.highpass = "2000"
        self.lowresmesh = 32
        self.highresmesh = 164
        
        if len(self.vol_fmritcs) > 0:
            zooms = nibabel.load(self.vol_fmritcs).get_header().get_zooms()
            self.fmrires = str(int(min(zooms[:3])))

        # Determine locations of necessary directories (using expected naming convention)
        self.AtlasFolder='/'.join(self.cifti_file.split("/")[0:5])
        self.DownSampleFolder=self.AtlasFolder + "/fsaverage_LR" + str(self.lowresmesh) + "k"
        self.ResultsFolder=self.AtlasFolder+"/Results"
        self.ROIsFolder=self.AtlasFolder+"/ROIs"
        self.regressor_file = self.seed_ROI_string + '-Regressor.txt'
        self.write_regressor()
        
        if self.level == 1:
            self.run_regression_level1()
        else:
            self.run_regression_level2()
    
    def run_regression_level1(self):
        os.system("export PATH=/usr/local/fsl/bin:${PATH}")
        fsf_creation = '/generate_level1_fsf.sh ' + \
            '--taskname="{fmriname}" ' + \
            '--temporalfilter="{highpass}" ' + \
            '--originalsmoothing="{fmrires}" ' + \
            '--outdir="{outdir}" '
        fsf_creation = fsf_creation.format(fmriname=self.fmriname,highpass=self.highpass,
                                           fmrires=self.fmrires,outdir=self.output_dir)
        self.run(fsf_creation, cwd=self.output_dir)
        
        generate_regression = '/RestfMRILevel1.sh ' + \
            '--outdir={outdir} ' + \
            '--ICAoutputs={ICAstring} ' + \
            '--pipeline={pipeline} ' + \
            '--finalfile={finalfile} ' + \
            '--volfinalfile={vol_finalfile} ' + \
            '--fmrifilename={fmrifilename} ' + \
            '--fmrifoldername={fmrifoldername} ' + \
            '--DownSampleFolder={DownSampleFolder} ' + \
            '--ResultsFolder={ResultsFolder} ' + \
            '--ROIsFolder={ROIsFolder} ' + \
            '--lowresmesh={lowresmesh:d} ' + \
            '--grayordinatesres={fmrires:s} ' + \
            '--origsmoothingFWHM={fmrires:s} ' + \
            '--confound={confound} ' + \
            '--finalsmoothingFWHM={smoothing:d} ' + \
            '--temporalfilter={temporal_filter} ' + \
            '--regname={regname} ' + \
            '--parcellation={parcel_name} ' + \
            '--parcellationfile={parcel_file} ' + \
            '--seedROI={seedROI}'
        generate_regression = generate_regression.format(outdir=self.output_dir,ICAstring=self.ICAstring,
                                                         pipeline=self.pipeline,finalfile=self.cifti_file,
                                                         vol_finalfile=self.vol_finalfile,fmrifilename=self.fmriname,
                                                         fmrifoldername=self.fmrifoldername,DownSampleFolder=self.DownSampleFolder,
                                                         ResultsFolder=self.ResultsFolder,ROIsFolder=self.ROIsFolder,
                                                         lowresmesh=self.lowresmesh,fmrires=self.fmrires,
                                                         confound=self.confound,temporal_filter=self.highpass,
                                                         smoothing=self.smoothing,regname=self.regname,
                                                         parcel_name=self.parcel_name,parcel_file=self.parcel_file,seedROI=self.seed_ROI_name)
        self.run(generate_regression, cwd=self.output_dir)
    
    def run_regression_level2(self):
        os.system("export PATH=/usr/local/fsl/bin:${PATH}")
        fsf_creation = '/generate_level2_fsf.sh ' + \
            '--taskname="{fmriname}" ' + \
            '--temporalfilter="{highpass}" ' + \
            '--originalsmoothing="{fmrires}" ' + \
            '--outdir="{outdir}" '
        fsf_creation = fsf_creation.format(fmriname=self.level_2_foldername, highpass=self.highpass,
                                           fmrires=self.fmrires,outdir=self.output_dir)
        self.run(fsf_creation, cwd=self.output_dir)

        generate_regression = '/RestfMRILevel2.sh ' + \
            '--outdir={outdir} ' + \
            '--ICAoutputs={ICAstring} ' + \
            '--pipeline={pipeline} ' + \
            '--fmrifilenames={fmrifilename} ' + \
            '--lvl2fmrifoldername={level_2_foldername} ' + \
            '--finalsmoothingFWHM={smoothing:d} ' + \
            '--temporalfilter={temporal_filter} ' + \
            '--regname={regname} ' + \
            '--parcellation={parcel_name} ' + \
            '--seedROI={seedROI}'
        generate_regression = generate_regression.format(outdir=self.output_dir,ICAstring=self.ICAstring,
                                                         pipeline=self.pipeline,fmrifilename=self.fmriname,
                                                         level_2_foldername=self.level_2_foldername,
                                                         smoothing=self.smoothing,temporal_filter=self.highpass,
                                                         reg_name=self.regname,parcel_name=self.parcel_name,
                                                         seedROI=self.seedROI)
        self.run(generate_regression, cwd=self.output_dir)
             
    def write_regressor(self):
        print('rsfMRI_seed.py: Create regressor file ')
        print('\t-Output folder: ' + self.output_dir)
        print('\t-Cifti file: ' + self.cifti_file)
        print('\t-Parcel file: ' + self.parcel_file)
        print('\t-Seed ROI name: ' + str(self.seed_ROI_name))
        
        # path that regressor file will be outputted to
        regressor_file_path = os.path.join(self.output_dir,self.regressor_file)
        #create regressor file
        df = pd.DataFrame(self.cifti_load.get_fdata())
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
            
    def run(command, env={}, cwd=None):
        merged_env = os.environ
        merged_env.update(env)
        merged_env.pop("DEBUG", None)
        print(command)
        process = Popen(command, stdout=PIPE, stderr=subprocess.STDOUT,
                        shell=True, env=merged_env, cwd=cwd)
        while True:
            line = process.stdout.readline()
            print(line)
            line = str(line)[:-1]
            if line == '' and process.poll() != None:
                break
        if process.returncode != 0:
            raise Exception("Non zero return code: %d"%process.returncode)  
    
class pair_pair_connectivity(seed_analysis):
    def __init__(self,method):
        '''
        Child class of seed_analysis. This performs connectivity on resting state data by:
        1) Generating connectivity matrices with nilearn's ConnectivityMeasure module 
        2) Metrics include correlation, partial correlation, covariance, precision, sparse covariance, and sparse precision
        3) Extract only the functional connectivity vector associated with the inputted seed
        4) Output as a ptseries.nii file in the same position and format as the regression class
        '''
        
        self.method = method
        
        if self.level == 1:
            self.df_cifti_load = pd.DataFrame(self.cifti_load.get_fdata())
            self.df_cifti_load.columns = self.parcel_labels
            
            # run extract_vector
            if type(self.seed_ROI_name) == str:
                self.extract_vector()
            else:
                self.df_cifti_load['avg'] = self.df_cifti_load[self.seed_ROI_name].mean(axis=1)
                self.seed_ROI_name='avg'
                self.parcel_labels=self.df_cifti_load.columns.to_list()
                self.extract_vector()
        # run cifti_create_file
        self.create_cifti_file()
                    
    def extract_vector(self):
        if self.level == 1:
            cifti_np_array = self.df_cifti_load.to_numpy()
            if self.method == 'correlation':
                #Pearson correlation coefficients with LedoitWolf covariance estimator
                measure = ConnectivityMeasure(kind='correlation')
            elif self.method == 'covariance':
                #LedoitWolf estimator
                measure = ConnectivityMeasure(kind='covariance')
            elif self.method == 'partial_correlation':
                # Partial correlation with LedoitWolf covariance estimator
                measure = ConnectivityMeasure(kind='partial correlation')
            elif self.method == 'precision':
                measure = ConnectivityMeasure(kind='precision')
            elif 'sparse' in self.method:
                measure = GraphicalLassoCV() 
            if 'sparse' in self.method:
                measure.fit(cifti_np_array)
                if 'covariance' in self.method:
                    network_matrix = measure.covariance_
                elif 'precision' in self.method:
                    network_matrix = measure.precision_
            else:
                network_matrix = measure.fit_transform([cifti_np_array])[0]
            df_network_matrix = pd.DataFrame(network_matrix)
            df_network_matrix.columns = self.parcel_labels
            self.r_functional_vector = df_network_matrix[self.seed_ROI_name].to_numpy()
            self.z_functional_vector = np.arctanh(self.r_functional_vector)
            
    def create_cifti_file(self):
        if self.level == 1:
            grayordinate_file = '/91282_Greyordinates.dscalar.nii'
            self.cifti_file = grayordinate_file
            self.cifti_tests()
            #save new image
            new_r_cifti_img = nibabel.cifti2.Cifti2Image(np.transpose(np.expand_dims(self.r_functional_vector,axis=1)),header=self.cifti_load.header)
            new_z_cifti_img = nibabel.cifti2.Cifti2Image(np.transpose(np.expand_dims(self.z_functional_vector,axis=1)),header=self.cifti_load.header)
            new_cifti_output_folder=os.path.join(self.output_dir,self.fmriname,self.parcel_name+'_',self.ICAoutputs_level1_seed + self.seed_ROI_name,'ParcellatedStats')
            if not os.path.isdir(new_cifti_output_folder):
                os.makedirs(new_cifti_output_folder)
            nibabel.cifti2.save(new_r_cifti_img,os.path.join(new_cifti_output_folder,'rstats.pscalar.nii'))
            nibabel.cifti2.save(new_z_cifti_img,os.path.join(new_cifti_output_folder,'zstats.pscalar.nii'))
        else:
            new_cifti_output_folder=os.path.join(self.output_dir,self.fmriname,self.parcel_name+'_',self.ICAoutputs_level2_seed + self.seed_ROI_name,'ParcellatedStats')
            if not os.path.isdir(new_cifti_output_folder):
                os.makedirs(new_cifti_output_folder)
            
class create_text_output(seed_analysis):
    def create_text_output(self,text_output_dir):
        # find first level CORTADO folder for given participant and session
        print('rsfMRI_seed.py: Create Text Output ')
        print('\t-Text output folder: %s' %str(text_output_dir))
        print('\t-Cifti file: %s' %str(self.cifti_file))
        print('\t-Parcel file: %s' %str(self.parcel_file))
        print('\t-Parcel name: %s' %str(self.parcel_name))
        print('\t-Seed ROI name/s: %s' %str(self.seed_ROI_name))
        print('\t-The fmri file name: %s' %str(self.fmriname))
        print('\t-ICA String to be used to find FEAT dir, if any: %s' %str(self.ICAstring))
        print('\t-Analysis level to output data from: %s' %str(self.level))
        
        # if file exists and subject and session have yet to be added, add to file
        if self.level == 1:
            output_text_file = os.path.join(text_output_dir,"_".join(self.fmriname.split('_')[2:])+"_"+self.parcel_name+self.ICAstring+'_level'+ str(self.level)+'_seed'+self.seed_ROI_string+".csv")
        elif self.level == 2:
            output_text_file = os.path.join(text_output_dir,"rsfMRI_combined_"+self.fmriname.split('_bold_')[1] + self.parcel_name+self.ICAstring+'_level'+ str(self.level)+'_seed'+self.seed_ROI_string+".csv")
        print('\t-Output file: %s' %str(output_text_file))
        print('\n')
        if self.level == 1:
            CORTADO_dir = os.path.join(self.output_dir,self.fmriname+"_"+self.parcel_name+self.ICAstring+'_level' + str(self.level)+'_seed'+self.seed_ROI_string+".feat")
            zstat_data_file = os.path.join(CORTADO_dir,"ParcellatedStats","zstat1.ptseries.nii")
        elif self.level == 2:
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






