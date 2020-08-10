Usage Notes
===========

Command-Line Arguments
----------------------
.. code-block:: python

  [-h] --input_dir INPUT_DIR --output_dir OUTPUT_DIR --group
              {participant,batch}
              [--participant_label PARTICIPANT_LABEL [PARTICIPANT_LABEL ...]]
              [--session_label SESSION_LABEL [SESSION_LABEL ...]]
              [--preprocessing_type {HCP,fmriprep}]
              [--use_ICA_outputs {Yes,yes,No,no}]
              [--combine_resting_scans {Yes,yes,No,no}]
              [--smoothing SMOOTHING] --parcellation_file PARCELLATION_FILE
              --parcellation_name PARCELLATION_NAME --seed_ROI_name
              SEED_ROI_NAME [SEED_ROI_NAME ...]
              [--seed_handling {together,separate}]
              [--seed_analysis_output {dense,parcellated}]
              [--motion_confounds {NONE,Movement_Regressors,Movement_Regressors_dt,Movement_RelativeRMS,Movement_RelativeRMS_mean,Movement_AbsoluteRMS,Movement_AbsoluteRMS_mean,dvars,fd}]
              [--reg_name {NONE,MSMAll_2_d40_WRN}]
              [--text_output_format {CSV,csv,none,NONE}] [--num_cpus NUM_CPUS]
              [--statistic {correlation,regression}]

Required Arguments
------------------
--input_dir INPUT_DIR
                The directory where the preprocessed derivative needed
                live
--output_dir OUTPUT_DIR
                The directory where the output files should be stored.
--group GROUP
                Whether to run this participant by participant or the
                entire group. Choices are "participant" or "batch". If
                participant by participant "--participant_label" and "
                --session_label" must be specified
--parcellation_file PARCELLATION_FILE
                The CIFTI label/atlas file to use or used to
                parcellate the brain.
--parcellation_name PARCELLATION_NAME
                Shorthand name of the CIFTI label file.
--seed_ROI_name SEED_ROI_NAME
                Space separated list of ROI name/s from CIFTI label
                file to be used as the seed ROI/s. The exact ROI from
                the label file must be known!

Optional Arguments
------------------
-h, --help            show this help message and exit
--participant_label PARTICIPANT_LABEL
                The label of the participant that should be analyzed.
                The label corresponds to sub-<participant_label> from
                the BIDS spec (so it does not include "sub-"). If this
                parameter is not provided all subjects should be
                analyzed. Multiple participants can be specified with
                a space separated list.
--session_label SESSION_LABEL
                The label of the session that should be analyzed. The
                label corresponds to ses-<session_label> from the BIDS
                spec (so it does not include "ses-"). If this
                parameter is not provided all sessions within a
                subject should be analyzed.
--preprocessing_type PREPROCESSING_TYPE
                BIDS-apps preprocessing pipeline run on data. Choices
                include "HCP" and "fmriprep". Default: "HCP".
--use_ICA_outputs USE_ICA_OUTPUTS
                Use ICA (whether FIX or AROMA) outputs in seed
                analysis. Choices include "Y/yes" or "N/no". Default:
                "Yes".
--combine_resting_scans COMBINE_RESTING_SCANS
                If multiple of the same resting state BIDS file type
                exist should they be combined prior seed analysis?
                Choices include "Y/yes" or "N/no". Default "No".
--smoothing SMOOTHING
                What FWHM smoothing (in mm) to apply to final output,
                only applies to SBA with dtseries. Default: 4
--seed_handling SEED_HANDLING
                Of the ROI/s you have provided do you want to treat
                them as together (i.e. averaging ROIs together), or
                separate (run separate seed based analyses for each
                ROI)? Choices are "together", or "separate". Default:
                "separate".
--seed_analysis_output SEED_ANALYSIS_OUTPUT
                The output of the seed based analysis. Choices are
                "dense" (i.e. dtseries.nii) and "parcellated" (i.e.
                ptseries.nii)). Default: "parcellated".
--motion_confounds MOTION_CONFOUNDS
                What type of motion confounds to use, if any. Note
                only works in combination with "--statistic
                regression". Choices are "Movement_Regressors" (motion
                rotation angles and translations in mm),
                "Movement_Regressors_dt" (detrended motion rotation
                angles and translations in mm),
                "Movement_Regressors_demean" (demeaned motion rotation
                angles and translations in mm) "Movement_RelativeRMS"
                (RMS intensity difference of volume N to the reference
                volume), "Movement_RelativeRMS_mean" (square of RMS
                intensity difference of volume N to the reference
                volume), "Movement_AbsoluteRMS" (absolute RMS
                intensity difference of volume N to the reference
                volume, "Movement_AbsoluteRMS_mean" (square of
                absolute RMS intensity difference of volume N to the
                reference volume), "dvars" ( RMS intensity difference
                of volume N to volume N+1 (see Power et al,
                NeuroImage, 59(3), 2012)), "fd" ( frame displacement
                (average of rotation and translation parameter
                differences - using weighted scaling, as in Power et
                al.))
--reg_name REG_NAME
                What type of registration do you want to use? Choices
                are "MSMAll_2_d40_WRN" and "NONE". Default:
                "MSMAll_2_d40_WRN".
--text_output_format TEXT_OUTPUT_FORMAT
                What format should the text output be in? Choices are
                "CSV" or "NONE". Default: "CSV".
--num_cpus NUM_CPUS   How many concurrent CPUs to use. Default: "1".
--statistic STATISTIC
                Strategy to calculate functional connectivity. Choices
                are "correlation", and "regression" Default:
                "correlation"
