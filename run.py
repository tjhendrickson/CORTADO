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
from rsfMRI_seed import SeedIO
import dask

@dask.delayed
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

@dask.delayed
def run_Generatefsf_level1_processing(**args):
    args.update(os.environ)
    cmd = '/generate_level1_fsf.sh ' + \
        '--taskname="{fmriname}" ' + \
        '--temporalfilter="{highpass}" ' + \
        '--originalsmoothing="{fmrires}" ' + \
        '--outdir="{outdir}" '
    cmd = cmd.format(**args)
    run(cmd, cwd=args["outdir"])

@dask.delayed
def run_Generatefsf_level2_processing(**args):
    args.update(os.environ)
    cmd = '/generate_level2_fsf.sh ' + \
        '--taskname="{fmriname}" ' + \
        '--temporalfilter="{highpass}" ' + \
        '--originalsmoothing="{fmrires}" ' + \
        '--outdir="{outdir}" '
    cmd = cmd.format(**args)
    run(cmd, cwd=args["outdir"])

@dask.delayed
def run_seed_level1_rsfMRI_processing(**args):
    args.update(os.environ)
    os.system("export PATH=/usr/local/fsl/bin:${PATH}")
    cmd = '/RestfMRILevel1.sh ' + \
        '--outdir={outdir} ' + \
        '--ICAoutputs={ICAstring} ' + \
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

@dask.delayed
def run_seed_level2_rsfMRI_processing(**args):
    args.update(os.environ)
    os.system("export PATH=/usr/local/fsl/bin:${PATH}")
    cmd = '/RestfMRILevel2.sh ' + \
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
    cmd = cmd.format(**args)
    run(cmd, cwd=args["outdir"])

parser = argparse.ArgumentParser(description='')
parser.add_argument('input_dir', help='The directory where the preprocessed derivative needed live')
parser.add_argument('output_dir', help='The directory where the output files should be stored.')
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
parser.add_argument('--reg_name',help='What type of registration do you want to use? Choices are "MSMAll_2_d40_WRN" and "NONE"',choices = ['NONE','MSMAll_2_d40_WRN'],default='MSMAll_2_d40_WRN')
parser.add_argument('--text_output_format',help='What format should the text output be in? Choices are "CSV" or "NONE"', choices=['CSV',"csv",'none','NONE'],default='NONE')
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
text_output_format = args.text_output_format
selected_reg_name = args.reg_name
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
        motion_confounds_filepath = 'NONE'
elif preprocessing_type == 'fmriprep' and motion_confounds != 'NONE':
    pass

 # use ICA outputs
if args.use_ICA_outputs == 'yes' or args.use_ICA_outputs == 'Yes':
    ICAoutputs = 'YES'
else:
    ICAoutputs = 'NO'

# check on arguments
print("Running CORTADO ")
layout = BIDSLayout(os.path.join(args.input_dir))
if args.seed_ROI_name:
    print('\t-Seed ROI selected: %s' %str(seed_ROI_name))
else:
    print('\n')
    raise ValueError('Selecting a seed name of interest must be specified after argument "--seed_ROI_name" is required. Exiting.')
print('\t-Seed ROI handling: %s' %str(seed_handling))
print('\t-Seed analysis output: %s' %str(seed_analysis_output))
if seed_analysis_output == 'dense':
    print('\t-Spatial smoothing applied: %smm' %str(smoothing))
elif seed_analysis_output == 'parcellated':
    if parcel_file == 'NONE':
        print('\n')
        raise ValueError('Parcellating output selected but no parcel file specified after argument "--parcellation_file". Exiting.')
    else:
        print('\t-Parcellation file to be used to parcellate outputs: %s' %str(parcel_file))
    if parcel_name == 'NONE':
        print('\n')
        raise ValueError('Parcellating output selected but no parcel name specified after argument "--parcellation_name". Exiting.')
    else:
        print('\t-Short hand parcellation name to be used: %s' %str(parcel_name))
print('\t-Input registration file to be used: %s' %str(selected_reg_name))
print('\t-Whether motion confounds will be used for output: %s' %str(motion_confounds))
print('\t-The preprocessing pipeline that the input comes from: %s' %str(preprocessing_type))
print('\t-Use ICA outputs: %s' %str(ICAoutputs))
print('\t-Use mixed effects if multiple of same acquisition: %s' %str(args.combine_resting_scans))
print('\t-Text output format: %s' %str(args.text_output_format))
print('\n')

# if # of session larger than zero, iterate on that
def run_CORTADO(scanning_sessions):
    if layout.get_sessions() > 0:
        for ses_label in scanning_sessions:
            subject_label = layout.get(session=ses_label,target='subject',return_type='id')[0]
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
                    ICAstring="_FIXclean"
                    if selected_reg_name == msm_all_reg_name:
                        bolds = [f.filename for f in layout.get(subject=subject_label, session=ses_label,type='clean',
                                                                extensions="dtseries.nii", task='rest',) if msm_all_reg_name+'_hp2000_clean' in f.filename]
                    else:
                        bolds = [f.filename for f in layout.get(subject=subject_label, session=ses_label,type='clean',
                                                                extensions="dtseries.nii", task='rest',) if '_hp2000_clean' and not msm_all_reg_name in f.filename]        
                # do not use ICA outputs
                else:
                    ICAstring=""
                    if selected_reg_name == msm_all_reg_name:
                        bolds = [f.filename for f in layout.get(subject=subject_label, session=ses_label,
                                                                extensions="dtseries.nii", task='rest') if msm_all_reg_name + '_hp2000' in f.filename and not 'clean' in f.filename]
                    else:
                        bolds = [f.filename for f in layout.get(subject=subject_label, session=ses_label,
                                                                extensions="dtseries.nii", task='rest') if '_hp2000' in f.filename and not 'clean' and not msm_all_reg_name in f.filename]
            elif preprocessing_type == 'fmriprep':
                #use ICA outputs
                if ICAoutputs == 'YES':
                    ICAstring="_AROMAclean"
                    bolds = [f.filename for f in layout.get(subject=subject_label,session=ses_label,type='bold',task='rest') if 'smoothAROMAnonaggr' in f.filename]
                # do not use ICA outputs
                else:
                    ICAstring=""
                    bolds = [f.filename for f in layout.get(subject=subject_label,session=ses_label,type='bold',task='rest') if 'preproc' in f.filename]
                # will need bold reference images
                bolds_ref = [f.filename for f in layout.get(subject=subject_label,session=ses_label,type='boldref',task='rest')]
            # store list of fmrinames for level 2 analysis
            if level_2_foldername == 'sub-'+ subject_label+ '_ses-' + ses_label+'_rsfMRI_combined':
                fmrinames = []
            for idx,fmritcs in enumerate(bolds):
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
                        if preprocessing_type == 'HCP':
                            SeedIO_init = SeedIO(outdir,fmritcs, parcel_file, parcel_name, seed_ROI_name)
                            regressor_file = SeedIO_init.write_regressor()
                            seed_ROI_merged_string = os.path.basename(regressor_file).split('-Regressor.txt')[0]
                        elif preprocessing_type == 'fmriprep':
                            pass
                        if not regressor_file:
                            raise Exception("variable 'regressor_file' does not exist. Something failed within rsfMRI_seed.py. Must exit")
                        if seed_analysis_output == 'dense':
                            rsfMRI_seed_stages_dict = OrderedDict([("Generatefsf", partial(run_Generatefsf_level1_processing,
                                                                                    outdir=outdir,
                                                                                    fmriname=fmriname,
                                                                                    highpass=highpass,
                                                                                    fmrires=fmrires)),
                                                        ("rsfMRISeedAnalysis", partial(run_seed_level1_rsfMRI_processing,
                                                                                        outdir=outdir,
                                                                                        pipeline=preprocessing_type,
                                                                                        ICAstring=ICAstring,
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
                                                                                        parcel_file="NONE",
                                                                                        parcel_name="NONE",
                                                                                        regname=selected_reg_name,
                                                                                        seedROI=seed_ROI_merged_string))])
                            for stage, stage_func in rsfMRI_seed_stages_dict.iteritems():
                                if stage in args.stages:
                                    stage_func()
                            if preprocessing_type == 'HCP':
                                if level_2_foldername == 'NONE' and seed_analysis_output == 'parcellated':
                                    if text_output_format == 'csv' or text_output_format == 'CSV':
                                        SeedIO_init.create_text_output(ICAstring=ICAstring,level=1)
    
                        else:
                            rsfMRI_seed_stages_dict = OrderedDict([("Generatefsf", partial(run_Generatefsf_level1_processing,
                                                                                    outdir=outdir,
                                                                                    fmriname=fmriname,
                                                                                    highpass=highpass,
                                                                                    fmrires=fmrires)),
                                                        ("rsfMRISeedAnalysis", partial(run_seed_level1_rsfMRI_processing,
                                                                                        outdir=outdir,
                                                                                        pipeline=preprocessing_type,
                                                                                        ICAstring=ICAstring,
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
                                                                                        regname=selected_reg_name,
                                                                                        seedROI=seed_ROI_merged_string))])
                            # run through creation of data first, then handle easy output creation
                            for stage, stage_func in rsfMRI_seed_stages_dict.iteritems():
                                if stage in args.stages:
                                    stage_func()
                            if preprocessing_type == 'HCP':
                                if level_2_foldername == 'NONE' and seed_analysis_output == 'parcellated':
                                    if text_output_format == 'csv' or text_output_format == 'CSV':
                                        SeedIO_init.create_text_output(ICAstring=ICAstring,level=1)
                    else:
                        for seed in seed_ROI_name:
                            if preprocessing_type == 'HCP':
                                SeedIO_init = SeedIO(outdir,fmritcs, parcel_file, parcel_name, seed)
                                regressor_file = SeedIO_init.write_regressor()
                            elif preprocessing_type == 'fmriprep':
                                pass
                            if not regressor_file:
                                raise Exception("variable 'regressor_file' does not exist. Something failed within rsfMRI_seed.py. Must exit")
                            if seed_analysis_output == 'dense':
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
                                                                    ICAstring=ICAstring,
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
                                                                    parcel_file="NONE",
                                                                    parcel_name="NONE",
                                                                    regname=selected_reg_name,
                                                                    seedROI=seed))])
    
                            else:
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
                                                                    ICAstring=ICAstring,
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
                                                                    regname=selected_reg_name,
                                                                    seedROI=seed))])
    
                            for stage, stage_func in rsfMRI_seed_stages_dict.iteritems():
                                if stage in args.stages:
                                    stage_func()
                            if preprocessing_type == 'HCP':
                                if level_2_foldername == 'NONE' and seed_analysis_output == 'parcellated':
                                    if text_output_format == 'csv' or text_output_format == 'CSV':
                                        SeedIO_init.create_text_output(ICAstring=ICAstring,text_output_dir=args.output_dir,level=1)
                elif len(seed_ROI_name) == 1:
                    if preprocessing_type == 'HCP':
                        SeedIO_init = SeedIO(outdir,fmritcs, parcel_file, parcel_name, seed_ROI_name[0])
                        regressor_file = SeedIO_init.write_regressor()
                    elif preprocessing_type == 'fmriprep':
                        pass
                    if not regressor_file:
                        raise Exception("variable 'regressor_file' does not exist. Something failed within rsfMRI_seed.py. Must exit")
                    if seed_analysis_output == 'dense':
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
                                                                    ICAstring=ICAstring,
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
                                                                    parcel_file="NONE",
                                                                    parcel_name="NONE",
                                                                    regname=selected_reg_name,
                                                                    seedROI=seed_ROI_name[0]))])
                    else:
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
                                                                    ICAstring=ICAstring,
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
                                                                    regname=selected_reg_name,
                                                                    seedROI=seed_ROI_name[0]))])
                    for stage, stage_func in rsfMRI_seed_stages_dict.iteritems():
                        if stage in args.stages:
                            stage_func()
                    if preprocessing_type == 'HCP':
                        if level_2_foldername == 'NONE' and seed_analysis_output == 'parcellated':
                                if text_output_format == 'csv' or text_output_format == 'CSV':
                                    SeedIO_init.create_text_output(ICAstring=ICAstring,text_output_dir=args.output_dir,level=1)
            if level_2_foldername == 'sub-'+ subject_label+ '_ses-' + ses_label+'_rsfMRI_combined':
                # convert list to string expected by RestfMRILevel2.sh
                fmrinames = '@'.join(str(i) for i in fmrinames)
                if seed_analysis_output == 'dense':
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
                                                                            ICAstring=ICAstring,
                                                                            fmrifilename=fmrinames,
                                                                            level_2_foldername=level_2_foldername,
                                                                            smoothing=smoothing,
                                                                            temporal_filter=highpass,
                                                                            regname=selected_reg_name,
                                                                            parcel_name="NONE",
                                                                            seedROI=seed))])
    
                                for stage, stage_func in rsfMRI_seed_stages_dict.iteritems():
                                    if stage in args.stages:
                                        stage_func()
                                pdb.set_trace()
                                if preprocessing_type == 'HCP':
                                    if seed_analysis_output == 'parcellated':
                                        if text_output_format == 'csv' or text_output_format == 'CSV':
                                            SeedIO_init.create_text_output(ICAstring=ICAstring,text_output_dir=args.output_dir,level=2)
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
                                                                            ICAstring=ICAstring,
                                                                            fmrifilename=fmrinames,
                                                                            level_2_foldername=level_2_foldername,
                                                                            smoothing=smoothing,
                                                                            temporal_filter=highpass,
                                                                            regname=selected_reg_name,
                                                                            parcel_name="NONE",
                                                                            seedROI=seed))])
                else:
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
                                                                            ICAstring=ICAstring,
                                                                            fmrifilename=fmrinames,
                                                                            level_2_foldername=level_2_foldername,
                                                                            smoothing=smoothing,
                                                                            temporal_filter=highpass,
                                                                            regname=selected_reg_name,
                                                                            parcel_name=parcel_name,
                                                                            seedROI=seed))])
    
                                for stage, stage_func in rsfMRI_seed_stages_dict.iteritems():
                                    if stage in args.stages:
                                        stage_func()
    else:
        for subject_label in scanning_sessions:
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
                    ICAstring="_FIXclean"
                    if selected_reg_name == msm_all_reg_name:
                        bolds = [f.filename for f in layout.get(subject=subject_label, type='clean',
                                                                extensions="dtseries.nii", task='rest',) if msm_all_reg_name+'_hp2000_clean' in f.filename]
                    else:
                        bolds = [f.filename for f in layout.get(subject=subject_label, type='clean',
                                                                extensions="dtseries.nii", task='rest',) if '_hp2000_clean' and not msm_all_reg_name in f.filename]
                # do not use ICA outputs
                else:
                    ICAstring=""
                    if selected_reg_name == msm_all_reg_name:
                        bolds = [f.filename for f in layout.get(subject=subject_label,
                                                                extensions="dtseries.nii", task='rest') if msm_all_reg_name + '_hp2000' in f.filename and not 'clean' in f.filename]
                    else:
                        bolds = [f.filename for f in layout.get(subject=subject_label,
                                                                extensions="dtseries.nii", task='rest') if '_hp2000' in f.filename and not 'clean' and not msm_all_reg_name in f.filename]
    
            elif preprocessing_type == 'fmriprep':
                #use ICA outputs
                if ICAoutputs == 'YES':
                    ICAstring="_AROMAclean"
                    bolds = [f.filename for f in layout.get(subject=subject_label,type='bold',task='rest') if 'smoothAROMAnonaggr' in f.filename]
                # do not use ICA outputs
                else:
                    ICAstring=""
                    bolds = [f.filename for f in layout.get(subject=subject_label,type='bold',task='rest') if 'preproc' in f.filename]
                bolds_ref = [f.filename for f in layout.get(subject=subject_label,session=ses_label,type='boldref',task='rest')]
            for idx,fmritcs in enumerate(bolds):
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
    
                    AtlasFolder='/'.join(fmritcs.split("/")[0:4])
                    fmriname = fmritcs.path.basename.split(".")[0]
                    assert fmriname
                    bold_ref = "NONE"
                elif preprocessing_type == 'fmriprep':
                    bold_ref = bolds_ref[idx]
                    vol_fmritcs="NONE"
                if len(seed_ROI_name) > 1:
                    if seed_handling == "together":
                        if preprocessing_type == 'HCP':
                            SeedIO_init = SeedIO(outdir,fmritcs, parcel_file, parcel_name, seed_ROI_name)
                            regressor_file = SeedIO_init.write_regressor()
                            seed_ROI_merged_string = os.path.basename(regressor_file).split('-Regressor.txt')[0]
                        elif preprocessing_type == 'fmriprep':
                            pass
                        if not regressor_file:
                            raise Exception("variable 'regressor_file' does not exist. Something failed within rsfMRI_seed.py. Must exit")
                        if seed_analysis_output == 'dense':
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
                                                                                ICAstring=ICAstring,
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
                                                                                parcel_file="NONE",
                                                                                parcel_name="NONE",
                                                                                regname=selected_reg_name,
                                                                                seedROI=seed_ROI_merged_string))])
                        else:
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
                                                                                ICAstring=ICAstring,
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
                                                                                regname=selected_reg_name,
                                                                                seedROI=seed_ROI_merged_string))])
    
                        for stage, stage_func in rsfMRI_seed_stages_dict.iteritems():
                            if stage in args.stages:
                                stage_func()
                        if preprocessing_type == 'HCP':
                            if level_2_foldername == 'NONE' and seed_analysis_output == 'parcellated':
                                    if text_output_format == 'csv' or text_output_format == 'CSV':
                                        SeedIO_init.create_text_output(ICAstring=ICAstring,level=1)
                    else:
                        for seed in seed_ROI_name:
                            if preprocessing_type == 'HCP':
                                SeedIO_init = SeedIO(outdir,fmritcs, parcel_file, parcel_name, seed)
                                regressor_file = SeedIO_init.write_regressor()
                            elif preprocessing_type == 'fmriprep':
                                pass
                            if not regressor_file:
                                raise Exception("variable 'regressor_file' does not exist. Something failed within rsfMRI_seed.py. Must exit")
                            if seed_analysis_output == 'dense':
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
                                                                            ICAstring=ICAstring,
                                                                            finalfile=fmritcs,
                                                                            bold_ref = bolds_ref[idx],
                                                                            fmrifilename=fmriname,
                                                                            fmrifoldername=shortfmriname,
                                                                            lowresmesh=lowresmesh,
                                                                            fmrires=fmrires,
                                                                            smoothing=smoothing,
                                                                            confound=motion_confounds_filepath,
                                                                            temporal_filter=highpass,
                                                                            parcel_file="NONE",
                                                                            parcel_name="NONE",
                                                                            regname=selected_reg_name,
                                                                            seedROI=seed))])
                            else:
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
                                                                            ICAstring=ICAstring,
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
                                                                            regname=selected_reg_name,
                                                                            seedROI=seed))])
                            for stage, stage_func in rsfMRI_seed_stages_dict.iteritems():
                                if stage in args.stages:
                                    stage_func()
                            if preprocessing_type == 'HCP':
                                if level_2_foldername == 'NONE' and seed_analysis_output == 'parcellated':
                                    if text_output_format == 'csv' or text_output_format == 'CSV':
                                        SeedIO_init.create_text_output(ICAstring=ICAstring,level=1)
                elif len(seed_ROI_name) == 1:
                    if preprocessing_type == 'HCP':
                        SeedIO_init = SeedIO(outdir,fmritcs, parcel_file, parcel_name, seed_ROI_name[0])
                        regressor_file = SeedIO_init.write_regressor()
                    if not regressor_file:
                        raise Exception("variable 'regressor_file' does not exist. Something failed within rsfMRI_seed.py. Must exit")
                    if seed_analysis_output == 'dense':
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
                                                                            ICAstring=ICAstring,
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
                                                                            parcel_file="NONE",
                                                                            parcel_name="NONE",
                                                                            regname=selected_reg_name,
                                                                            seedROI=seed_ROI_name[0]))])
    
                    else:
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
                                                                            ICAstring=ICAstring,
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
                                                                            regname=selected_reg_name,
                                                                            seedROI=seed_ROI_name[0]))])
                    for stage, stage_func in rsfMRI_seed_stages_dict.iteritems():
                        if stage in args.stages:
                            stage_func()
                    if preprocessing_type == 'HCP':
                        if level_2_foldername == 'NONE' and seed_analysis_output == 'parcellated':
                                    if text_output_format == 'csv' or text_output_format == 'CSV':
                                        SeedIO_init.create_text_output(ICAstring=ICAstring,level=1)
            if level_2_foldername == 'sub-' + subject_label+ '_rsfMRI_combined':
                # convert list to string expected by RestfMRILevel2.sh
                fmrinames = '@'.join(str(i) for i in fmrinames)
                if seed_analysis_output == 'dense':
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
                                                                        ICAstring=ICAstring,
                                                                        fmrifilename=fmrinames,
                                                                        level_2_foldername=level_2_foldername,
                                                                        smoothing=smoothing,
                                                                        temporal_filter=highpass,
                                                                        regname=selected_reg_name,
                                                                        parcel_name="NONE",
                                                                        seedROI=seed))])
    
                                for stage, stage_func in rsfMRI_seed_stages_dict.iteritems():
                                    if stage in args.stages:
                                        stage_func()
                                if preprocessing_type == 'HCP':
                                    if seed_analysis_output == 'parcellated':
                                        if text_output_format == 'csv' or text_output_format == 'CSV':
                                            SeedIO_init.create_text_output(ICAstring=ICAstring,level=2)                       
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
                                                                        ICAstring=ICAstring,
                                                                        fmrifilename=fmrinames,
                                                                        level_2_foldername=level_2_foldername,
                                                                        smoothing=smoothing,
                                                                        temporal_filter=highpass,
                                                                        regname=selected_reg_name,
                                                                        parcel_name="NONE",
                                                                        seedROI=seed))])
                else:
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
                                                                        ICAstring=ICAstring,
                                                                        fmrifilename=fmrinames,
                                                                        level_2_foldername=level_2_foldername,
                                                                        smoothing=smoothing,
                                                                        temporal_filter=highpass,
                                                                        regname=selected_reg_name,
                                                                        parcel_name=parcel_name,
                                                                        seedROI=seed))])
    
                                for stage, stage_func in rsfMRI_seed_stages_dict.iteritems():
                                    if stage in args.stages:
                                        stage_func()
                                if preprocessing_type == 'HCP':
                                    if seed_analysis_output == 'parcellated':
                                        if text_output_format == 'csv' or text_output_format == 'CSV':
                                            SeedIO_init.create_text_output(ICAstring=ICAstring,level=2)
                                    
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
                                                                        ICAstring=ICAstring,
                                                                        fmrifilename=fmrinames,
                                                                        level_2_foldername=level_2_foldername,
                                                                        smoothing=smoothing,
                                                                        temporal_filter=highpass,
                                                                        regname=selected_reg_name,
                                                                        parcel_name=parcel_name,
                                                                        seedROI=seed))])
                for stage, stage_func in rsfMRI_seed_stages_dict.iteritems():
                    if stage in args.stages:
                        stage_func()
                if preprocessing_type == 'HCP':
                    if seed_analysis_output == 'parcellated':
                        if text_output_format == 'csv' or text_output_format == 'CSV':
                            SeedIO_init.create_text_output(ICAstring=ICAstring,level=2)[0]
                    rsfMRI_seed_stages_dict = OrderedDict([("Generatefsf", partial(run_Generatefsf_level2_processing,
                                                                            outdir=outdir,
                                                                            fmriname=level_2_foldername,
                                                                            highpass=highpass,
                                                                            fmrires=fmrires)),
                                                            ("rsfMRISeedAnalysis", partial(run_seed_level2_rsfMRI_processing,
                                                                            outdir=outdir,
                                                                            pipeline=preprocessing_type,
                                                                            ICAstring=ICAstring,
                                                                            fmrifilename=fmrinames,
                                                                            level_2_foldername=level_2_foldername,
                                                                            smoothing=smoothing,
                                                                            temporal_filter=highpass,
                                                                            regname=selected_reg_name,
                                                                            parcel_name=parcel_name,
                                                                            seedROI=seed))])
    
                for stage, stage_func in rsfMRI_seed_stages_dict.iteritems():
                    if stage in args.stages:
                        stage_func()
                if preprocessing_type == 'HCP':
                    if seed_analysis_output == 'parcellated':
                        if text_output_format == 'csv' or text_output_format == 'CSV':
                            SeedIO_init.create_text_output(ICAstring=ICAstring,text_output_dir=args.output_dir,level=2)
                            
                            
if layout.get_sessions() > 0:
    scanning_sessions = layout.get_sessions()
else:
    scanning_sessions = layout.get_subjects()
dask.compute(run_CORTADO(scanning_sessions))