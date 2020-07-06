#!/opt/Miniconda3/bin/python

from __future__ import print_function
import argparse
import os
from bids.grabbids import BIDSLayout
from functools import partial
from rsfMRI_seed import regression, pair_pair_connectivity
from multiprocessing import Pool, Lock
import time
import pdb

def generate_motion_confounds(vol_fmritcs,base_folder,fmritcs,selected_reg_name):
    shortfmriname=base_folder.split('/')[-1]
    if motion_confounds_filename == 'Movement_dvars.txt':
        os.system("${FSL_DIR}/bin/fsl_motion_outliers -i " + vol_fmritcs + \
                    " -o " + base_folder + "/" + motion_confounds_filename + " --dvars")
    elif motion_confounds_filename == 'Movement_fd.txt':
        os.system("${FSL_DIR}/bin/fsl_motion_outliers -i " + vol_fmritcs + \
                    " -o " + base_folder + "/" + motion_confounds_filename + " --fd")
    if motion_confounds_filename != 'NONE' and ICAoutputs == 'YES':
        if selected_reg_name == msm_all_reg_name:
            motion_confounds_filepath = fmritcs.replace(shortfmriname+'_Atlas_MSMAll_2_d40_WRN_hp2000_clean.dtseries.nii',motion_confounds_filename)
        else:
            motion_confounds_filepath = fmritcs.replace(shortfmriname+'_Atlas_hp2000_clean.dtseries.nii',motion_confounds_filename)
    elif motion_confounds_filename != 'NONE' and ICAoutputs == 'NO':
        if selected_reg_name == msm_all_reg_name:
            motion_confounds_filepath = fmritcs.replace(shortfmriname+'_Atlas_MSMAll_2_d40_WRN_hp2000.dtseries.nii',motion_confounds_filename)
        else:
            motion_confounds_filepath = fmritcs.replace(shortfmriname+'_Atlas_hp2000.dtseries.nii',motion_confounds_filename)
    else:
        motion_confounds_filepath = 'NONE'
    return motion_confounds_filepath

def first_level_logic(fmritcs,output_dir,seed_ROI_name,seed_handling,
                      ICAstring,statistic,motion_confounds,
                      preprocessing_type,vol_fmritcs,seed_analysis_output,
                      level,text_output_format,smoothing,parcel_file,
                      parcel_name,selected_reg_name):
    shortfmriname = fmritcs.split("/")[-2]
    fmriname = os.path.basename(fmritcs).split(".")[0]
    if not motion_confounds == 'NONE':
        motion_confounds_filepath = generate_motion_confounds(base_folder=os.path.join(output_dir,'MNINonLinear','Results',shortfmriname),
                                                              vol_fmritcs=vol_fmritcs,fmritcs=fmritcs,selected_reg_name=selected_reg_name)
    else:
        motion_confounds_filepath = 'NONE'
    if len(seed_ROI_name) > 1:
        if seed_handling == "together":
            if statistic == 'regression':
                run_regression = regression(output_dir=output_dir,cifti_file=fmritcs,
                       parcel_file=parcel_file,parcel_name=parcel_name,
                       seed_ROI_name=seed_ROI_name,level=1,
                       pipeline=preprocessing_type,ICAstring=ICAstring,
                       vol_fmritcs=vol_fmritcs,
                       confound=motion_confounds_filepath,
                       smoothing=smoothing,regname=selected_reg_name,
                       fmriname=fmriname,
                       fmrifoldername=shortfmriname,
                       seed_analysis_output=seed_analysis_output)
                run_regression.setup()
                if preprocessing_type == 'HCP':
                    if level == 1 and seed_analysis_output == 'parcellated':
                        if not text_output_format == 'none' or not text_output_format == 'NONE':
                            l.acquire()
                            run_regression.create_text_output(text_output_dir=args.output_dir,text_output_format=text_output_format)
                            l.release()
                            time.sleep(1)
            else:
                run_pair_pair_connectivity = pair_pair_connectivity(output_dir=output_dir,cifti_file=fmritcs,
                       parcel_file=parcel_file,parcel_name=parcel_name,
                       seed_ROI_name=seed_ROI_name,level=1,
                       pipeline=preprocessing_type,ICAstring=ICAstring,
                       vol_fmritcs=vol_fmritcs,
                       confound=motion_confounds_filepath,
                       smoothing=smoothing,regname=selected_reg_name,
                       fmriname=fmriname,
                       fmrifoldername=shortfmriname,
                       seed_analysis_output=seed_analysis_output,
                       method=statistic)
                if preprocessing_type == 'HCP':
                    if level == 1 and seed_analysis_output == 'parcellated':
                        if not text_output_format == 'none' or not text_output_format == 'NONE':
                            l.acquire()
                            run_pair_pair_connectivity.create_text_output(text_output_dir=args.output_dir,text_output_format=text_output_format)
                            l.release()
                            time.sleep(1)
        else:
            for seed in seed_ROI_name:
                if statistic == 'regression':
                    run_regression = regression(output_dir=output_dir,cifti_file=fmritcs,
                       parcel_file=parcel_file,parcel_name=parcel_name,
                       seed_ROI_name=seed,level=1,
                       pipeline=preprocessing_type,ICAstring=ICAstring,
                       vol_fmritcs=vol_fmritcs,confound=motion_confounds_filepath,
                       smoothing=smoothing,regname=selected_reg_name,
                       fmriname=fmriname,
                       fmrifoldername=shortfmriname,
                       seed_analysis_output=seed_analysis_output)
                    run_regression.setup()
                    if preprocessing_type == 'HCP':
                        if level == 1 and seed_analysis_output == 'parcellated':
                            if not text_output_format == 'none' or not text_output_format == 'NONE':
                                l.acquire()
                                run_regression.create_text_output(text_output_dir=args.output_dir,text_output_format=text_output_format)
                                l.release()
                                time.sleep(1)
                else:
                    run_pair_pair_connectivity = pair_pair_connectivity(output_dir=output_dir,cifti_file=fmritcs,
                                           parcel_file=parcel_file,parcel_name=parcel_name,
                                           seed_ROI_name=seed,level=1,
                                           pipeline=preprocessing_type,ICAstring=ICAstring,
                                           vol_fmritcs=vol_fmritcs,
                                           confound=motion_confounds_filepath,
                                           smoothing=smoothing,regname=selected_reg_name,
                                           fmriname=fmriname,
                                           fmrifoldername=shortfmriname,
                                           seed_analysis_output=seed_analysis_output,
                                           method=statistic)
                    if preprocessing_type == 'HCP':
                        if level == 1 and seed_analysis_output == 'parcellated':
                            if not text_output_format == 'none' or not text_output_format == 'NONE':
                                l.acquire()
                                run_pair_pair_connectivity.create_text_output(text_output_dir=args.output_dir,text_output_format=text_output_format)
                                l.release()
                                time.sleep(1)
    elif len(seed_ROI_name) == 1:
        if statistic == 'regression':
            run_regression = regression(output_dir=output_dir,cifti_file=fmritcs,
                       parcel_file=parcel_file,parcel_name=parcel_name,
                       seed_ROI_name=seed_ROI_name,level=1,
                       pipeline=preprocessing_type,ICAstring=ICAstring,
                       vol_fmritcs=vol_fmritcs,confound=motion_confounds_filepath,
                       smoothing=smoothing,regname=selected_reg_name,
                       fmriname=fmriname,
                       fmrifoldername=shortfmriname,
                       seed_analysis_output=seed_analysis_output)
            run_regression.setup()
            if preprocessing_type == 'HCP':
                if level == 1 and seed_analysis_output == 'parcellated':
                    if not text_output_format == 'none' or not text_output_format == 'NONE':
                        l.acquire()
                        run_regression.create_text_output(text_output_dir=args.output_dir,text_output_format=text_output_format)
                        l.release()
                        time.sleep(1)
        else:
            run_pair_pair_connectivity = pair_pair_connectivity(output_dir=output_dir,cifti_file=fmritcs,
                       parcel_file=parcel_file,parcel_name=parcel_name,
                       seed_ROI_name=seed_ROI_name,level=1,
                       pipeline=preprocessing_type,ICAstring=ICAstring,
                       vol_fmritcs=vol_fmritcs,
                       confound=motion_confounds_filepath,
                       smoothing=smoothing,regname=selected_reg_name,
                       fmriname=fmriname,
                       fmrifoldername=shortfmriname,
                       seed_analysis_output=seed_analysis_output,
                       method=statistic)
            if preprocessing_type == 'HCP':
                    if level == 1 and seed_analysis_output == 'parcellated':
                        if not text_output_format == 'none' or not text_output_format == 'NONE':
                            l.acquire()
                            run_pair_pair_connectivity.create_text_output(text_output_dir=args.output_dir,text_output_format=text_output_format)
                            l.release()
                            time.sleep(1)
def run_CORTADO(bold, ICAstring, preprocessing_type, smoothing, parcel_file,
                               parcel_name, seed_ROI_name, seed_handling,
                               seed_analysis_output, text_output_format,
                               selected_reg_name, motion_confounds, ICAoutputs,
                               combine_resting_scans,output_dir,statistic):
    pdb.set_trace()
    if combine_resting_scans == 'Yes' or combine_resting_scans == 'yes':
        fmritcs = bold[0]
        level = 2
    elif combine_resting_scans == 'No' or combine_resting_scans == 'no':
        fmritcs = bold
        level = 1

    if preprocessing_type == 'HCP':
        if ICAoutputs == 'YES':
            if selected_reg_name == msm_all_reg_name:
                vol_fmritcs=fmritcs.replace('_Atlas_MSMAll_2_d40_WRN_hp2000_clean.dtseries.nii','_hp2000_clean.nii.gz')
            else:
                vol_fmritcs=fmritcs.replace('_Atlas_hp2000_clean.dtseries.nii','_hp2000_clean.nii.gz')
        else:
            if selected_reg_name == msm_all_reg_name:
                vol_fmritcs = fmritcs.replace('_Atlas_MSMAll_2_d40_WRN_hp2000.dtseries.nii','_hp2000.nii.gz')
            else:
                vol_fmritcs = fmritcs.replace('_Atlas_hp2000.dtseries.nii','_hp2000.nii.gz')

    if 'ses' in fmritcs:
        subject_label = fmritcs.split('sub-')[1].split('/')[0]
        ses_label = fmritcs.split('ses-')[1].split('/')[0]
        # set output folder path
        output_dir=output_dir + "/sub-%s/ses-%s" % (subject_label, ses_label)
    else:
        subject_label = fmritcs.split('sub-')[1].split('/')[0]
        output_dir=output_dir + "/sub-%s" % (subject_label)
    if combine_resting_scans == 'Yes' or combine_resting_scans == 'yes':
        fmrinames = []
        for fmritcs in bold:
            if statistic == 'regression':
                first_level_logic(fmritcs=fmritcs,output_dir=output_dir,
                seed_ROI_name=seed_ROI_name,
                seed_handling=seed_handling,
                ICAstring=ICAstring,
                statistic=statistic,
                motion_confounds=motion_confounds,
                preprocessing_type=preprocessing_type,
                vol_fmritcs=vol_fmritcs,
                seed_analysis_output=seed_analysis_output,
                level=level,
                text_output_format=text_output_format,
                smoothing=smoothing,
                parcel_file=parcel_file,
                parcel_name=parcel_name,
                selected_reg_name=selected_reg_name)
                fmriname = os.path.basename(fmritcs).split(".")[0] 
            else:
                fmriname = fmritcs
            fmrinames.append(fmriname)
        if len(seed_ROI_name) > 1:
            if seed_handling == "together":
                if preprocessing_type == 'HCP':
                    if statistic == 'regression':
                        run_regression = regression(output_dir=output_dir,cifti_file='', 
                               parcel_file=parcel_file, parcel_name=parcel_name, 
                               seed_ROI_name=seed_ROI_name,
                               level=level,
                               pipeline=preprocessing_type,
                               ICAstring=ICAstring,
                               vol_fmritcs=vol_fmritcs,
                               confound='',
                               smoothing=smoothing,
                               regname=selected_reg_name,
                               fmriname=fmrinames,
                               fmrifoldername='rsfMRI_combined',
                               seed_analysis_output=seed_analysis_output)
                        run_regression.setup()
                        if preprocessing_type == 'HCP':
                            if seed_analysis_output == 'parcellated':
                                if not text_output_format == 'none' or not text_output_format == 'NONE':
                                    l.acquire()
                                    run_regression.create_text_output(text_output_dir=args.output_dir,text_output_format=text_output_format)
                                    l.release()
                                    time.sleep(1)
                    else:
                        run_pair_pair_connectivity = pair_pair_connectivity(output_dir=output_dir,cifti_file='', 
                               parcel_file=parcel_file, parcel_name=parcel_name, 
                               seed_ROI_name=seed_ROI_name,
                               level=level,
                               pipeline=preprocessing_type,
                               ICAstring=ICAstring,
                               vol_fmritcs='',
                               confound='',
                               smoothing=smoothing,
                               regname=selected_reg_name,
                               fmriname=fmrinames,
                               fmrifoldername='rsfMRI_combined',
                               seed_analysis_output=seed_analysis_output,
                               method=statistic)
                        if preprocessing_type == 'HCP':
                            if seed_analysis_output == 'parcellated':
                                if not text_output_format == 'none' or not text_output_format == 'NONE':
                                    l.acquire()
                                    run_pair_pair_connectivity.create_text_output(text_output_dir=args.output_dir,text_output_format=text_output_format)
                                    l.release()
                                    time.sleep(1)                        
            else:
                for seed in seed_ROI_name:
                    if statistic == 'regression':
                        run_regression = regression(output_dir=output_dir,cifti_file='', 
                               parcel_file=parcel_file, parcel_name=parcel_name, 
                               seed_ROI_name=seed,
                               level=level,
                               pipeline=preprocessing_type,
                               ICAstring=ICAstring,
                               vol_fmritcs=vol_fmritcs,
                               confound='',
                               smoothing=smoothing,
                               regname=selected_reg_name,
                               fmriname=fmrinames,
                               fmrifoldername='rsfMRI_combined',
                               seed_analysis_output=seed_analysis_output)
                        run_regression.setup()
                        if preprocessing_type == 'HCP':
                            if seed_analysis_output == 'parcellated':
                                if not text_output_format == 'none' or not text_output_format == 'NONE':
                                    l.acquire()
                                    run_regression.create_text_output(text_output_dir=args.output_dir,text_output_format=text_output_format)
                                    l.release()
                                    time.sleep(1)
                    else:
                        run_pair_pair_connectivity = pair_pair_connectivity(output_dir=output_dir,cifti_file='', 
                               parcel_file=parcel_file, parcel_name=parcel_name, 
                               seed_ROI_name=seed,
                               level=level,
                               pipeline=preprocessing_type,
                               ICAstring=ICAstring,
                               vol_fmritcs='',
                               confound='',
                               smoothing=smoothing,
                               regname=selected_reg_name,
                               fmriname=fmrinames,
                               fmrifoldername='rsfMRI_combined',
                               seed_analysis_output=seed_analysis_output,
                               method=statistic)
                        if preprocessing_type == 'HCP':
                            if seed_analysis_output == 'parcellated':
                                if not text_output_format == 'none' or not text_output_format == 'NONE':
                                    l.acquire()
                                    run_pair_pair_connectivity.create_text_output(text_output_dir=args.output_dir,text_output_format=text_output_format)
                                    l.release()
                                    time.sleep(1)
        elif len(seed_ROI_name) == 1:
            if statistic == 'regression':
                run_regression = regression(output_dir=output_dir,cifti_file='', 
                               parcel_file=parcel_file, parcel_name=parcel_name, 
                               seed_ROI_name=seed_ROI_name,
                               level=level,
                               pipeline=preprocessing_type,
                               ICAstring=ICAstring,
                               vol_fmritcs=vol_fmritcs,
                               confound='',
                               smoothing=smoothing,
                               regname=selected_reg_name,
                               fmriname=fmrinames,
                               fmrifoldername='rsfMRI_combined',
                               seed_analysis_output=seed_analysis_output)
                run_regression.setup()
                if preprocessing_type == 'HCP':
                    if seed_analysis_output == 'parcellated':
                        if not text_output_format == 'none' or not text_output_format == 'NONE':
                            l.acquire()
                            run_regression.create_text_output(text_output_dir=args.output_dir,text_output_format=text_output_format)
                            l.release()
                            time.sleep(1)
            else:
                run_pair_pair_connectivity = pair_pair_connectivity(output_dir=output_dir,cifti_file='', 
                               parcel_file=parcel_file, parcel_name=parcel_name, 
                               seed_ROI_name=seed_ROI_name,
                               level=level,
                               pipeline=preprocessing_type,
                               ICAstring=ICAstring,
                               vol_fmritcs='',
                               confound='',
                               smoothing=smoothing,
                               regname=selected_reg_name,
                               fmriname=fmrinames,
                               fmrifoldername='rsfMRI_combined',
                               seed_analysis_output=seed_analysis_output,
                               method=statistic)
                if preprocessing_type == 'HCP':
                    if seed_analysis_output == 'parcellated':
                        if not text_output_format == 'none' or not text_output_format == 'NONE':
                            l.acquire()
                            run_pair_pair_connectivity.create_text_output(text_output_dir=args.output_dir,text_output_format=text_output_format)
                            l.release()
                            time.sleep(1)
    else:
        first_level_logic(fmritcs=fmritcs,output_dir=output_dir,
                                            seed_ROI_name=seed_ROI_name,
                                            seed_handling=seed_handling,
                                            ICAstring=ICAstring,
                                            statistic=statistic,
                                            motion_confounds=motion_confounds,
                                            preprocessing_type=preprocessing_type,
                                            vol_fmritcs=vol_fmritcs,
                                            seed_analysis_output=seed_analysis_output,
                                            level=level,
                                            text_output_format=text_output_format,
                                            smoothing=smoothing,
                                            parcel_file=parcel_file,
                                            parcel_name=parcel_name,
                                            selected_reg_name=selected_reg_name)
    
parser = argparse.ArgumentParser(description='')
parser.add_argument('--input_dir', help='The directory where the preprocessed derivative needed live',required=True)
parser.add_argument('--output_dir', help='The directory where the output files should be stored.',required=True)
parser.add_argument('--group', help='Whether to run this participant by participant or the entire group. Choices are "participant" or "batch". If participant by participant "--participant_label" and "--session_label" must be specified',choices = ['participant','batch'],required=True)
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
parser.add_argument('--preprocessing_type', help='BIDS-apps preprocessing pipeline run on data. Choices include "HCP" and "fmriprep". ',choices=['HCP','fmriprep'],default='HCP')
parser.add_argument('--use_ICA_outputs',help='Use ICA (whether FIX or AROMA) outputs in seed analysis. Choices include "Y/yes" or "N/no".',choices=['Yes','yes','No','no'],default='Yes')
parser.add_argument('--combine_resting_scans',help='If multiple of the same resting state BIDS file type exist should they be combined prior seed analysis? Choices include "Y/yes" or "N/no".',choices=['Yes','yes','No','no'],default='No')
parser.add_argument('--smoothing',help="What FWHM smoothing (in mm) to apply to final output",default=4, type=int)
parser.add_argument('--parcellation_file', help='The CIFTI label/atlas file to use or used to parcellate the brain. ', required=True)
parser.add_argument('--parcellation_name', help='Shorthand name of the CIFTI label file. ', required=True)
parser.add_argument('--seed_ROI_name', help='Space separated list of ROI name/s from CIFTI label file to be used as the seed ROI/s. The exact ROI from the label file must be known!', nargs="+",required=True)
parser.add_argument('--seed_handling', help='Of the ROI/s you have provided do you want to treat them as together (i.e. averaging ROIs together), or separate (run separate seed based analyses for each ROI)? '
                                        'Choices are "together", or "separate". Default argument is "separate".',
                                        choices=['together', 'separate'],
                                        default='separate')
parser.add_argument('--seed_analysis_output',help='The output of the seed based analysis. Choices are "dense" (i.e. dtseries.nii) and "parcellated" (i.e. ptseries.nii)).',choices = ['dense','parcellated'], default = 'parcellated')
parser.add_argument('--motion_confounds',help='What type of motion confounds to use, if any. Choices are "Movement_Regressors" (motion rotation angles and translations in mm), '
                                        ' "Movement_Regressors_dt" (detrended motion rotation angles and translations in mm), "Movement_Regressors_demean" (demeaned motion rotation angles and translations in mm) "Movement_RelativeRMS" (RMS intensity difference of volume N to the reference volume), '
                                        ' "Movement_RelativeRMS_mean" (square of RMS intensity difference of volume N to the reference volume), "Movement_AbsoluteRMS" (absolute RMS intensity difference of volume N to the reference volume, '
                                        ' "Movement_AbsoluteRMS_mean" (square of absolute RMS intensity difference of volume N to the reference volume), "dvars" ( RMS intensity difference of volume N to volume N+1 (see Power et al, NeuroImage, 59(3), 2012)), '
                                        ' "fd" ( frame displacement (average of rotation and translation parameter differences - using weighted scaling, as in Power et al.))',
                                        choices = ['NONE','Movement_Regressors','Movement_Regressors_dt','Movement_RelativeRMS','Movement_RelativeRMS_mean','Movement_AbsoluteRMS','Movement_AbsoluteRMS_mean','dvars','fd'],default='NONE')
parser.add_argument('--reg_name',help='What type of registration do you want to use? Choices are "MSMAll_2_d40_WRN" and "NONE"',choices = ['NONE','MSMAll_2_d40_WRN'],default='MSMAll_2_d40_WRN')
parser.add_argument('--text_output_format',help='What format should the text output be in? Choices are "CSV" or "NONE"', choices=['CSV',"csv",'none','NONE'],default='CSV')
parser.add_argument('--num_cpus', help='How many concurrent CPUs to use',default=1)
parser.add_argument('--statistic', help='Strategy to calculate functional connectivity. ' 
                    'Choices are "correlation", and "regression"', 
                    choices=['correlation','partial_correlation','regression','tangent', 'covariance', 'sparse_inverse_covariance', 'precision', 'sparse_inverse_precision'],default='correlation')
# global variables
args = parser.parse_args()
msm_all_reg_name = "MSMAll_2_d40_WRN"
if args.text_output_format == 'CSV' or args.text_output_format == 'csv':
    args.text_output_format = 'csv'

if args.preprocessing_type == 'HCP':
    if not args.motion_confounds == 'NONE':
        motion_confounds_dict = {'Movement_Regressors': 'Movement_Regressors.txt',
        'Movement_Regressors_dt': 'Movement_Regressors_dt.txt',
        'Movement_Regressors_demean': 'Movement_Regressors_demean.txt',
        'Movement_RelativeRMS': 'Movement_RelativeRMS.txt',
        'Movement_RelativeRMS_mean': 'Movement_RelativeRMS_mean.txt',
        'Movement_AbsoluteRMS': 'Movement_AbsoluteRMS.txt',
        'Movement_AbsoluteRMS_mean': 'Movement_AbsoluteRMS_mean.txt',
        'dvars': 'Movement_dvars.txt',
        'fd': 'Movement_fd.txt'}
        motion_confounds_filename = motion_confounds_dict[args.motion_confounds]
    else:
        motion_confounds_filename = 'NONE'
elif args.preprocessing_type == 'fmriprep' and args.motion_confounds != 'NONE':
    pass

if args.group == 'participant':
    if args.participant_label or args.session_label:
        pass
    else:
        print('\n')
        raise ValueError('Selecting "--group participant" must also include either subject or session IDs through "--participant_label" or "--session label" respectively. Exiting.')

 # use ICA outputs
if args.use_ICA_outputs == 'yes' or args.use_ICA_outputs == 'Yes':
    ICAoutputs = 'YES'
else:
    ICAoutputs = 'NO'

# check on arguments
print("Running CORTADO ")
layout = BIDSLayout(os.path.join(args.input_dir))

if args.seed_ROI_name:
    print('\t-Seed ROI selected: %s' %str(args.seed_ROI_name))
else:
    print('\n')
    raise ValueError('Selecting a seed name of interest must be specified after argument "--seed_ROI_name" is required. Exiting.')
print('\t-Seed ROI handling: %s' %str(args.seed_handling))
print('\t-Seed analysis output: %s' %str(args.seed_analysis_output))
if args.seed_analysis_output == 'dense':
    print('\t-Spatial smoothing applied: %smm' %str(args.smoothing))
elif args.seed_analysis_output == 'parcellated':
    print('\t-Parcellation file to be used to parcellate outputs: %s' %str(args.parcellation_file))
    print('\t-Short hand parcellation name to be used: %s' %str(args.parcellation_name))
print('\t-Statistic to use for functional connectivity: %s' %str(args.statistic))
print('\t-Input registration file to be used: %s' %str(args.reg_name))
print('\t-Whether motion confounds will be used for output: %s' %str(args.motion_confounds))
print('\t-The preprocessing pipeline that the input comes from: %s' %str(args.preprocessing_type))
print('\t-Use ICA outputs: %s' %str(ICAoutputs))
print('\t-Use mixed effects if multiple of same acquisition: %s' %str(args.combine_resting_scans))
print('\t-Text output format: %s' %str(args.text_output_format))
print('\t-Whether to run this participant by participant or the entire group: %s' %(str(args.group)))
print('\n')

l = Lock()
multiproc_pool = Pool(int(args.num_cpus))            
if args.combine_resting_scans == 'No' or args.combine_resting_scans == 'no':
    if args.preprocessing_type == 'HCP':
        # use ICA outputs
        if ICAoutputs == 'YES':
            ICAstring="_FIXclean"
            if args.reg_name == msm_all_reg_name:
                if args.group == 'batch':
                    bolds = [f.filename for f in layout.get(type='clean',extensions="dtseries.nii",task='rest') if msm_all_reg_name+'_hp2000_clean' in f.filename]
                else:
                    if args.participant_label:
                        if args.session_label:
                            bolds = [f.filename for f in layout.get(subject=args.participant_label,session=args.session_label,type='clean',extensions="dtseries.nii",task='rest') if msm_all_reg_name+'_hp2000_clean' in f.filename]
                        else:
                            bolds = [f.filename for f in layout.get(subject=args.participant_label,type='clean',extensions="dtseries.nii",task='rest') if msm_all_reg_name+'_hp2000_clean' in f.filename]
            else:
                if args.group == 'batch':
                    bolds = [f.filename for f in layout.get(type='clean',extensions="dtseries.nii", task='rest') if '_hp2000_clean' and not msm_all_reg_name in f.filename]
                else:
                    if args.participant_label:
                        if args.session_label:
                            bolds = [f.filename for f in layout.get(subject=args.participant_label,session=args.session_label,type='clean',extensions="dtseries.nii", task='rest') if '_hp2000_clean' and not msm_all_reg_name in f.filename]
                        else:
                            bolds = [f.filename for f in layout.get(subject=args.participant_label,type='clean',extensions="dtseries.nii", task='rest') if '_hp2000_clean' and not msm_all_reg_name in f.filename]
        # do not use ICA outputs
        else:
            ICAstring=""
            if args.reg_name == msm_all_reg_name:
                if args.group == 'batch':
                    bolds = [f.filename for f in layout.get(extensions="dtseries.nii", task='rest') if msm_all_reg_name + '_hp2000' in f.filename and not 'clean' in f.filename]
                else:
                    if args.participant_label:
                        if args.session_label:
                            bolds = [f.filename for f in layout.get(subject=args.participant_label,session=args.session_label,extensions="dtseries.nii", task='rest') if msm_all_reg_name + '_hp2000' in f.filename and not 'clean' in f.filename]
                        else:
                            bolds = [f.filename for f in layout.get(subject=args.participant_label,extensions="dtseries.nii", task='rest') if msm_all_reg_name + '_hp2000' in f.filename and not 'clean' in f.filename]
            else:
                if args.group == 'batch':
                    bolds = [f.filename for f in layout.get(extensions="dtseries.nii", task='rest') if '_hp2000' in f.filename and not 'clean' and not msm_all_reg_name in f.filename]
                else:
                    if args.participant_label:
                        if args.session_label:
                            bolds = [f.filename for f in layout.get(subject=args.participant_label,session=args.session_label,extensions="dtseries.nii", task='rest') if '_hp2000' in f.filename and not 'clean' and not msm_all_reg_name in f.filename]
                        else:
                            bolds = [f.filename for f in layout.get(subject=args.participant_label,extensions="dtseries.nii", task='rest') if '_hp2000' in f.filename and not 'clean' and not msm_all_reg_name in f.filename]
                            
    elif args.preprocessing_type == 'fmriprep':
        #use ICA outputs
        if ICAoutputs == 'YES':
            ICAstring="_AROMAclean"
            bolds = [f.filename for f in layout.get(type='bold',task='rest') if 'smoothAROMAnonaggr' in f.filename]
        # do not use ICA outputs
        else:
            ICAstring=""
            bolds = [f.filename for f in layout.get(type='bold',task='rest') if 'preproc' in f.filename]
        bolds_ref = [f.filename for f in layout.get(type='boldref',task='rest')]
    # multiproc_pool.map(partial(run_CORTADO,ICAstring=ICAstring, 
    #                            preprocessing_type=args.preprocessing_type,
    #                            smoothing=args.smoothing,
    #                            parcel_file=args.parcellation_file,
    #                            parcel_name=args.parcellation_name,
    #                            seed_ROI_name=args.seed_ROI_name,
    #                            seed_handling=args.seed_handling,
    #                            seed_analysis_output=args.seed_analysis_output,
    #                            text_output_format=args.text_output_format,
    #                            selected_reg_name=args.reg_name,
    #                            motion_confounds=args.motion_confounds,
    #                            ICAoutputs=ICAoutputs,
    #                            combine_resting_scans=args.combine_resting_scans,
    #                            output_dir=args.output_dir,
    #                            statistic=args.statistic),
    #             sorted(bolds))
    run_CORTADO(bold=bolds[0],ICAstring=ICAstring, 
        preprocessing_type=args.preprocessing_type,
        smoothing=args.smoothing,
        parcel_file=args.parcellation_file,
        parcel_name=args.parcellation_name,
        seed_ROI_name=args.seed_ROI_name,
        seed_handling=args.seed_handling,
        seed_analysis_output=args.seed_analysis_output,
        text_output_format=args.text_output_format,
        selected_reg_name=args.reg_name,
        motion_confounds=args.motion_confounds,
        ICAoutputs=ICAoutputs,
        combine_resting_scans=args.combine_resting_scans,
        output_dir=args.output_dir,
        statistic=args.statistic)
else:
    combined_bolds_list = []
    # if there are any sessions, parse data this way
    if args.group == 'batch':
        if len(layout.get_sessions()) > 0:
            for scanning_session in layout.get_sessions():
                # retreive subject id that is associated with session id and parse data with subject and session id
                for subject in layout.get_subjects(session=scanning_session):
                    if args.preprocessing_type == 'HCP':
                        # use ICA outputs
                        if ICAoutputs == 'YES':
                            ICAstring="_FIXclean"
                            if args.reg_name == msm_all_reg_name:
                                if args.group == 'batch':
                                    bolds = [f.filename for f in layout.get(type='clean',extensions="dtseries.nii",task='rest',subject=subject,session=scanning_session) if msm_all_reg_name+'_hp2000_clean' in f.filename]
                            else:
                                bolds = [f.filename for f in layout.get(type='clean',extensions="dtseries.nii", task='rest',subject=subject,session=scanning_session) if '_hp2000_clean' and not msm_all_reg_name in f.filename]
                        # do not use ICA outputs
                        else:
                            ICAstring=""
                            if args.reg_name == msm_all_reg_name:
                                bolds = [f.filename for f in layout.get(extensions="dtseries.nii", task='rest',subject=subject,session=scanning_session) if msm_all_reg_name + '_hp2000' in f.filename and not 'clean' in f.filename]
                            else:
                                bolds = [f.filename for f in layout.get(extensions="dtseries.nii", task='rest',subject=subject,session=scanning_session) if '_hp2000' in f.filename and not 'clean' and not msm_all_reg_name in f.filename]
                    elif args.preprocessing_type == 'fmriprep':
                        #use ICA outputs
                        if ICAoutputs == 'YES':
                            ICAstring="_AROMAclean"
                            bolds = [f.filename for f in layout.get(type='bold',task='rest',subject=subject,session=scanning_session) if 'smoothAROMAnonaggr' in f.filename]
                        # do not use ICA outputs
                        else:
                            ICAstring=""
                            bolds = [f.filename for f in layout.get(type='bold',task='rest') if 'preproc' in f.filename]
                        bolds_ref = [f.filename for f in layout.get(type='boldref',task='rest')]
                    if len(bolds) == 2:
                        combined_bolds_list.append(bolds)
        else:
            for scanning_session in layout.get_subjects():
                if args.preprocessing_type == 'HCP':
                    # use ICA outputs
                    if ICAoutputs == 'YES':
                        ICAstring="_FIXclean"
                        if args.reg_name == msm_all_reg_name:
                            bolds = [f.filename for f in layout.get(type='clean',extensions="dtseries.nii",task='rest',subject=scanning_session) if msm_all_reg_name+'_hp2000_clean' in f.filename]
                        else:
                            bolds = [f.filename for f in layout.get(type='clean',extensions="dtseries.nii", task='rest',subject=scanning_session) if '_hp2000_clean' and not msm_all_reg_name in f.filename]
                    # do not use ICA outputs
                    else:
                        ICAstring=""
                        if args.reg_name == msm_all_reg_name:
                            bolds = [f.filename for f in layout.get(extensions="dtseries.nii", task='rest',subject=scanning_session) if msm_all_reg_name + '_hp2000' in f.filename and not 'clean' in f.filename]
                        else:
                            bolds = [f.filename for f in layout.get(extensions="dtseries.nii", task='rest',subject=scanning_session) if '_hp2000' in f.filename and not 'clean' and not msm_all_reg_name in f.filename]
                elif args.preprocessing_type == 'fmriprep':
                    #use ICA outputs
                    if ICAoutputs == 'YES':
                        ICAstring="_AROMAclean"
                        bolds = [f.filename for f in layout.get(type='bold',task='rest',subject=scanning_session) if 'smoothAROMAnonaggr' in f.filename]
                    # do not use ICA outputs
                    else:
                        ICAstring=""
                        bolds = [f.filename for f in layout.get(type='bold',task='rest') if 'preproc' in f.filename]
                    bolds_ref = [f.filename for f in layout.get(type='boldref',task='rest')]
                if len(bolds) == 2:
                    combined_bolds_list.append(bolds)
    else:
        if args.participant_label:
            if args.session_label:
                if args.preprocessing_type == 'HCP':
                        # use ICA outputs
                        if ICAoutputs == 'YES':
                            ICAstring="_FIXclean"
                            if args.reg_name == msm_all_reg_name:
                                if args.group == 'batch':
                                    bolds = [f.filename for f in layout.get(type='clean',extensions="dtseries.nii",task='rest',subject=args.participant_label,session=args.session_label) if msm_all_reg_name+'_hp2000_clean' in f.filename]
                            else:
                                bolds = [f.filename for f in layout.get(type='clean',extensions="dtseries.nii", task='rest',subject=args.participant_label,session=args.session_label) if '_hp2000_clean' and not msm_all_reg_name in f.filename]
                        # do not use ICA outputs
                        else:
                            ICAstring=""
                            if args.reg_name == msm_all_reg_name:
                                bolds = [f.filename for f in layout.get(extensions="dtseries.nii", task='rest',subject=args.participant_label,session=args.session_label) if msm_all_reg_name + '_hp2000' in f.filename and not 'clean' in f.filename]
                            else:
                                bolds = [f.filename for f in layout.get(extensions="dtseries.nii", task='rest',subject=args.participant_label,session=args.session_label) if '_hp2000' in f.filename and not 'clean' and not msm_all_reg_name in f.filename]
                elif args.preprocessing_type == 'fmriprep':
                    #use ICA outputs
                    if ICAoutputs == 'YES':
                        ICAstring="_AROMAclean"
                        bolds = [f.filename for f in layout.get(type='bold',task='rest',subject=args.participant_label,session=args.session_label) if 'smoothAROMAnonaggr' in f.filename]
                    # do not use ICA outputs
                    else:
                        ICAstring=""
                        bolds = [f.filename for f in layout.get(type='bold',task='rest') if 'preproc' in f.filename]
                    bolds_ref = [f.filename for f in layout.get(type='boldref',task='rest')]
                if len(bolds) == 2:
                    combined_bolds_list.append(bolds)
            else:
                if args.preprocessing_type == 'HCP':
                    # use ICA outputs
                    if ICAoutputs == 'YES':
                        ICAstring="_FIXclean"
                        if args.reg_name == msm_all_reg_name:
                            if args.group == 'batch':
                                bolds = [f.filename for f in layout.get(type='clean',extensions="dtseries.nii",task='rest',subject=args.participant_label) if msm_all_reg_name+'_hp2000_clean' in f.filename]
                        else:
                            bolds = [f.filename for f in layout.get(type='clean',extensions="dtseries.nii", task='rest',subject=args.participant_label) if '_hp2000_clean' and not msm_all_reg_name in f.filename]
                    # do not use ICA outputs
                    else:
                        ICAstring=""
                        if args.reg_name == msm_all_reg_name:
                            bolds = [f.filename for f in layout.get(extensions="dtseries.nii", task='rest',subject=args.participant_label) if msm_all_reg_name + '_hp2000' in f.filename and not 'clean' in f.filename]
                        else:
                            bolds = [f.filename for f in layout.get(extensions="dtseries.nii", task='rest',subject=args.participant_label) if '_hp2000' in f.filename and not 'clean' and not msm_all_reg_name in f.filename]
                elif args.preprocessing_type == 'fmriprep':
                    #use ICA outputs
                    if ICAoutputs == 'YES':
                        ICAstring="_AROMAclean"
                        bolds = [f.filename for f in layout.get(type='bold',task='rest',subject=args.participant_label) if 'smoothAROMAnonaggr' in f.filename]
                    # do not use ICA outputs
                    else:
                        ICAstring=""
                        bolds = [f.filename for f in layout.get(type='bold',task='rest') if 'preproc' in f.filename]
                    bolds_ref = [f.filename for f in layout.get(type='boldref',task='rest')]
                if len(bolds) == 2:
                    combined_bolds_list.append(bolds)
                
    
    # multiproc_pool.map(partial(run_CORTADO,ICAstring=ICAstring, 
    #                        preprocessing_type=args.preprocessing_type,
    #                        smoothing=args.smoothing,
    #                        parcel_file=args.parcellation_file,
    #                        parcel_name=args.parcellation_name,
    #                        seed_ROI_name=args.seed_ROI_name,
    #                        seed_handling=args.seed_handling,
    #                        seed_analysis_output=args.seed_analysis_output,
    #                        text_output_format=args.text_output_format,
    #                        selected_reg_name=args.reg_name,
    #                        motion_confounds=args.motion_confounds,
    #                        ICAoutputs=ICAoutputs,
    #                        combine_resting_scans=args.combine_resting_scans,
    #                        output_dir=args.output_dir,
    #                        statistic=args.statistic),
    # sorted(combined_bolds_list))
    run_CORTADO(bold=combined_bolds_list[0],ICAstring=ICAstring, 
                       preprocessing_type=args.preprocessing_type,
                       smoothing=args.smoothing,
                       parcel_file=args.parcellation_file,
                       parcel_name=args.parcellation_name,
                       seed_ROI_name=args.seed_ROI_name,
                       seed_handling=args.seed_handling,
                       seed_analysis_output=args.seed_analysis_output,
                       text_output_format=args.text_output_format,
                       selected_reg_name=args.reg_name,
                       motion_confounds=args.motion_confounds,
                       ICAoutputs=ICAoutputs,
                       combine_resting_scans=args.combine_resting_scans,
                       output_dir=args.output_dir,
                       statistic=args.statistic)
    