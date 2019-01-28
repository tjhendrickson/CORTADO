#!/opt/Anaconda2/bin/python

import nibabel.cifti2
import pandas as pd
import argparse
import os
from glob import glob
from multiprocessing import Pool
from subprocess import Popen, PIPE
import shlex
import cifti
import pdb


# For testing: ./rsfMRI_seed.py --output_dir /home/timothy/Projects/263_ETOH_tDCS/HCP_output --participant_label 7859 --session_label 48920 --parcel_file /home/timothy/Github/BIDShcppipelines/modified_files/360CortSurf_19Vol_parcel.dlabel.nii --parcel_name Glasser --seed_ROI_name AMYGDALA_LEFT AMYGDALA_RIGHT --seed_handling together --cifti_file ~/Projects/263_ETOH_tDCS/HCP_output/sub-7859/ses-48920/MNINonLinear/Results/sub-7859_ses-48920_task-rest_acq-eyesopenbeforePA_run-02_bold/RestingStateStats/sub-7859_ses-48920_task-rest_acq-eyesopenbeforePA_run-02_bold_Atlas_MSMAll_2_d40_WRN_hp2000_clean.ptseries.nii
parser = argparse.ArgumentParser(description='')
parser.add_argument('--output_dir', help='The directory where the output files '
                    'should be stored. If you are running group level analysis '
                    'this folder should be prepopulated with the results of the'
                    'participant level analysis.')
parser.add_argument('--participant_label', help='The label of the participant that should be analyzed. The label '
                   'corresponds to sub-<participant_label> from the BIDS spec '
                   '(so it does not include "sub-"). If this parameter is not '
                   'provided all subjects should be analyzed. Multiple '
                   'participants can be specified with a space separated list.',
                   nargs="+")
parser.add_argument('--session_label', help='The label of the session that should be analyzed. The label '
                   'corresponds to ses-<session_label> from the BIDS spec '
                   '(so it does not include "ses-"). If this parameter is not '
                   'provided all sessions within a subject should be analyzed.',
                   nargs="+")   
parser.add_argument('--coreg', help='Coregistration method to use ',
                    choices=['MSMSulc', 'FS'], default='MSMSulc')
parser.add_argument('--cifti_file', help='The CIFTI file to pull the seed timeseries from. Can either be a dtseries or ptseries file.')
parser.add_argument('--parcel_file', help='The CIFTI label file to use or used to parcellate the brain. ')
parser.add_argument('--parcel_name', help='Shorthand name of the CIFTI label file. ')
parser.add_argument('--fsf_rsfMRI_folder', help="folder containing templae fsf files to run first level rsfMRI seed analysis.")
parser.add_argument('--seed_ROI_name', help='Space separated list of ROI name/s from CIFTI label file to be used as the seed ROI/s. The exact ROI from the label file must be known!', nargs="+")
parser.add_argument('--seed_handling', help='Of the ROI/s you have provided do you want to treat them as together (i.e. averaging ROIs together), or separate (run separate seed based analyses for each ROI)? '
                                        'Choices are "together", or "separate". Default argument is "separate".',
                        choices=['together', 'separate'], default='separate')
args = parser.parse_args()

#global variables from arg parser
output_dir = args.output_dir
fsf_rsfMRI_folder = args.fsf_rsfMRI_folder
subj_id = args.participant_label
ses_id = args.session_label
parcel_file = args.parcel_file 
read_parcel_file = cifti.read(parcel_file)
parcel_file_label_tuple = read_parcel_file[1][0][0][1]
parcel_labels = []
cifti_file = args.cifti_file
for idx, value in enumerate(parcel_file_label_tuple):
        if not '???' in parcel_file_label_tuple[idx][0]:
                parcel_labels.append(parcel_file_label_tuple[idx][0])

# TODO: incorporate this function into run.py, not needed here
"""
def run_first_level_analysis(ptseries_file, subj_id, ses_id, out_dir, fsf_rsfMRI_folder, regressor_file):
    #args.update(os.environ)
    taskname = ptseries_file.split("/")[-3]
    cmd = '/opt/HCP-Pipelines/Examples/Scripts/generate_level1_fsf.sh --studyfolder="%s/HCP_output" --subject="%s" --session="%s" --taskname="%s" --templatedir="%s" --outdir="%s"' % (output_dir, subj_id, ses_id, taskname,current_dir,out_dir)
    process = Popen(shlex.split(cmd), stdout=PIPE)
    process.communicate()
    exit_code = process.wait()
    if exit_code == 0:
        fsf_file = "%s/%s_hp200_s2_level1.fsf" % (out_dir, taskname)
        feat_file = "../%s_%s_%s_hp2000_clean.nii.gz" % (subj_id, ses_id, taskname)
        with open(fsf_file, 'r') as file:
            filedata = file.read()
            filedata = filedata.replace('REGRESSOR',regressor_file)
        with open(fsf_file, 'w') as file:
            file.write(filedata)
        with open(fsf_file, 'r') as file:
            filedata = file.read()
            filedata = filedata.replace('FEATFILE', feat_file)
        with open(fsf_file, 'w') as file:
            file.write(filedata)
        cmd = '%s/ROI_rsfMRIAnalysisBatch.sh --StudyFolder="%s/HCP_output/%s" --Subjlist="%s" --seedROI="%s" --TaskName="%s" --runlocal' % (current_dir, output_dir, subj_id, ses_id, regressor_file.split(".")[0],taskname)
        process = Popen(shlex.split(cmd), stdout=PIPE)
        process.communicate()
"""	
def write_regressor(cifti_file,label_headers, seed_ROI_name, regressor_file):
    #args.update(os.environ)
    try:
        cifti_load = nibabel.cifti2.cifti2.load(cifti_file)
    except IOError:
        print("file does not exist")
    except:
        print("file does not look like a cifti file")
    
    #if not parcellated, first parcellate, then proceed to write regressor
    cifti_file_basename = os.path.basename(cifti_file)
    cifti_file_folder = os.path.dirname(cifti_file)
    if ".dtseries.nii" in cifti_file_basename:
        if not os.path.isdir(os.path.join(cifti_file_folder,"RestingStateStats")):
            os.mkdir(os.path.join(cifti_file_folder,"RestingStateStats"))
        cifti_prefix = cifti_file_basename.split(".dtseries.nii")[0]
        os.system("/opt/workbench/bin_rh_linux64/wb_command -cifti-parcellate %s %s %s %s" % (cifti_file, parcel_file, "COLUMN", os.path.join(cifti_file_folder,"RestingStateStats",cifti_prefix) + ".ptseries.nii"))
        cifti_file = os.path.join(cifti_file_folder,"RestingStateStats",cifti_prefix) + ".ptseries.nii"
        try:
            cifti_load = nibabel.cifti2.cifti2.load(cifti_file)
        except IOError:
            print("file does not exist")
        except:
            print("file does not look like a cifti file")
    
    pdb.set_trace()     
    regressor_file_path = os.path.join(cifti_file_folder,regressor_file)
	
    #create regressor file
    df = pd.DataFrame(cifti_load.get_fdata())
    
    df.columns = label_headers
    if type(seed_ROI_name) == str:
        df.to_csv(regressor_file_path,header=False,index=False,columns=[seed_ROI_name],sep=' ')
        return regressor_file_path
    else:
        if len(seed_ROI_name) == 2:
            df['avg'] = df[[seed_ROI_name[0],seed_ROI_name[1]]].mean(axis=1)
            df.to_csv(regressor_file_path,header=False,index=False,columns=['avg'],sep=' ')
            return regressor_file_path
        


def main():
    
    if len(args.seed_ROI_name) > 1:
        if args.seed_handling == "together":
            seed_ROI_merged_string = "-".join(str(x) for x in args.seed_ROI_name)
            seed_ROI_name = args.seed_ROI_name
            regressor_file = seed_ROI_merged_string + '-AvgRegressor.txt' 
            regressor_file_path = write_regressor(cifti_file, parcel_labels, seed_ROI_name, regressor_file)
        elif  args.seed_handling == "separate":
            for seed_ROI_name in args.seed_ROI_name:
                regressor_file = seed_ROI_name + '-Regressor.txt'
                regressor_file_path = write_regressor(cifti_file, parcel_labels, seed_ROI_name, regressor_file)
    else:
        seed_ROI_name = args.seed_ROI_name[0]
        regressor_file = seed_ROI_name + '-Regressor.txt'
        regressor_file_path = write_regressor(cifti_file, parcel_labels, seed_ROI_name, regressor_file)

main()
 







