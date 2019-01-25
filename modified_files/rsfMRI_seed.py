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


# For testing: ./rsfMRI_seed.py --output_dir /home/timothy/Projects/263_ETOH_tDCS/HCP_output --participant_label 7859 --session_label 48920 --parcel_file /home/timothy/Github/BIDShcppipelines/modified_files/360CortSurf_19Vol_parcel.dlabel.nii --parcel_name Glasser --seed_ROI_name AMYGDALA_LEFT AMYGDALA_RIGHT
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
parser.add_argument('--parcel_file', help='The CIFTI label file to use or used to parcellate the brain. ')
parser.add_argument('--parcel_name', help='Shorthand name of the CIFTI label file. ')
parser.add_argument('--seed_ROI_name', help='Space separated list of ROI name/s from CIFTI label file to be used as the seed ROI/s. The exact ROI from the label file must be known!', nargs="+")
parser.add_argument('--seed_handling', help='Of the ROI/s you have provided do you want to treat them as together (i.e. averaging ROIs together), or separate (run separate seed based analyses for each ROI)? '
                                        'Choices are "together", or "separate". Default argument is "separate".',
                        choices=['together', 'separate'], default='separate')
args = parser.parse_args()

#global variables from arg parser
output_dir = args.output_dir
subj_id = args.participant_label
ses_id = args.session_label
parcel_file = args.parcel_file 
read_parcel_file = cifti.read(parcel_file)
parcel_file_label_tuple = read_parcel_file[1][0][0][1]
parcel_labels = []
for idx, value in enumerate(parcel_file_label_tuple):
        if not '???' in parcel_file_label_tuple[idx][0]:
                parcel_labels.append(parcel_file_label_tuple[idx][0])
labels = pd.DataFrame(parcel_labels)


def run_first_level_analysis(ptseries_file, subj_id, ses_id, out_dir, regressor_file):
        taskname = ptseries_file.split("/")[-3]
        cmd = '%s/generate_level1_fsf.sh --studyfolder="%s/HCP_output" --subject="%s" --session="%s" --taskname="%s" --templatedir="%s" --outdir="%s"' % (current_dir, output_dir, subj_id, ses_id, taskname,current_dir,out_dir)
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
	
def write_regressor(ptseries_file,label_headers, seed_roi, regressor_file, seed_handling):

	#create needed variables
    ptseries_load = nibabel.cifti2.cifti2.load(ptseries_file)
    RSS_folder = "/".join(ptseries_file.split("/")[:-1])
    regressor_file_path = os.path.join(RSS_folder,regressor_file)
	#create regressor/s file
    df = pd.DataFrame(ptseries_load.get_fdata())
    df.columns = label_headers
    if seed_handling == 'separate':
        df.to_csv(regressor_file_path,header=False,index=False,columns=[seed_roi],sep=' ')
        return regressor_file_path
    #else:
        


#	run_first_level_analysis(ptseries_file, subj_id, ses_id, output_dir, regressor_file)
def main():
    
    # TODO: shore up how to handle this within container
    #tasknames=['task-rest_acq-eyesopenbeforePA_run-02_bold', 'task-rest_acq-eyesopenafterPA_run-03_bold']
    #ptseries_files = [ ptseries_file for taskname in tasknames for ptseries_file in glob(os.path.join(output_dir, 'HCP_output','sub-' + subj_id, 'ses-' + ses_id, 'MNINonLinear', 'Results', 'sub-' + subj_id + '_ses-' + ses_id + '_' + taskname, 'RestingStateStats',  'sub-' +subj_id + '_ses-' + ses_id + '_' + taskname + '_Atlas_MSMAll_2_d40_WRN_hp2000_clean.ptseries.nii'))]

   # df['LGN_avg'] = df[[('L_Lateral_Geniculum_Body',),('R_Lateral_Geniculum_Body',)]].mean(axis=1)
	# df.to_csv(os.path.join(RSS_folder,LGN_file),header=False,index=False,columns=['LGN_avg'],sep=' ')
    
    #organize variables based on # of ROIs and seed handling
    if len(args.seed_ROI_name) > 1:
        if args.seed_handling == "together":
            seed_ROI_name = "-".join(str(x) for x in args.seed_roi_name)
            regressor_file = seed_ROI_name + '-AvgRegressor.txt' #TODO: will have to handle this in a different way since a space separated list can now be used
            regressor_file_path = write_regressor(ptseries_file, labels, seed_roi, regressor_file, args.seed_handling)
            run_first_level_analysis(ptseries_file, subj_id, ses_id, output_dir, regressor_file_path)
        elif  args.seed_handling == "separate":
            for seed in args.seed_ROI_name:
                seed_roi = (seed,)
                regressor_file_path = write_regressor(ptseries_file, labels, seed_roi, regressor_file, args.seed_handling)
                run_first_level_analysis(ptseries_file, subj_id, ses_id, output_dir, regressor_file_path)
    else:
        seed_roi = (args.seed_ROI_name,) 
        regressor_file = args.seed_ROI_name + '-Regressor.txt'
        regressor_file_path = write_regressor(ptseries_file, labels, seed_roi, regressor_file, args.seed_handling)
        run_first_level_analysis(ptseries_file, subj_id, ses_id, output_dir, regressor_file_path)

main()
 







