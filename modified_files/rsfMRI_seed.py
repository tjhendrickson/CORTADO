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
parser.add_argument('--parcellation_file', help='The CIFTI label file to use or used to parcellate the brain. ')
parser.add_argument('--parcellation_name', help='Shorthand name of the CIFTI label file. ')
parser.add_argument('--seedROI', help='ROI name from CIFTI label file to be used as the seed ROI. The exact ROI from the label file must be known! ')
args = parser.parse_args()

# global variables
seed_roi = (args.seedROI,)
regressor_file = args.seedROI + '_regressor.txt'
output_dir = args.output_dir
subj_id = args.participant_label
ses_id = args.session_label
parcel_file = args.parcellation_file

#read parcel file and return label names 
read_parcel_file = cifti.read(parcel_file)
parcel_file_label_tuple = read_parcel_file[1][0][0][1]
parcel_labels = []
for idx, value in enumerate(parcel_file_label_tuple):
        if not '???' in parcel_file_label_tuple[idx][0]:
                parcel_labels.append(parcel_file_label_tuple[idx][0])
labels = pd.DataFrame(parcel_labels)


# TODO: shore up how to handle this within container
tasknames=['task-rest_acq-eyesopenbeforePA_run-02_bold', 'task-rest_acq-eyesopenafterPA_run-03_bold']
ptseries_files = [ ptseries_file for taskname in tasknames for ptseries_file in glob(os.path.join(output_dir, 'HCP_output','sub-' + subj_id, 'ses-' + ses_id, 'MNINonLinear', 'Results', 'sub-' + subj_id + '_ses-' + ses_id + '_' + taskname, 'RestingStateStats',  'sub-' +subj_id + '_ses-' + ses_id + '_' + taskname + '_Atlas_MSMAll_2_d40_WRN_hp2000_clean.ptseries.nii'))]


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
	
def write_regressor(ptseries_file,label_headers, seed_roi):

	#create needed variables
	ptseries_load = nibabel.cifti2.cifti2.load(ptseries_file)
	RSS_folder = "/".join(ptseries_file.split("/")[:-1])
	regressor_file_path = os.path.join(RSS_folder,regressor_file)
	#create regressor/s file
	df = pd.DataFrame(ptseries_load.get_fdata())
	df.columns = label_headers
	df.to_csv(regressor_file_path,header=False,index=False,columns=[seed_roi],sep=' ')
        return regressor_file_path

#	run_first_level_analysis(ptseries_file, subj_id, ses_id, output_dir, regressor_file)

regressor_file_path = write_regressor(ptseries_file, labels, seed_roi)
run_first_level_analysis(ptseries_file, subj_id, ses_id, output_dir, regressor_file_path)




