# CORTADO

## Description 
This postprocessing pipeline is developed by the [University of Minnesota Informatics Institute](https://research.umn.edu/units/umii) for use by University of Minnesota neuroimaging researchers, and for open-source software distribution. CORTADO facilitates seed-based analysis with BIDS compatible CIFTI rsfMRI derivates from the [Human Connectome Project pipeline](https://github.com/Washington-University/Pipelines) by creating a robust and easy to use Singularity container, as will be described here. This software is intended to follow a "Glass Box" philosophy in that while this software is automated through the usage of containerization one can review this github repository to visually inspect the source code and methods used. 

### Container Hosting
The containerization of this application is maintained and hosted on Singularity Hub [![https://www.singularity-hub.org/static/img/hosted-singularity--hub-%23e32929.svg](https://www.singularity-hub.org/static/img/hosted-singularity--hub-%23e32929.svg)](https://singularity-hub.org/collections/3125). Pull the most recent container by typing the command below into a linux terminal, (**NOTE: you do not have to do this every time before executing the container!**)

```
singularity pull shub://tjhendrickson/CORTADO
```

### Singularity Usage
 
 To discover usage for this container you can look on this repository but you can execute the container by typing in the terminal:
 ```
 singularity run tjhendrickson-CORTADO-master-latest.simg -h
 ```
 Which should return the following:
```
usage: CORTADO [-h] --input_dir INPUT_DIR --output_dir OUTPUT_DIR --group {participant,batch}
              [--participant_label PARTICIPANT_LABEL [PARTICIPANT_LABEL ...]]
              [--session_label SESSION_LABEL [SESSION_LABEL ...]] [--preprocessing_type {HCP,fmriprep}]
              [--use_ICA_outputs {Yes,yes,No,no}] [--combine_resting_scans {Yes,yes,No,no}]
              [--smoothing SMOOTHING] --parcellation_file PARCELLATION_FILE --parcellation_name
              PARCELLATION_NAME --seed_ROI_name SEED_ROI_NAME [SEED_ROI_NAME ...]
              [--seed_handling {together,separate}] [--seed_analysis_output {dense,parcellated}]
              [--motion_confounds {NONE,Movement_Regressors,Movement_Regressors_dt,Movement_RelativeRMS,Movement_RelativeRMS_mean,Movement_AbsoluteRMS,Movement_AbsoluteRMS_mean,dvars,fd}]
              [--reg_name {NONE,MSMAll_2_d40_WRN}] [--text_output_format {CSV,csv,none,NONE}]
              [--num_cpus NUM_CPUS]
              [--statistic {correlation,partial_correlation,regression,tangent,covariance,sparse_inverse_covariance,precision,sparse_inverse_precision}]

optional arguments:
  -h, --help            show this help message and exit
  --input_dir INPUT_DIR
                        The directory where the preprocessed derivative needed live
  --output_dir OUTPUT_DIR
                        The directory where the output files should be stored.
  --group {participant,batch}
                        Whether to run this participant by participant or the entire group. Choices are
                        "participant" or "batch". If participant by participant "--participant_label" and
                        "--session_label" must be specified
  --participant_label PARTICIPANT_LABEL [PARTICIPANT_LABEL ...]
                        The label of the participant that should be analyzed. The label corresponds to
                        sub-<participant_label> from the BIDS spec (so it does not include "sub-"). If
                        this parameter is not provided all subjects should be analyzed. Multiple
                        participants can be specified with a space separated list.
  --session_label SESSION_LABEL [SESSION_LABEL ...]
                        The label of the session that should be analyzed. The label corresponds to
                        ses-<session_label> from the BIDS spec (so it does not include "ses-"). If this
                        parameter is not provided all sessions within a subject should be analyzed.
  --preprocessing_type {HCP,fmriprep}
                        BIDS-apps preprocessing pipeline run on data. Choices include "HCP" and
                        "fmriprep".
  --use_ICA_outputs {Yes,yes,No,no}
                        Use ICA (whether FIX or AROMA) outputs in seed analysis. Choices include "Y/yes"
                        or "N/no".
  --combine_resting_scans {Yes,yes,No,no}
                        If multiple of the same resting state BIDS file type exist should they be combined
                        prior seed analysis? Choices include "Y/yes" or "N/no".
  --smoothing SMOOTHING
                        What FWHM smoothing (in mm) to apply to final output
  --parcellation_file PARCELLATION_FILE
                        The CIFTI label/atlas file to use or used to parcellate the brain.
  --parcellation_name PARCELLATION_NAME
                        Shorthand name of the CIFTI label file.
  --seed_ROI_name SEED_ROI_NAME [SEED_ROI_NAME ...]
                        Space separated list of ROI name/s from CIFTI label file to be used as the seed
                        ROI/s. The exact ROI from the label file must be known!
  --seed_handling {together,separate}
                        Of the ROI/s you have provided do you want to treat them as together (i.e.
                        averaging ROIs together), or separate (run separate seed based analyses for each
                        ROI)? Choices are "together", or "separate". Default argument is "separate".
  --seed_analysis_output {dense,parcellated}
                        The output of the seed based analysis. Choices are "dense" (i.e. dtseries.nii) and
                        "parcellated" (i.e. ptseries.nii)).
  --motion_confounds {NONE,Movement_Regressors,Movement_Regressors_dt,Movement_RelativeRMS,Movement_RelativeRMS_mean,Movement_AbsoluteRMS,Movement_AbsoluteRMS_mean,dvars,fd}
                        What type of motion confounds to use, if any. Note only works in combination with
                        "--statistic regression". Choices are "Movement_Regressors" (motion rotation
                        angles and translations in mm), "Movement_Regressors_dt" (detrended motion
                        rotation angles and translations in mm), "Movement_Regressors_demean" (demeaned
                        motion rotation angles and translations in mm) "Movement_RelativeRMS" (RMS
                        intensity difference of volume N to the reference volume),
                        "Movement_RelativeRMS_mean" (square of RMS intensity difference of volume N to the
                        reference volume), "Movement_AbsoluteRMS" (absolute RMS intensity difference of
                        volume N to the reference volume, "Movement_AbsoluteRMS_mean" (square of absolute
                        RMS intensity difference of volume N to the reference volume), "dvars" ( RMS
                        intensity difference of volume N to volume N+1 (see Power et al, NeuroImage,
                        59(3), 2012)), "fd" ( frame displacement (average of rotation and translation
                        parameter differences - using weighted scaling, as in Power et al.))
  --reg_name {NONE,MSMAll_2_d40_WRN}
                        What type of registration do you want to use? Choices are "MSMAll_2_d40_WRN" and
                        "NONE"
  --text_output_format {CSV,csv,none,NONE}
                        What format should the text output be in? Choices are "CSV" or "NONE"
  --num_cpus NUM_CPUS   How many concurrent CPUs to use
  --statistic {correlation,partial_correlation,regression,tangent,covariance,sparse_inverse_covariance,precision,sparse_inverse_precision}
                        Strategy to calculate functional connectivity. Choices are "correlation", and
                        "regression"
```
