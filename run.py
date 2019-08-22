#!/opt/Anaconda2/bin/python

from __future__ import print_function
import argparse
import os
import nibabel
from glob import glob
from subprocess import Popen, PIPE
import subprocess
from bids.grabbids import BIDSLayout
from functools import partial
from collections import OrderedDict
import pdb
from rsfMRI_seed import write_regressor


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


def run_Generatefsf_level1_processing(**args):
    args.update(os.environ)
    cmd = '/generate_level1_fsf.sh ' + \
        '--taskname="{fmriname}" ' + \
        '--temporalfilter="{highpass}" ' + \
        '--originalsmoothing="{fmrires}" ' + \
        '--outdir="{outdir}" '
    cmd = cmd.format(**args)
    run(cmd, cwd=args["outdir"])

def run_Generatefsf_level2_processing(**args):
    args.update(os.environ)
    cmd = '/generate_level2_fsf.sh ' + \
        '--taskname="{fmriname}" ' + \
        '--temporalfilter="{highpass}" ' + \
        '--originalsmoothing="{fmrires}" ' + \
        '--outdir="{outdir}" '
    cmd = cmd.format(**args)
    run(cmd, cwd=args["outdir"])

def run_seed_level1_rsfMRI_processing(**args):
    args.update(os.environ)
    os.system("export PATH=/usr/local/fsl/bin:${PATH}")
    cmd = '/RestfMRILevel1.sh ' + \
        '--outdir={outdir} ' + \
        '--ICAoutputs={ICAoutputs} ' + \
        '--pipeline={pipeline} ' + \
        '--finalfile={finalfile} ' + \
        '--volfinalfile={vol_finalfile} ' + \
        '--boldref={bold_ref} ' + \
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
    cmd = cmd.format(**args)
    run(cmd, cwd=args["outdir"])

def run_seed_level2_rsfMRI_processing(**args):
    args.update(os.environ)
    os.system("export PATH=/usr/local/fsl/bin:${PATH}")
    cmd = '/RestfMRILevel2.sh ' + \
        '--outdir={outdir} ' + \
        '--ICAoutputs={ICAoutputs} ' + \
        '--pipeline={pipeline} ' + \
        '--fmrifilenames={fmrifilename} ' + \
        '--lvl2fmrifoldername={level_2_foldername} ' + \
        '--finalsmoothingFWHM={smoothing:d} ' + \
        '--temporalfilter={temporal_filter} ' + \
        '--regname={regname} ' + \
        '--parcellation={parcel_name} ' + \
        '--seedROI={seedROI}'
    cmd = cmd.format(**args)
    run(cmd, cwd=args["outdir"])

parser = argparse.ArgumentParser(description='')
parser.add_argument('input_dir', help='The directory where the preprocessed derivative needed live')
parser.add_argument('output_dir', help='The directory where the output files should be stored.')
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
parser.add_argument('--stages',help='Which stages to run. Space separated list. ',nargs="+", choices=['rsfMRISeedAnalysis', 'Generatefsf'],default=['Generatefsf', 'rsfMRISeedAnalysis'])
parser.add_argument('--combine_resting_scans',help='If multiple of the same resting state BIDS file type exist should they be combined prior seed analysis? Choices include "Y/yes" or "N/no".',choices=['Yes','yes','No','no'],default='No')
parser.add_argument('--smoothing',help="What FWHM smoothing (in mm) to apply to final output",default=4, type=int)
parser.add_argument('--parcellation_file', help='The CIFTI label file to use or used to parcellate the brain. ', default='NONE')
parser.add_argument('--parcellation_name', help='Shorthand name of the CIFTI label file. ', default='NONE')
parser.add_argument('--seed_ROI_name', help='Space separated list of ROI name/s from CIFTI label file to be used as the seed ROI/s. The exact ROI from the label file must be known!', nargs="+")
parser.add_argument('--seed_handling', help='Of the ROI/s you have provided do you want to treat them as together (i.e. averaging ROIs together), or separate (run separate seed based analyses for each ROI)? '
                                        'Choices are "together", or "separate". Default argument is "separate".',
                                        choices=['together', 'separate'],
                                        default='separate')
parser.add_argument('--seed_analysis_output',help='The output of the seed based analysis. Choices are "dense" (i.e. dtseries.nii) and "parcellated" (i.e. ptseries.nii)).',choices = ['dense','parcellated'], default = 'dense')
parser.add_argument('--motion_confounds',help='What type of motion confounds to use, if any. Choices are "Movement_Regressors" (motion rotation angles and translations in mm), '
                                        ' "Movement_Regressors_dt" (detrended motion rotation angles and translations in mm), "Movement_Regressors_demean" (demeaned motion rotation angles and translations in mm) "Movement_RelativeRMS" (RMS intensity difference of volume N to the reference volume), '
                                        ' "Movement_RelativeRMS_mean" (square of RMS intensity difference of volume N to the reference volume), "Movement_AbsoluteRMS" (absolute RMS intensity difference of volume N to the reference volume, '
                                        ' "Movement_AbsoluteRMS_mean" (square of absolute RMS intensity difference of volume N to the reference volume), "dvars" ( RMS intensity difference of volume N to volume N+1 (see Power et al, NeuroImage, 59(3), 2012)), '
                                        ' "fd" ( frame displacement (average of rotation and translation parameter differences - using weighted scaling, as in Power et al.))', 
                                        choices = ['NONE','Movement_Regressors','Movement_Regressors_dt','Movement_RelativeRMS','Movement_RelativeRMS_mean','Movement_AbsoluteRMS','Movement_AbsoluteRMS_mean','dvars','fd'],default='NONE')
args = parser.parse_args()

# global variables
highpass = "2000"
lowresmesh = 32   
highresmesh = 164
smoothing = args.smoothing
parcel_file = args.parcellation_file
parcel_name = args.parcellation_name
seed_ROI_name = args.seed_ROI_name
seed_handling = args.seed_handling
seed_analysis_output = args.seed_analysis_output
msm_all_reg_name = "MSMAll_2_d40_WRN"
preprocessing_type = args.preprocessing_type
motion_confounds = args.motion_confounds

if preprocessing_type == 'HCP':
    if not motion_confounds == 'NONE':
        motion_confounds_dict = {'Movement_Regressors': 'Movement_Regressors.txt',
        'Movement_Regressors_dt': 'Movement_Regressors_dt.txt',
        'Movement_Regressors_demean': 'Movement_Regressors_demean.txt',
        'Movement_RelativeRMS': 'Movement_RelativeRMS.txt',
        'Movement_RelativeRMS_mean': 'Movement_RelativeRMS_mean.txt',
        'Movement_AbsoluteRMS': 'Movement_AbsoluteRMS.txt',
        'Movement_AbsoluteRMS_mean': 'Movement_AbsoluteRMS_mean.txt',
        'dvars': 'Movement_dvars.txt',
        'fd': 'Movement_fd.txt'}
        motion_confounds_filename = motion_confounds_dict[motion_confounds]
    else:
        motion_confounds_filename = 'NONE'
elif preprocessing_type == 'fmriprep' and motion_confounds != 'NONE':
    pass

 # use ICA outputs
if args.use_ICA_outputs == 'yes' or args.use_ICA_outputs == 'Yes':
    ICAoutputs = 'YES'
else:
    ICAoutputs = 'NO'

# need a subject label in order to start
if args.participant_label:
    subject_label=args.participant_label[0]
    layout = BIDSLayout(os.path.join(args.input_dir,'sub-'+subject_label))
else:
    raise ValueError('An argument must be specified for participant label. Quitting.')
# if subject label has sessions underneath those need to be outputted into different directories
if args.session_label:
    ses_to_analyze = args.session_label
else:
    ses_to_analyze = layout.get_sessions(subject=subject_label)

if ses_to_analyze:
    for ses_label in ses_to_analyze:
        # initialize level 2 variables
        if args.combine_resting_scans == 'No' or args.combine_resting_scans == 'no':
            level_2_foldername = 'NONE'
        else:
            level_2_foldername = 'sub-'+ subject_label+ '_ses-' + ses_label+'_rsfMRI_combined'
        # set output folder path
        outdir=args.output_dir + "/sub-%s/ses-%s" % (subject_label, ses_label)
        if preprocessing_type == 'HCP':
            # use ICA outputs
            if ICAoutputs == 'YES':
                
                bolds = [f.filename for f in layout.get(subject=subject_label, session=ses_label,type='clean',
                extensions="dtseries.nii", task='rest',) if msm_all_reg_name+'_hp2000_clean' in f.filename]
            # do not use ICA outputs
            else:
                bolds = [f.filename for f in layout.get(subject=subject_label, session=ses_label,
                extensions="dtseries.nii", task='rest') if msm_all_reg_name + '_hp2000' in f.filename and not 'clean' in f.filename]

        elif preprocessing_type == 'fmriprep':
            #use ICA outputs
            if ICAoutputs == 'YES':
                bolds = [f.filename for f in layout.get(subject=subject_label,session=ses_label,type='bold',task='rest') if 'smoothAROMAnonaggr' in f.filename]
            # do not use ICA outputs
            else:
                bolds = [f.filename for f in layout.get(subject=subject_label,session=ses_label,type='bold',task='rest') if 'preproc' in f.filename]
            # will need bold reference images
            bolds_ref = [f.filename for f in layout.get(subject=subject_label,session=ses_label,type='boldref',task='rest')]
        # store list of fmrinames for level 2 analysis
        if level_2_foldername == 'sub-'+ subject_label+ '_ses-' + ses_label+'_rsfMRI_combined':
            fmrinames = []
        for idx,fmritcs in enumerate(bolds):
            if preprocessing_type == 'HCP':
                if ICAoutputs == 'YES':
                    vol_fmritcs=fmritcs.replace('_Atlas_MSMAll_2_d40_WRN_hp2000_clean.dtseries.nii','_hp2000_clean.nii.gz')
                else:
                    vol_fmritcs = fmritcs.replace('_Atlas_MSMAll_2_d40_WRN_hp2000.dtseries.nii','_hp2000.nii.gz')
                zooms = nibabel.load(vol_fmritcs).get_header().get_zooms()
                fmrires = str(int(min(zooms[:3])))
                shortfmriname=fmritcs.split("/")[-2]
                # create confounds if dvars or fd selected
                if motion_confounds_filename == 'Movement_dvars.txt':
                    os.system("${FSL_DIR}/bin/fsl_motion_outliers -i " + vol_fmritcs + \
                                    " -o " + outdir + "/sub-" + subject_label + "/ses-" + \
                                        ses_label + "/MNINonLinear/" + "Results/" + shortfmriname + "/" + motion_confounds_filename + " --dvars")
                elif motion_confounds_filename == 'Movement_fd.txt':
                    os.system("${FSL_DIR}/bin/fsl_motion_outliers -i " + vol_fmritcs + \
                                    " -o " + outdir + "/sub-" + subject_label + "/ses-" + \
                                        ses_label + "/MNINonLinear/" + "Results/" + shortfmriname + "/" + motion_confounds_filename + " --fd")
                # create full path to confounds file if not 'NONE'
                if motion_confounds_filename != 'NONE' and ICAoutputs == 'YES':
                    motion_confounds_filepath = fmritcs.replace(shortfmriname+'_Atlas_MSMAll_2_d40_WRN_hp2000_clean.dtseries.nii',motion_confounds_filename)
                elif motion_confounds_filename != 'NONE' and ICAoutputs == 'NO':
                    motion_confounds_filepath = fmritcs.replace(shortfmriname+'_Atlas_MSMAll_2_d40_WRN_hp2000.dtseries.nii',motion_confounds_filename)
                AtlasFolder='/'.join(fmritcs.split("/")[0:5])
                # Determine locations of necessary directories (using expected naming convention)
                DownSampleFolder=AtlasFolder + "/fsaverage_LR" + str(lowresmesh) + "k"
                ResultsFolder=AtlasFolder+"/Results"
                ROIsFolder=AtlasFolder+"/ROIs"
                fmriname = os.path.basename(fmritcs).split(".")[0]
                if level_2_foldername == 'sub-'+ subject_label+ '_ses-' + ses_label+'_rsfMRI_combined':
                    fmrinames.append(fmriname)
                assert fmriname
                bold_ref = "NONE"
            elif preprocessing_type == 'fmriprep':
                #reference image
                bold_ref = bolds_ref[idx]
                vol_fmritcs='NONE'

            if len(seed_ROI_name) > 1:
                if seed_handling == "together":
                    separator = "-"
                    seed_ROI_merged_string = separator.join(seed_ROI_name)
                    regressor_file = seed_ROI_merged_string + '-Regressor.txt'
                    if preprocessing_type == 'HCP':
                        write_regressor(outdir,fmritcs, parcel_file, seed_ROI_name, regressor_file)
                    elif preprocessing_type == 'fmriprep':
                        pass
                    if not regressor_file:
                        raise Exception("variable 'regressor_file' does not exist. Something failed within rsfMRI_seed.py. Must exit")
                    if seed_analysis_output == 'dense':
                        parcel_file = "NONE"
                        parcel_name = "NONE"
                    rsfMRI_seed_stages_dict = OrderedDict([("Generatefsf", partial(run_Generatefsf_level1_processing,
                                                                                outdir=outdir,
                                                                                fmriname=fmriname,
                                                                                highpass=highpass,
                                                                                fmrires=fmrires)),
                                                    ("rsfMRISeedAnalysis", partial(run_seed_level1_rsfMRI_processing,
                                                                                    outdir=outdir,
                                                                                    pipeline=preprocessing_type,
                                                                                    ICAoutputs=ICAoutputs,
                                                                                    finalfile=fmritcs,
                                                                                    vol_finalfile=vol_fmritcs,
                                                                                    bold_ref=bold_ref,
                                                                                    fmrifilename=fmriname,
                                                                                    fmrifoldername=shortfmriname,
                                                                                    DownSampleFolder=DownSampleFolder,
                                                                                    ResultsFolder=ResultsFolder,
                                                                                    ROIsFolder=ROIsFolder,
                                                                                    lowresmesh=lowresmesh,
                                                                                    confound=motion_confounds_filepath,
                                                                                    fmrires=fmrires,
                                                                                    smoothing=smoothing,
                                                                                    temporal_filter=highpass,
                                                                                    parcel_file=parcel_file,
                                                                                    parcel_name=parcel_name,
                                                                                    regname=msm_all_reg_name,
                                                                                    seedROI=seed_ROI_merged_string))])
                    for stage, stage_func in rsfMRI_seed_stages_dict.iteritems():
                        if stage in args.stages:
                            stage_func()
                else:
                    for seed in seed_ROI_name:
                        parcel_file = args.parcellation_file
                        parcel_name = args.parcellation_name
                        regressor_file = seed + '-Regressor.txt'
                        if preprocessing_type == 'HCP':
                            write_regressor(outdir,fmritcs, parcel_file, seed_ROI_name, regressor_file)
                        elif preprocessing_type == 'fmriprep':
                            pass
                        if not regressor_file:
                            raise Exception("variable 'regressor_file' does not exist. Something failed within rsfMRI_seed.py. Must exit")
                        if seed_analysis_output == 'dense':
                            parcel_file = "NONE"
                            parcel_name = "NONE"
                        rsfMRI_seed_stages_dict = OrderedDict([("Generatefsf", partial(run_Generatefsf_level1_processing,
                                                                outdir=outdir,
                                                                fmriname=fmriname,
                                                                highpass=highpass,
                                                                fmrires=fmrires)),
                                ("rsfMRISeedAnalysis", partial(run_seed_level1_rsfMRI_processing,
                                                                outdir=outdir,
                                                                DownSampleFolder=DownSampleFolder,
                                                                ResultsFolder=ResultsFolder,
                                                                ROIsFolder=ROIsFolder,
                                                                pipeline=preprocessing_type,
                                                                ICAoutputs=ICAoutputs,
                                                                finalfile=fmritcs,    
                                                                confound=motion_confounds_filepath,                                     
                                                                vol_finalfile=vol_fmritcs,
                                                                bold_ref=bold_ref,
                                                                fmrifilename=fmriname,
                                                                fmrifoldername=shortfmriname,
                                                                lowresmesh=lowresmesh,
                                                                fmrires=fmrires,
                                                                smoothing=smoothing,
                                                                temporal_filter=highpass,
                                                                parcel_file=parcel_file,
                                                                parcel_name=parcel_name,
                                                                regname=msm_all_reg_name,
                                                                seedROI=seed))])

                        for stage, stage_func in rsfMRI_seed_stages_dict.iteritems():
                            if stage in args.stages:
                                stage_func()
            elif len(seed_ROI_name) == 1:
                regressor_file = seed_ROI_name[0] + '-Regressor.txt'
                if preprocessing_type == 'HCP':
                    write_regressor(outdir,fmritcs, parcel_file, seed_ROI_name, regressor_file)
                elif preprocessing_type == 'fmriprep':
                    pass
                if not regressor_file:
                    raise Exception("variable 'regressor_file' does not exist. Something failed within rsfMRI_seed.py. Must exit")
                if seed_analysis_output == 'dense':
                    parcel_file = "NONE"
                    parcel_name = "NONE"
                rsfMRI_seed_stages_dict = OrderedDict([("Generatefsf", partial(run_Generatefsf_level1_processing,
                                                                outdir=outdir,
                                                                fmriname=fmriname,
                                                                highpass=highpass,
                                                                fmrires=fmrires)),
                                ("rsfMRISeedAnalysis", partial(run_seed_level1_rsfMRI_processing,
                                                                outdir=outdir,
                                                                DownSampleFolder=DownSampleFolder,
                                                                ResultsFolder=ResultsFolder,
                                                                ROIsFolder=ROIsFolder,
                                                                pipeline=preprocessing_type,
                                                                ICAoutputs=ICAoutputs,
                                                                finalfile=fmritcs,
                                                                vol_finalfile=vol_fmritcs,
                                                                confound=motion_confounds_filepath,
                                                                bold_ref=bold_ref,
                                                                fmrifilename=fmriname,
                                                                fmrifoldername=shortfmriname,
                                                                lowresmesh=lowresmesh,
                                                                fmrires=fmrires,
                                                                smoothing=smoothing,
                                                                temporal_filter=highpass,
                                                                parcel_file=parcel_file,
                                                                parcel_name=parcel_name,
                                                                regname=msm_all_reg_name,
                                                                seedROI=seed_ROI_name[0]))])
                for stage, stage_func in rsfMRI_seed_stages_dict.iteritems():
                    if stage in args.stages:
                        stage_func()
    if level_2_foldername == 'sub-'+ subject_label+ '_ses-' + ses_label+'_rsfMRI_combined':
        # convert list to string expected by RestfMRILevel2.sh
        fmrinames = '@'.join(str(i) for i in fmrinames)
        if len(seed_ROI_name) > 1:
            if seed_handling == "together":
                seed = seed_ROI_merged_string
            else:
                for seed in seed_ROI_name:        
                    rsfMRI_seed_stages_dict = OrderedDict([("Generatefsf", partial(run_Generatefsf_level2_processing,
                                                                outdir=outdir,
                                                                fmriname=level_2_foldername,
                                                                highpass=highpass,
                                                                fmrires=fmrires)),
                                                ("rsfMRISeedAnalysis", partial(run_seed_level2_rsfMRI_processing,
                                                                outdir=outdir,
                                                                pipeline=preprocessing_type,
                                                                ICAoutputs=ICAoutputs,
                                                                fmrifilename=fmrinames,
                                                                level_2_foldername=level_2_foldername,
                                                                smoothing=smoothing,
                                                                temporal_filter=highpass,
                                                                regname=msm_all_reg_name,
                                                                parcel_name=parcel_name,
                                                                seedROI=seed))])
                                                                
                    for stage, stage_func in rsfMRI_seed_stages_dict.iteritems():
                        if stage in args.stages:
                            stage_func()
        elif len(seed_ROI_name) == 1:
            seed = seed_ROI_name[0]
        rsfMRI_seed_stages_dict = OrderedDict([("Generatefsf", partial(run_Generatefsf_level2_processing,
                                                                outdir=outdir,
                                                                fmriname=level_2_foldername,
                                                                highpass=highpass,
                                                                fmrires=fmrires)),
                                                ("rsfMRISeedAnalysis", partial(run_seed_level2_rsfMRI_processing,
                                                                outdir=outdir,
                                                                pipeline=preprocessing_type,
                                                                ICAoutputs=ICAoutputs,
                                                                fmrifilename=fmrinames,
                                                                level_2_foldername=level_2_foldername,
                                                                smoothing=smoothing,
                                                                temporal_filter=highpass,
                                                                regname=msm_all_reg_name,
                                                                parcel_name=parcel_name,
                                                                seedROI=seed))])
        
        for stage, stage_func in rsfMRI_seed_stages_dict.iteritems():
            if stage in args.stages:
                stage_func()

else:
    # initialize level 2 variables
    if args.combine_resting_scans == 'No' or args.combine_resting_scans == 'no':
        level_2_foldername = 'NONE'
    else:
        level_2_foldername = 'sub-' + subject_label+ '_rsfMRI_combined'
    outdir=args.output_dir + "/sub-%s" % (subject_label)
    # retrieve preprocessing BIDS layout for participant specified
    if preprocessing_type == 'HCP':
        # use ICA outputs
        if ICAoutputs == 'YES':
            bolds = [f.filename for f in layout.get(subject=subject_label, type='clean',
            extensions="dtseries.nii", task='rest',) if msm_all_reg_name+'_hp2000_clean' in f.filename]
        # do not use ICA outputs
        else:
            bolds = [f.filename for f in layout.get(subject=subject_label,
            extensions="dtseries.nii", task='rest') if msm_all_reg_name + '_hp2000' in f.filename and not 'clean' in f.filename]
    elif preprocessing_type == 'fmriprep':
        #use ICA outputs
        if ICAoutputs == 'YES':
            bolds = [f.filename for f in layout.get(subject=subject_label,type='bold',task='rest') if 'smoothAROMAnonaggr' in f.filename]
        # do not use ICA outputs
        else:
            bolds = [f.filename for f in layout.get(subject=subject_label,type='bold',task='rest') if 'preproc' in f.filename]
        bolds_ref = [f.filename for f in layout.get(subject=subject_label,session=ses_label,type='boldref',task='rest')]
    for idx,fmritcs in enumerate(bolds):
        if preprocessing_type == 'HCP':
            if ICAoutputs == 'YES':
                vol_fmritcs=fmritcs.replace('_Atlas_MSMAll_2_d40_WRN_hp2000_clean.dtseries.nii','_hp2000_clean.nii.gz')
            else:
                vol_fmritcs = fmritcs.replace('_Atlas_MSMAll_2_d40_WRN_hp2000.dtseries.nii','_hp2000.nii.gz')
            
            zooms = nibabel.load(vol_fmritcs).get_header().get_zooms()
            fmrires = str(int(min(zooms[:3])))
            shortfmriname=fmritcs.split("/")[-2]
            # create confounds if dvars or fd selected
            if motion_confounds_filename == 'Movement_dvars.txt':
                os.system("${FSL_DIR}/bin/fsl_motion_outliers -i " + vol_fmritcs + \
                        " -o " + outdir + "/sub-" + subject_label + "/ses-" + \
                        ses_label + "/MNINonLinear/" + "Results/" + shortfmriname + "/" + motion_confounds_filename + " --dvars")
            elif motion_confounds_filename == 'Movement_fd.txt':
                os.system("${FSL_DIR}/bin/fsl_motion_outliers -i " + vol_fmritcs + \
                            " -o " + outdir + "/sub-" + subject_label + "/ses-" + \
                            ses_label + "/MNINonLinear/" + "Results/" + shortfmriname + "/" + motion_confounds_filename + " --fd")
            # create full path to confounds file if not 'NONE'
            if motion_confounds_filename != 'NONE' and ICAoutputs == 'YES':
                motion_confounds_filepath = fmritcs.replace(shortfmriname+'_Atlas_MSMAll_2_d40_WRN_hp2000_clean.dtseries.nii',motion_confounds_filename)
            elif motion_confounds_filename != 'NONE' and ICAoutputs == 'NO':
                motion_confounds_filepath = fmritcs.replace(shortfmriname+'_Atlas_MSMAll_2_d40_WRN_hp2000.dtseries.nii',motion_confounds_filename)
            AtlasFolder='/'.join(fmritcs.split("/")[0:4])
            fmriname = fmritcs.path.basename.split(".")[0]
            assert fmriname
            bold_ref = "NONE"
        elif preprocessing_type == 'fmriprep':
            bold_ref = bolds_ref[idx]
            vol_fmritcs="NONE"
        if len(seed_ROI_name) > 1:
            if seed_handling == "together":
                separator = "-"
                seed_ROI_merged_string = separator.join(seed_ROI_name)
                regressor_file = seed_ROI_merged_string + '-Regressor.txt'
                if preprocessing_type == 'HCP':
                    write_regressor(fmritcs, parcel_file, seed_ROI_name, regressor_file)
                elif preprocessing_type == 'fmriprep':
                    pass
                if not regressor_file:
                    raise Exception("variable 'regressor_file' does not exist. Something failed within rsfMRI_seed.py. Must exit")
                if seed_analysis_output == 'dense':
                    parcel_file = "NONE"
                    parcel_name = "NONE"
                rsfMRI_seed_stages_dict = OrderedDict([("Generatefsf", partial(run_Generatefsf_level1_processing,
                                                                        outdir=outdir,
                                                                        fmriname=fmriname,
                                                                        highpass=highpass,
                                                                        fmrires=fmrires)),
                                            ("rsfMRISeedAnalysis", partial(run_seed_level1_rsfMRI_processing,
                                                                        outdir=outdir,
                                                                        DownSampleFolder=DownSampleFolder,
                                                                        ResultsFolder=ResultsFolder,
                                                                        ROIsFolder=ROIsFolder,
                                                                        pipeline=preprocessing_type,
                                                                        ICAoutputs=ICAoutputs,
                                                                        finalfile=fmritcs,
                                                                        vol_finalfile=vol_fmritcs,
                                                                        bold_ref=bold_ref,
                                                                        fmrifilename=fmriname,
                                                                        fmrifoldername=shortfmriname,
                                                                        lowresmesh=lowresmesh,
                                                                        fmrires=fmrires,
                                                                        smoothing=smoothing,
                                                                        temporal_filter=highpass,
                                                                        confound=motion_confounds_filepath,
                                                                        parcel_file=parcel_file,
                                                                        parcel_name=parcel_name,
                                                                        regname=msm_all_reg_name,
                                                                        seedROI=seed_ROI_merged_string))])

                for stage, stage_func in rsfMRI_seed_stages_dict.iteritems():
                    if stage in args.stages:
                        stage_func()
            else:
                for seed in seed_ROI_name:
                    regressor_file = seed + '-Regressor.txt'
                    if preprocessing_type == 'HCP':
                        write_regressor(fmritcs, parcel_file, seed, regressor_file)
                    elif preprocessing_type == 'fmriprep':
                        pass
                    if not regressor_file:
                        raise Exception("variable 'regressor_file' does not exist. Something failed within rsfMRI_seed.py. Must exit")
                    if seed_analysis_output == 'dense':
                        parcel_file = "NONE"
                        parcel_name = "NONE"
                    rsfMRI_seed_stages_dict = OrderedDict([("Generatefsf", partial(run_Generatefsf_level1_processing,
                                                                    outdir=outdir,
                                                                    fmriname=fmriname,
                                                                    highpass=highpass,
                                                                    fmrires=fmrires)),
                                            ("rsfMRISeedAnalysis", partial(run_seed_level1_rsfMRI_processing,
                                                                    outdir=outdir,
                                                                    DownSampleFolder=DownSampleFolder,
                                                                    ResultsFolder=ResultsFolder,
                                                                    ROIsFolder=ROIsFolder,
                                                                    pipeline=preprocessing_type,
                                                                    vol_finalfile=vol_fmritcs,
                                                                    ICAoutputs=ICAoutputs,
                                                                    finalfile=fmritcs,
                                                                    bold_ref = bolds_ref[idx],
                                                                    fmrifilename=fmriname,
                                                                    fmrifoldername=shortfmriname,
                                                                    lowresmesh=lowresmesh,
                                                                    fmrires=fmrires,
                                                                    smoothing=smoothing,
                                                                    confound=motion_confounds_filepath,
                                                                    temporal_filter=highpass,
                                                                    parcel_file=parcel_file,
                                                                    parcel_name=parcel_name,
                                                                    regname=msm_all_reg_name,
                                                                    seedROI=seed))])
                    for stage, stage_func in rsfMRI_seed_stages_dict.iteritems():
                        if stage in args.stages:
                            stage_func()
        elif len(seed_ROI_name) == 1:
            regressor_file = seed_ROI_name[0] + '-Regressor.txt'
            write_regressor(fmritcs, parcel_file, seed_ROI_name, regressor_file)
            if not regressor_file:
                raise Exception("variable 'regressor_file' does not exist. Something failed within rsfMRI_seed.py. Must exit")
            if seed_analysis_output == 'dense':
                parcel_file = "NONE"
                parcel_name = "NONE"
            rsfMRI_seed_stages_dict = OrderedDict([("Generatefsf", partial(run_Generatefsf_level1_processing,
                                                                    outdir=outdir,
                                                                    fmriname=fmriname,
                                                                    highpass=highpass,
                                                                    fmrires=fmrires)),
                                            ("rsfMRISeedAnalysis", partial(run_seed_level1_rsfMRI_processing,
                                                                    outdir=outdir,
                                                                    DownSampleFolder=DownSampleFolder,
                                                                    ResultsFolder=ResultsFolder,
                                                                    ROIsFolder=ROIsFolder,
                                                                    pipeline=preprocessing_type,
                                                                    ICAoutputs=ICAoutputs,
                                                                    vol_finalfile=vol_fmritcs,
                                                                    finalfile=fmritcs,
                                                                    bold_ref = bolds_ref[idx],
                                                                    fmrifilename=fmriname,
                                                                    fmrifoldername=shortfmriname,
                                                                    lowresmesh=lowresmesh,
                                                                    fmrires=fmrires,
                                                                    smoothing=smoothing,
                                                                    confound=motion_confounds_filepath,
                                                                    temporal_filter=highpass,
                                                                    parcel_file=parcel_file,
                                                                    parcel_name=parcel_name,
                                                                    regname=msm_all_reg_name,
                                                                    seedROI=seed_ROI_name[0]))])
            for stage, stage_func in rsfMRI_seed_stages_dict.iteritems():
                if stage in args.stages:
                    stage_func()
    if level_2_foldername == 'sub-' + subject_label+ '_rsfMRI_combined':
        # convert list to string expected by RestfMRILevel2.sh
        fmrinames = '@'.join(str(i) for i in fmrinames)
        if len(seed_ROI_name) > 1:
            if seed_handling == "together":
                seed = seed_ROI_merged_string
            else:
                for seed in seed_ROI_name:        
                    rsfMRI_seed_stages_dict = OrderedDict([("Generatefsf", partial(run_Generatefsf_level2_processing,
                                                            outdir=outdir,
                                                            fmriname=level_2_foldername,
                                                            highpass=highpass,
                                                            fmrires=fmrires)),
                                            ("rsfMRISeedAnalysis", partial(run_seed_level2_rsfMRI_processing,
                                                            outdir=outdir,
                                                            pipeline=preprocessing_type,
                                                            ICAoutputs=ICAoutputs,
                                                            fmrifilename=fmrinames,
                                                            level_2_foldername=level_2_foldername,
                                                            smoothing=smoothing,
                                                            temporal_filter=highpass,
                                                            regname=msm_all_reg_name,
                                                            parcel_name=parcel_name,
                                                            seedROI=seed))])
                                                            
                    for stage, stage_func in rsfMRI_seed_stages_dict.iteritems():
                        if stage in args.stages:
                            stage_func()
        elif len(seed_ROI_name) == 1:
            seed = seed_ROI_name[0]
        rsfMRI_seed_stages_dict = OrderedDict([("Generatefsf", partial(run_Generatefsf_level2_processing,
                                                            outdir=outdir,
                                                            fmriname=level_2_foldername,
                                                            highpass=highpass,
                                                            fmrires=fmrires)),
                                            ("rsfMRISeedAnalysis", partial(run_seed_level2_rsfMRI_processing,
                                                            outdir=outdir,
                                                            pipeline=preprocessing_type,
                                                            ICAoutputs=ICAoutputs,
                                                            fmrifilename=fmrinames,
                                                            level_2_foldername=level_2_foldername,
                                                            smoothing=smoothing,
                                                            temporal_filter=highpass,
                                                            regname=msm_all_reg_name,
                                                            parcel_name=parcel_name,
                                                            seedROI=seed))])
    
        for stage, stage_func in rsfMRI_seed_stages_dict.iteritems():
            if stage in args.stages:
                stage_func()