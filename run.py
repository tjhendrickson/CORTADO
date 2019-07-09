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


def run_Generatefsf_processing(**args):
    args.update(os.environ)
    cmd = '{HCPPIPEDIR}/Examples/Scripts/generate_level1_fsf.sh ' + \
        '--studyfolder="{path}" ' + \
        '--subject="{subject}" ' + \
        '--taskname="{shortfmriname}" ' + \
        '--temporalfilter="{highpass}" ' + \
        '--originalsmoothing="{fmrires}" ' + \
        '--regressor_file="{regressor_file}" ' + \
        '--templatedir="{templatedir}" ' + \
        '--outdir="{path}/{subject}/MNINonLinear/Results/{fmriname}" '
    cmd = cmd.format(**args)
    run(cmd, cwd=args["path"])
        
def run_seed_FirstLevel_rsfMRI_processing(**args):
    args.update(os.environ)
    os.system("export PATH=/usr/local/fsl/bin:${PATH}")
    cmd = '{HCPPIPEDIR}/TaskfMRIAnalysis/RestfMRIAnalysis.sh ' + \
        '--path="{path}" ' + \
        '--subject="{subject}" ' + \
        '--lvl1tasks="{fmriname}" ' + \
        '--lvl1fsfs="{shortfmriname}" ' + \
        '--lvl2task="{level_2_task}" ' + \
        '--lvl2fsf="{level_2_fsf}" ' + \
        '--lowresmesh="{lowresmesh:d}" ' + \
        '--grayordinatesres="{fmrires:s}" ' + \
        '--origsmoothingFWHM="{fmrires:s}" ' + \
        '--confound="NONE" ' + \
        '--finalsmoothingFWHM="{smoothing:d}" ' + \
        '--temporalfilter="{temporal_filter}" ' + \
        '--vba="NO" ' + \
        '--regname="{regname}" ' + \
        '--parcellation="{parcel_name}" ' + \
        '--parcellationfile="{parcel_file}" ' + \
        '--seedROI="{seedROI}" '
    cmd = cmd.format(**args)
    run(cmd, cwd=args["path"])

parser = argparse.ArgumentParser(description='')
parser.add_argument('input_dir', help='The directory where the preprocessed derivative needed live')
parser.add_argument('output_dir', help='The directory where the output files '
                    'should be stored.')
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
parser.add_argument('--preprocessing_type', help='BIDS-apps preprocessing pipeline run on data. Choices include "HCP" and "fmriprep". ',
                    choices=['HCP','fmriprep'],
                    default='HCP',
                   nargs="+")
parser.add_argument('--use_ICA_outputs',help='Use ICA (whether FIX or AROMA) outputs in seed analysis. Choices include "Y/yes" or "N/no".',
choices=['Yes','yes','No','no'],default='Yes')
parser.add_argument('--stages', 
                    help='Which stages to run. Space separated list. ',
                   nargs="+", choices=['rsfMRISeedAnalysis', 'Generatefsf'],
                   default=['Generatefsf', 'rsfMRISeedAnalysis'])
parser.add_argument('--smoothing',
                    help="What FWHM smoothing (in mm) to apply to final output",
                    default=4, type=int)
parser.add_argument('--parcellation_file', help='The CIFTI label file to use or used to parcellate the brain. ')
parser.add_argument('--parcellation_name', help='Shorthand name of the CIFTI label file. ')
parser.add_argument('--seed_ROI_name', help='Space separated list of ROI name/s from CIFTI label file to be used as the seed ROI/s. The exact ROI from the label file must be known!', nargs="+")
parser.add_argument('--seed_handling', help='Of the ROI/s you have provided do you want to treat them as together (i.e. averaging ROIs together), or separate (run separate seed based analyses for each ROI)? '
                                        'Choices are "together", or "separate". Default argument is "separate".',
                                        choices=['together', 'separate'], 
                                        default='separate')
parser.add_argument('--combine_resting_scans', 
help='If multiple of the same resting state BIDS file type exist should they be combined prior seed analysis? Choices include "Y/yes" or "N/no".',
choices=['Yes','yes','No','no'],default='No')
parser.add_argument('--seed_analysis_output', 
                    help='The output of the seed based analysis. Choices are "dense" (i.e. dtseries.nii) and "parcellated" (i.e. ptseries.nii)).',
                    choices = ['dense','parcellated'], default = 'dense')
                        

args = parser.parse_args()

# global variables
highpass = "2000"
lowresmesh = 32
highresmesh = 164
smoothing = args.smoothing
output_dir = args.output_dir
parcel_file = args.parcellation_file
parcel_name = args.parcellation_name
seed_ROI_name = args.seed_ROI_name
seed_handling = args.seed_handling
seed_analysis_output = args.seed_analysis_output
msm_all_reg_name = "MSMAll_2_d40_WRN"

if args.participant_label:
    layout = BIDSLayout(os.path.join(args.input_dir,'sub-'+subject_label))
else:
    raise ValueError('An argument must be specified for participant label. Quitting.')

# if subject label has sessions underneath those need to be outputted into different directories
if args.session_label:
    ses_to_analyze = args.session_label
elif glob(os.path.join(args.bids_dir, "sub-" + subject_label, "ses-*")):
    ses_dirs = glob(os.path.join(args.bids_dir, "sub-" + subject_label, "ses-*"))
    ses_to_analyze = [ses_dir.split("-")[-1] for ses_dir in ses_dirs]
else:
    ses_to_analyze = ""
if ses_to_analyze:
    for ses_label in ses_to_analyze:
        # retrieve preprocessing BIDS layout for participant specified
        if args.preprocessing_type == 'HCP':
            try
            bolds = [f.filename for f in layout.get(subject=subject_label, session=ses_label,
                                                type='clean',
                                                extensions=["nii.gz"])]
        
        elif args.preprocessing_type == 'fmriprep':
            bolds = [f.filename for f in layout.get(subject=subject_label, session=ses_label,
                                                type='bold',
                                                extensions=["nii.gz"])]

        
        for fmritcs in bolds:
            fmriname = fmritcs.split("%s/func/" % ses_label)[-1].split(".")[0]
            assert fmriname
            zooms = nibabel.load(fmritcs).get_header().get_zooms()
            reptime = float("%.1f" % zooms[3])
            fmrires = str(int(min(zooms[:3])))
            
            if 'rest' in fmriname:
                shortfmriname = "_".join(fmriname.split("_")[2:4])
                if args.fsf_template_folder == None:
                    raise Exception("If Generatefsf or rsfMRISeedAnalysis is to be run --fsf_template_dir cannot be empty")
                else:
                    fsf_templates = glob(os.path.join(args.fsf_template_folder, '*'))
                if os.path.join(args.fsf_template_folder,shortfmriname) in fsf_templates:
                    if os.path.join(args.fsf_template_folder,shortfmriname,shortfmriname + "_hp"+highpass+"_s"+fmrires+"_level2.fsf") \
                            in glob(os.path.join(args.fsf_template_folder, shortfmriname, '*')):
                        level_2_task = shortfmriname + "_combined"
                        level_2_fsf = shortfmriname + "_hp"+highpass+"_s"+fmrires+"_level2.fsf"
                    else:
                        print("Second level fsf file for " + shortfmriname + " not provided. The naming must be " + shortfmriname + "_hp2000_s2_level2.fsf")
                        level_2_task = "NONE"
                        level_2_fsf = "NONE"
                        if os.path.join(args.fsf_template_folder,shortfmriname,shortfmriname + "_hp"+highpass+"_s"+fmrires+"_level1.fsf") in glob(os.path.join(args.fsf_template_folder, shortfmriname, '*')):
                            templatedir = os.path.join(args.fsf_template_folder,shortfmriname)
                            # find cifti file, with preference given to ptseries files
                            if os.path.isfile(os.path.join(output_dir,"sub-" + subject_label, "ses-" + ses_label, "MNINonLinear", "Results", fmriname, fmriname + "_Atlas_" + msm_all_reg_name + "_hp" + str(highpass) + "_clean_" + parcel_name + ".ptseries.nii")):
                                cifti_file = os.path.join(output_dir,"sub-" + subject_label, "ses-" + ses_label, "MNINonLinear", "Results", fmriname, fmriname + "_Atlas_" + msm_all_reg_name + "_hp" + str(highpass) + "_clean_" + parcel_name + ".ptseries.nii")
                            elif os.path.isfile(os.path.join(output_dir, "sub-" + subject_label, "ses-" + ses_label, "MNINonLinear", "Results", fmriname, "RestingStateStats", fmriname + "_Atlas_" + msm_all_reg_name + "_hp" + str(highpass) + "_clean_" + parcel_name + ".ptseries.nii")):
                                cifti_file = os.path.join(output_dir,"sub-" + subject_label, "ses-" + ses_label, "MNINonLinear", "Results", fmriname, "RestingStateStats", fmriname + "_Atlas_" + msm_all_reg_name + "_hp" + str(highpass) + "_clean_" + parcel_name + ".ptseries.nii")
                            elif os.path.isfile(os.path.join(output_dir,"sub-" + subject_label, "ses-" + ses_label, "MNINonLinear", "Results", fmriname, fmriname + "_Atlas_" + msm_all_reg_name + "_hp" + str(highpass) + "_clean.dtseries.nii")):
                                cifti_file = os.path.join(output_dir,"sub-" + subject_label, "ses-" + ses_label, "MNINonLinear", "Results", fmriname, fmriname + "_Atlas_" + msm_all_reg_name + "_hp" + str(highpass) + "_clean.dtseries.nii")
                            else:
                                raise Exception("cannot find cifti file, must exit")
                            if len(seed_ROI_name) > 1:
                                if seed_handling == "together":
                                    separator = "-"
                                    seed_ROI_merged_string = separator.join(seed_ROI_name)
                                    regressor_file = seed_ROI_merged_string + '-Regressor.txt'
                                    write_regressor(cifti_file, parcel_file, seed_ROI_name, regressor_file)
                                    if not regressor_file:
                                        raise Exception("variable 'regressor_file' does not exist. Something failed within rsfMRI_seed.py. Must exit")
                                    if seed_analysis_output == 'dense':
                                        parcel_file = "NONE"
                                        parcel_name = "NONE"    
                                    task_stages_dict = OrderedDict([("Generatefsf", partial(run_Generatefsf_processing,
                                                                                                path=output_dir + "/sub-%s" % (subject_label),
                                                                                                subject="ses-%s" % (ses_label),
                                                                                                fmriname=fmriname,
                                                                                                shortfmriname=shortfmriname,
                                                                                                highpass=highpass,
                                                                                                fmrires=fmrires,
                                                                                                templatedir=templatedir,
                                                                                                regressor_file=regressor_file)),
                                                                    ("rsfMRISeedAnalysis", partial(run_seed_FirstLevel_rsfMRI_processing,
                                                                                                    path=output_dir + "/sub-%s" % (subject_label),
                                                                                                    subject="ses-%s" % (ses_label),
                                                                                                    lowresmesh=lowresmesh,
                                                                                                    shortfmriname=shortfmriname,
                                                                                                    fmrires=fmrires,
                                                                                                    smoothing=smoothing,
                                                                                                    fmriname=fmriname,
                                                                                                    parcel_file=parcel_file,
                                                                                                    parcel_name=parcel_name,
                                                                                                    temporal_filter=highpass,
                                                                                                    regname=msm_all_reg_name,
                                                                                                    level_2_task=level_2_task,
                                                                                                    level_2_fsf=level_2_fsf,
                                                                                                    seedROI=seed_ROI_merged_string))])
                                    for stage, stage_func in task_stages_dict.iteritems():
                                        if stage in args.stages:
                                            stage_func()
                                else:
                                    for seed in seed_ROI_name:
                                        parcel_file = args.parcellation_file
                                        parcel_name = args.parcellation_name
                                        regressor_file = seed + '-Regressor.txt'
                                        write_regressor(cifti_file, parcel_file, seed, regressor_file)
                                        if not regressor_file:
                                            raise Exception("variable 'regressor_file' does not exist. Something failed within rsfMRI_seed.py. Must exit")
                                        if seed_analysis_output == 'dense':
                                            parcel_file = "NONE"
                                            parcel_name = "NONE"    
                                        task_stages_dict = OrderedDict([("Generatefsf", partial(run_Generatefsf_processing,
                                                                        path=output_dir + "/sub-%s" % (subject_label),
                                                                        subject="ses-%s" % (ses_label),
                                                                        fmriname=fmriname,
                                                                        shortfmriname=shortfmriname,
                                                                        highpass=highpass,
                                                                        fmrires=fmrires,
                                                                        templatedir=templatedir,
                                                                        regressor_file=regressor_file)),
                                                ("rsfMRISeedAnalysis", partial(run_seed_FirstLevel_rsfMRI_processing,
                                                                                path=output_dir + "/sub-%s" % (subject_label),
                                                                                subject="ses-%s" % (ses_label),
                                                                                lowresmesh=lowresmesh,
                                                                                shortfmriname=shortfmriname,                                                                                                      
                                                                                smoothing=smoothing,
                                                                                fmriname=fmriname,
                                                                                fmrires=fmrires,
                                                                                parcel_file=parcel_file,
                                                                                parcel_name=parcel_name,
                                                                                temporal_filter=highpass,
                                                                                regname=msm_all_reg_name,
                                                                                level_2_task=level_2_task,
                                                                                level_2_fsf=level_2_fsf,
                                                                                seedROI=seed))])
                                                
                                        for stage, stage_func in task_stages_dict.iteritems():
                                            if stage in args.stages:
                                                stage_func()
                            elif len(seed_ROI_name) == 1:
                                regressor_file = seed_ROI_name[0] + '-Regressor.txt'
                                write_regressor(cifti_file, parcel_file, seed_ROI_name, regressor_file)
                                if not regressor_file:
                                    raise Exception("variable 'regressor_file' does not exist. Something failed within rsfMRI_seed.py. Must exit")
                                if seed_analysis_output == 'dense':
                                    parcel_file = "NONE"
                                    parcel_name = "NONE"    
                                task_stages_dict = OrderedDict([("Generatefsf", partial(run_Generatefsf_processing,
                                                                        path=output_dir + "/sub-%s" % (subject_label),
                                                                        subject="ses-%s" % (ses_label),
                                                                        fmriname=fmriname,
                                                                        shortfmriname=shortfmriname,
                                                                        templatedir=templatedir,
                                                                        highpass=highpass,
                                                                        fmrires=fmrires,
                                                                        regressor_file=regressor_file)),
                                                ("rsfMRISeedAnalysis", partial(run_seed_FirstLevel_rsfMRI_processing,
                                                                                path=output_dir + "/sub-%s" % (subject_label),
                                                                                subject="ses-%s" % (ses_label),
                                                                                lowresmesh=lowresmesh,
                                                                                shortfmriname=shortfmriname,
                                                                                smoothing=smoothing,
                                                                                fmriname=fmriname,
                                                                                fmrires=fmrires,
                                                                                parcel_file=parcel_file,
                                                                                parcel_name=parcel_name,
                                                                                temporal_filter=highpass,
                                                                                regname=msm_all_reg_name,
                                                                                level_2_task=level_2_task,
                                                                                level_2_fsf=level_2_fsf,
                                                                                seedROI=seed_ROI_name[0]))])
                                for stage, stage_func in task_stages_dict.iteritems():
                                    if stage in args.stages:
                                        stage_func()
                        else:
                            print("First level fsf file for " + shortfmriname + " not provided. The naming must be " + shortfmriname + "_hp"+highpass+"_s"+fmrires+"_level1.fsf")
                else:
                    print(shortfmriname + " is not within the fsf_template_folder.")
else:
    bolds = [f.filename for f in layout.get(subject=subject_label,
                                            type='bold',
                                            extensions=["nii.gz", "nii"])]
    for fmritcs in bolds:
        fmriname = "_".join(fmritcs.split("sub-")[-1].split("_")[1:]).split(".")[0]
        assert fmriname
        zooms = nibabel.load(fmritcs).get_header().get_zooms()
        reptime = float("%.1f" % zooms[3])
        fmrires = str(float(min(zooms[:3])))
        if 'rest' in fmriname:
            shortfmriname = fmriname.split("_")[2].split("-")[1]
            if args.fsf_template_folder == None:
                raise Exception("If Generatefsf or rsfMRISeedAnalysis is to be run --fsf_template_dir cannot be empty")
            else:
                fsf_templates = glob(os.path.join(args.fsf_template_folder, '*'))
            if os.path.join(args.fsf_template_folder,shortfmriname) in fsf_templates:
                if os.path.join(args.fsf_template_folder,shortfmriname,shortfmriname + "_hp"+highpass+"_s"+fmrires+"_level2.fsf") \
                        in glob(os.path.join(args.fsf_template_folder, shortfmriname, '*')):
                    level_2_task = shortfmriname + "_combined"
                    level_2_fsf = shortfmriname + "_hp"+highpass+"_s"+fmrires+"_level2.fsf"
                else:
                    print("Second level fsf file for " + shortfmriname + " not provided. The naming must be " + shortfmriname + "_hp"+highpass+"_s"+fmrires+"_level2.fsf")
                    level_2_task = "NONE"
                    level_2_fsf = "NONE"
                    if os.path.join(args.fsf_template_folder,shortfmriname,shortfmriname + "_hp"+highpass+"_s"+fmrires+"_level1.fsf") in glob(os.path.join(args.fsf_template_folder, shortfmriname, '*')):
                        templatedir = os.path.join(args.fsf_template_folder,shortfmriname)
                        if os.path.isfile(os.path.join(output_dir,"sub-" + subject_label, "MNINonLinear", "Results", fmriname, fmriname + "_Atlas_" + msm_all_reg_name + "_hp" + str(highpass) + "_clean_" + parcel_name + ".ptseries.nii")):
                            cifti_file = os.path.join(output_dir,"sub-" + subject_label, "MNINonLinear", "Results", fmriname, fmriname + "_Atlas_" + msm_all_reg_name + "_hp" + str(highpass) + "_clean_" + parcel_name + ".ptseries.nii")
                        elif os.path.isfile(os.path.join(output_dir, "sub-" + subject_label, "MNINonLinear", "Results", fmriname, "RestingStateStats", fmriname + "_Atlas_" + msm_all_reg_name + "_hp" + str(highpass) + "_clean_" + parcel_name + ".ptseries.nii")):
                            cifti_file = os.path.join(output_dir,"sub-" + subject_label, "MNINonLinear", "Results", fmriname, "RestingStateStats", fmriname + "_Atlas_" + msm_all_reg_name + "_hp" + str(highpass) + "_clean_" + parcel_name + ".ptseries.nii")
                        elif os.path.isfile(os.path.join(output_dir,"sub-" + subject_label, "MNINonLinear", "Results", fmriname, fmriname + "_Atlas_" + msm_all_reg_name + "_hp" + str(highpass) + "_clean.dtseries.nii")):
                            cifti_file = os.path.join(output_dir,"sub-" + subject_label, "MNINonLinear", "Results", fmriname, fmriname + "_Atlas_" + msm_all_reg_name + "_hp" + str(highpass) + "_clean.dtseries.nii")
                        else:
                            raise Exception("cannot find cifti file, must exit")
                        if len(seed_ROI_name) > 1:
                            if seed_handling == "together":
                                separator = "-"
                                seed_ROI_merged_string = separator.join(seed_ROI_name)
                                regressor_file = seed_ROI_merged_string + '-Regressor.txt'
                                write_regressor(cifti_file, parcel_file, seed_ROI_name, regressor_file)
                                if not regressor_file:
                                    raise Exception("variable 'regressor_file' does not exist. Something failed within rsfMRI_seed.py. Must exit")
                                if seed_analysis_output == 'dense':
                                    parcel_file = "NONE"
                                    parcel_name = "NONE"
                                task_stages_dict = OrderedDict([("Generatefsf", partial(run_Generatefsf_processing,
                                                                    path=output_dir,
                                                                    subject="sub-%s" % (subject_label),
                                                                    fmriname=fmriname,
                                                                    highpass=highpass,
                                                                    fmrires=fmrires,
                                                                    shortfmriname=shortfmriname,
                                                                    templatedir=templatedir)),
                                            ("rsfMRISeedAnalysis", partial(run_seed_FirstLevel_rsfMRI_processing,
                                                                            path=output_dir,
                                                                            subject="sub-%s" % (subject_label),
                                                                            lowresmesh=lowresmesh,
                                                                            shortfmriname=shortfmriname,
                                                                            fmrires=fmrires,
                                                                            fmriname=fmriname,
                                                                            parcellation_file=parcel_file,
                                                                            parcellation=parcel_name,
                                                                            temporal_filter=highpass,
                                                                            regname=msm_all_reg_name,
                                                                            level_2_task=level_2_task,
                                                                            level_2_fsf=level_2_fsf))])

                                for stage, stage_func in task_stages_dict.iteritems():
                                        if stage in args.stages:
                                            stage_func()
                            else:
                                for seed in seed_ROI_name:
                                    regressor_file = seed + '-Regressor.txt'
                                    write_regressor(cifti_file, parcel_file, seed, regressor_file)
                                    if not regressor_file:
                                        raise Exception("variable 'regressor_file' does not exist. Something failed within rsfMRI_seed.py. Must exit")
                                    if seed_analysis_output == 'dense':
                                        parcel_file = "NONE"
                                        parcel_name = "NONE"    
                                    task_stages_dict = OrderedDict([("Generatefsf", partial(run_Generatefsf_processing,
                                                                    path=output_dir,
                                                                    subject="sub-%s" % (subject_label),
                                                                    fmriname=fmriname,
                                                                    shortfmriname=shortfmriname,
                                                                    highpass=highpass,
                                                                    fmrires=fmrires,
                                                                    templatedir=templatedir,
                                                                    regressor_file=regressor_file)),
                                            ("rsfMRISeedAnalysis", partial(run_seed_FirstLevel_rsfMRI_processing,
                                                                            path=output_dir,
                                                                            subject="sub-%s" % (subject_label),
                                                                            lowresmesh=lowresmesh,
                                                                            shortfmriname=shortfmriname,                                                                                                      
                                                                            smoothing=smoothing,
                                                                            fmriname=fmriname,
                                                                            fmrires=fmrires,
                                                                            parcel_file=parcel_file,
                                                                            parcel_name=parcel_name,
                                                                            temporal_filter=highpass,
                                                                            regname=msm_all_reg_name,
                                                                            level_2_task=level_2_task,
                                                                            level_2_fsf=level_2_fsf,
                                                                            seedROI=seed))])
                                    for stage, stage_func in task_stages_dict.iteritems():
                                        if stage in args.stages:
                                            stage_func()
                        elif len(seed_ROI_name) == 1:
                            regressor_file = seed_ROI_name[0] + '-Regressor.txt'
                            write_regressor(cifti_file, parcel_file, seed_ROI_name, regressor_file)
                            if not regressor_file:
                                raise Exception("variable 'regressor_file' does not exist. Something failed within rsfMRI_seed.py. Must exit")
                            if seed_analysis_output == 'dense':
                                parcel_file = "NONE"
                                parcel_name = "NONE"    
                            task_stages_dict = OrderedDict([("Generatefsf", partial(run_Generatefsf_processing,
                                                                    path=output_dir,
                                                                    subject="sub-%s" % (subject_label),
                                                                    fmriname=fmriname,
                                                                    shortfmriname=shortfmriname,
                                                                    templatedir=templatedir,
                                                                    highpass=highpass,
                                                                    fmrires=fmrires,
                                                                    regressor_file=regressor_file)),
                                            ("rsfMRISeedAnalysis", partial(run_seed_FirstLevel_rsfMRI_processing,
                                                                            path=output_dir,
                                                                            subject="sub-%s" % (subject_label),
                                                                            lowresmesh=lowresmesh,
                                                                            shortfmriname=shortfmriname,
                                                                            smoothing=smoothing,
                                                                            fmriname=fmriname,
                                                                            fmrires=fmrires,
                                                                            parcel_file=parcel_file,
                                                                            parcel_name=parcel_name,
                                                                            temporal_filter=highpass,
                                                                            regname=msm_all_reg_name,
                                                                            level_2_task=level_2_task,
                                                                            level_2_fsf=level_2_fsf,
                                                                            seedROI=seed_ROI_name[0]))])
                            for stage, stage_func in task_stages_dict.iteritems():
                                if stage in args.stages:
                                    stage_func()
                    else:
                        print("First level fsf file for " + shortfmriname + " not provided. The naming must be " + shortfmriname + "_hp"+highpass+"_s"+fmrires+"_level1.fsf")
            else:
                print(shortfmriname + " is not within the fsf_template_folder.")

            if args.fsf_template_folder == None:
                raise Exception(
                    "If Generatefsf or rsfMRISeedAnalysis is to be run --fsf_template_dir cannot be empty")
            else:
                fsf_templates = glob(os.path.join(args.fsf_template_folder, '*'))
            if os.path.join(args.fsf_template_folder, shortfmriname) in fsf_templates:
                for stage, stage_func in task_stages_dict.iteritems():
                    if stage in args.stages:
                        stage_func()