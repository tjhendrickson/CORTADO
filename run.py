#!/usr/bin/python
from __future__ import print_function
import argparse
import os
import shutil
import nibabel
from glob import glob
from subprocess import Popen, PIPE
import subprocess
from bids.grabbids import BIDSLayout
from functools import partial
from collections import OrderedDict


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
        '--taskname="{fmriname}" ' + \
        '--shorttaskname="{shortfmriname}" ' + \
        '--templatedir="{templatedir}" ' + \
        '--outdir="{path}/{subject}/MNINonLinear/Results/{fmriname}" '
    cmd = cmd.format(**args)
    run(cmd, cwd=args["path"], env={"OMP_NUM_THREADS": str(args["n_cpus"])})


def run_seed_correlation_rsfMRI_processing(**args):
    args.update(os.environ)
    


def run_seed_FirstLevel_rsfMRI_processing(**args):
    args.update(os.environ)
    cmd = '{HCPPIPEDIR}/TaskfMRIAnalysis/RestfMRIAnalysis.sh ' + \
        '--path="{path}" ' + \
        '--subject="{subject}" ' + \
        '--lvl1tasks="{fmriname}" ' + \
        '--lvl1fsfs="{shortfmriname}_hp200_s4_level1.fsf" ' + \
        '--lvl2task="{level_2_task}" ' + \
        '--lvl2fsf="{level_2_fsf}" ' + \
        '--lowresmesh="{lowresmesh:d}" ' + \
        '--grayordinatesres="{grayordinatesres:s}" ' + \
        '--origsmoothingFWHM="{fmrires:s}" ' + \
        '--confound="NONE" ' + \
        '--finalsmoothingFWHM="{fmrires:s}" ' + \
        '--temporalfilter="{temporal_filter}" ' + \
        '--vba="NO" ' + \
        '--regname="{regname}" ' + \
        '--parcellation="{parcellation}" ' + \
        '--parcellationfile="{parcellation_file}" ' + \
        '--seedROI="{seedROI}" '
    cmd = cmd.format(**args)
    run(cmd, cwd=args["path"], env={"OMP_NUM_THREADS": str(args["n_cpus"])})


parser = argparse.ArgumentParser(description='')
parser.add_argument('bids_dir', help='The directory with the input dataset '
                    'formatted according to the BIDS standard.')
parser.add_argument('output_dir', help='The directory where the output files '
                    'should be stored. If you are running group level analysis '
                    'this folder should be prepopulated with the results of the'
                    'participant level analysis.')
parser.add_argument('analysis_level', help='Level of the analysis that will be performed. '
                    'Multiple participant level analyses can be run independently '
                    '(in parallel) using the same output_dir.',
                    choices=['participant'])
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
parser.add_argument('--fsf_template_folder', help='Space separated folders to be used to perform 1st level Task fMRI Analysis.'
                                                 'The folder must have the following naming scheme: "task name" with "task_name" being the immediate text following "task-" and prior to the '
                                                 'following "_". ')
parser.add_argument('--stages', help='Which stages to run. Space separated list. ',
                   nargs="+", choices=['rsfMRISeedAnalysis', 'Generatefsf'],
                   default=['rsfMRISeedAnalysis', 'Generatefsf'])
parser.add_argument('--coreg', help='Coregistration method to use ',
                    choices=['MSMSulc', 'FS'], default='MSMSulc')
parser.add_argument('--parcellation_file', help='The CIFTI label file to use or used to parcellate the brain. ')
parser.add_argument('--parcellation_name', help='Shorthand name of the CIFTI label file. ')
parser.add_argument('--seedROI', help='ROI name from CIFTI label file to be used as the seed ROI. The exact ROI from the label file must be known! ')


args = parser.parse_args()
grayordinatesres = "2" # This is currently the only option for which there is an atlas
lowresmesh = 32
highresmesh = 164

dlabel_file = args.parcellation_file
parcellation = args.parcllation_name
regname = args.coreg
msm_all_reg_name = "MSMAll_2_d40_WRN"

# remove this for now
# run("bids-validator " + args.bids_dir)

layout = BIDSLayout(args.bids_dir)
subjects_to_analyze = []
# only for a subset of subjects
if args.participant_label:
    subjects_to_analyze = args.participant_label
# for all subjects
else:
    subject_dirs = glob(os.path.join(args.bids_dir, "sub-*"))
    subjects_to_analyze = [subject_dir.split("-")[-1] for subject_dir in subject_dirs]

# running participant level
if args.analysis_level == "participant":
    for subject_label in subjects_to_analyze:
        
        # if subject label has sessions underneath those need to be outputted into different directories
        if glob(os.path.join(args.bids_dir, "sub-" + subject_label, "ses-*")):
            ses_dirs = glob(os.path.join(args.bids_dir, "sub-" + subject_label, "ses-*"))
            ses_to_analyze = [ses_dir.split("-")[-1] for ses_dir in ses_dirs]
            for ses_label in ses_to_analyze:
                bolds = [f.filename for f in layout.get(subject=subject_label, session=ses_label,
                                                        type='bold',
                                                        extensions=["nii.gz", "nii"])]
                fMRIVolume_fMRIs = []
                fmrinames_fMRIs = []
                for fmritcs in bolds:
                    fmriname = fmritcs.split("%s/func/" % ses_label)[-1].split(".")[0]
                    assert fmriname
                    zooms = nibabel.load(fmritcs).get_header().get_zooms()
                    reptime = float("%.1f" % zooms[3])
                    fmrires = float(min(zooms[:3]))
                    fmrires = "2"
                    if 'rest' in fmriname:
                        shortfmriname = fmriname.split("_")[2].split("-")[1]
                        if args.fsf_template_folder == None:
                            raise Exception("If Generatefsf or rsfMRISeedAnalysis is to be run --fsf_template_dir cannot be empty")
                        else:
                            fsf_templates = glob(os.path.join(args.fsf_template_folder, '*'))
                        if os.path.join(args.fsf_template_folder,shortfmriname) in fsf_templates:
                            if os.path.join(args.fsf_template_folder,shortfmriname,shortfmriname + "_hp200_s4_level2.fsf") \
                                    in glob(os.path.join(args.fsf_template_folder, shortfmriname, '*')):
                                level_2_task = shortfmriname + "_combined"
                                level_2_fsf = shortfmriname + "_hp200_s4_level2.fsf"
                            else:
                                print("Second level fsf file for " + shortfmriname + " not provided. The naming must be " + shortfmriname + "_hp200_s4_level2.fsf")
                                level_2_task = "NONE"
                                level_2_fsf = "NONE"
                                if os.path.join(args.fsf_template_folder,shortfmriname,shortfmriname + "_hp200_s4_level1.fsf") \
                                        in glob(os.path.join(args.fsf_template_folder, shortfmriname, '*')):
                                     highpass=2000
                                     templatedir = os.path.join(args.fsf_template_folder,shortfmriname)
                                     task_stages_dict = OrderedDict([("Generatefsf", partial(run_Generatefsf_processing,
                                                                                path=args.output_dir + "/sub-%s" % (subject_label),
                                                                                n_cpus=args.n_cpus,
                                                                                subject="ses-%s" % (ses_label),
                                                                                fmriname=fmriname,
                                                                                shortfmriname=shortfmriname,
                                                                                templatedir=templatedir)),
                                                        ("rsfMRISeedAnalysis", partial(run_seed_FirstLevel_rsfMRI_processing,
                                                                                     path=args.output_dir + "/sub-%s" % (subject_label),
                                                                                     n_cpus=args.n_cpus,
                                                                                     subject="ses-%s" % (ses_label),
                                                                                     lowresmesh=lowresmesh,
                                                                                     shortfmriname=shortfmriname,
                                                                                     fmrires=fmrires,
                                                                                     fmriname=fmriname,
                                                                                     grayordinatesres=grayordinatesres,
                                                                                     parcellation_file=dlabel_file,
                                                                                     parcellation=parcellation,
                                                                                     temporal_filter=highpass,
                                                                                     regname=regname,
                                                                                     level_2_task=level_2_task,
                                                                                     level_2_fsf=level_2_fsf))])
                                else:
                                    print("First level fsf file for " + shortfmriname + " not provided. The naming must be " + shortfmriname + "_hp200_s4_level1.fsf")
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
        else:
            bolds = [f.filename for f in layout.get(subject=subject_label,
                                                    type='bold',
                                                    extensions=["nii.gz", "nii"])]
            for fmritcs in bolds:
                fmriname = "_".join(fmritcs.split("sub-")[-1].split("_")[1:]).split(".")[0]
                assert fmriname                
                zooms = nibabel.load(fmritcs).get_header().get_zooms()
                reptime = float("%.1f" % zooms[3])
                fmrires = float(min(zooms[:3]))
                fmrires = "2"
                if 'rest' in fmriname:
                    highpass=2000                    
                    shortfmriname = fmriname.split("_")[2].split("-")[1]
                    if args.fsf_template_folder == None:
                        raise Exception("If Generatefsf or rsfMRISeedAnalysis is to be run --fsf_template_dir cannot be empty")
                    else:
                        fsf_templates = glob(os.path.join(args.fsf_template_folder, '*'))
                    if os.path.join(args.fsf_template_folder,shortfmriname) in fsf_templates:
                        if os.path.join(args.fsf_template_folder,shortfmriname,shortfmriname + "_hp200_s4_level2.fsf") \
                                in glob(os.path.join(args.fsf_template_folder, shortfmriname, '*')):
                            level_2_task = shortfmriname + "_combined"
                            level_2_fsf = shortfmriname + "_hp200_s4_level2.fsf"
                        else:
                            print("Second level fsf file for " + shortfmriname + " not provided. The naming must be " + shortfmriname + "_hp200_s4_level2.fsf")
                            level_2_task = "NONE"
                            level_2_fsf = "NONE"
                            if os.path.join(args.fsf_template_folder,shortfmriname,shortfmriname + "_hp200_s4_level1.fsf") \
                                    in glob(os.path.join(args.fsf_template_folder, shortfmriname, '*')):
                                highpass=2000
                                templatedir = os.path.join(args.fsf_template_folder,shortfmriname)
                                task_stages_dict = OrderedDict([("Generatefsf", partial(run_Generatefsf_processing,
                                                                            path=args.output_dir,
                                                                            n_cpus=args.n_cpus,
                                                                            subject="sub-%s" % (subject_label),
                                                                            fmriname=fmriname,
                                                                            shortfmriname=shortfmriname,
                                                                            templatedir=templatedir)),
                                                    ("rsfMRISeedAnalysis", partial(run_seed_FirstLevel_rsfMRI_processing,
                                                                                    path=args.output_dir,
                                                                                    n_cpus=args.n_cpus,
                                                                                    subject="sub-%s" % (subject_label),
                                                                                    lowresmesh=lowresmesh,
                                                                                    shortfmriname=shortfmriname,
                                                                                    fmrires=fmrires,
                                                                                    fmriname=fmriname,
                                                                                    grayordinatesres=grayordinatesres,
                                                                                    parcellation_file=dlabel_file,
                                                                                    parcellation=parcellation,
                                                                                    temporal_filter=highpass,
                                                                                    regname=regname,
                                                                                    level_2_task=level_2_task,
                                                                                    level_2_fsf=level_2_fsf))])
                            else:
                                print("First level fsf file for " + shortfmriname + " not provided. The naming must be " + shortfmriname + "_hp200_s4_level1.fsf")
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