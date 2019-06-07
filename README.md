# CORTADO

## CORTADO 
This postprocessing pipeline is developed by the [University of Minnesota Informatics Institute](https://research.umn.edu/units/umii) for use by University of Minnesota neuroimaging researchers, and for open-source software distribution. CORTADO stands for Cifti based O Resting state seed  T Analysis D O, ultimately I just really enjoy coffee :).CORTADO facilitates seed-based analysis with BIDS compatiable CIFTI rsfMRI derivates from the [Human Connectome Project pipeline](https://github.com/Washington-University/Pipelines) by creating a robust and easy to use Singularity container, as will be described here. This software is intended to follow a "Glass Box" philosophy in that while this software is automated through the usage of containerization one can review this github repository to visually inspect the source code and methods used. 

### Container Hosting
The containerization of this application is maintained and hosted on Singularity Hub [![https://www.singularity-hub.org/static/img/hosted-singularity--hub-%23e32020.svg](https://www.singularity-hub.org/static/img/hosting-singularity--hub-%23e32929.svg)](https://singularity-hub.org/collections/3125). Pull the most recent container by typing the command below into a linux terminal, (**NOTE: you do not have to do this every time before executing the container!**)

```
singularity pull shub://tjhendrickson/CORTADO
```
Once this command completes there should be a file named tjhendrickson-CORTADO-master-latest.simg within your current working directory. In the same terminal as above type:
```
ls tjhendrickson-CORTADO-master-latest.simg
```
If file is returned you have successfully pulled the container and are ready to use it!

### Singularity Usage
 
 To discover usage for this container you can look on this repository but you can execute the container by typing in the terminal:
 ```
 singularity run tjhendrickson-CORTADO-master-latest.simg -h
 ```
 Which should return the following:
 ```
 usage: run.py [-h]
              [--participant_label PARTICIPANT_LABEL [PARTICIPANT_LABEL ...]]
              [--session_label SESSION_LABEL [SESSION_LABEL ...]]
              [--fsf_template_folder FSF_TEMPLATE_FOLDER]
              [--stages {rsfMRISeedAnalysis,Generatefsf} [{rsfMRISeedAnalysis,Generatefsf} ...]]
              [--smoothing SMOOTHING] [--parcellation_file PARCELLATION_FILE]
              [--parcellation_name PARCELLATION_NAME]
              [--seed_ROI_name SEED_ROI_NAME [SEED_ROI_NAME ...]]
              [--seed_handling {together,separate}]
              [--seed_analysis_output {dense,parcellated}]
              bids_dir output_dir

positional arguments:
  bids_dir              The directory with the input dataset formatted
                        according to the BIDS standard.
  output_dir            The directory where the output files should be stored.
                        If you are running group level analysis this folder
                        should be prepopulated with the results of
                        theparticipant level analysis.

optional arguments:
  -h, --help            show this help message and exit
  --participant_label PARTICIPANT_LABEL [PARTICIPANT_LABEL ...]
                        The label of the participant that should be analyzed.
                        The label corresponds to sub-<participant_label> from
                        the BIDS spec (so it does not include "sub-"). If this
                        parameter is not provided all subjects should be
                        analyzed. Multiple participants can be specified with
                        a space separated list.
  --session_label SESSION_LABEL [SESSION_LABEL ...]
                        The label of the session that should be analyzed. The
                        label corresponds to ses-<session_label> from the BIDS
                        spec (so it does not include "ses-"). If this
                        parameter is not provided all sessions within a
                        subject should be analyzed.
  --fsf_template_folder FSF_TEMPLATE_FOLDER
                        Space separated folders to be used to perform 1st
                        level Task fMRI Analysis.The folder must have the
                        following naming scheme: "task name" with "task_name"
                        being the immediate text following "task-" and prior
                        to the following "_".
  --stages {rsfMRISeedAnalysis,Generatefsf} [{rsfMRISeedAnalysis,Generatefsf} ...]
                        Which stages to run. Space separated list.
  --smoothing SMOOTHING
                        What FWHM smoothing (in mm) to apply to final output
  --parcellation_file PARCELLATION_FILE
                        The CIFTI label file to use or used to parcellate the
                        brain.
  --parcellation_name PARCELLATION_NAME
                        Shorthand name of the CIFTI label file.
  --seed_ROI_name SEED_ROI_NAME [SEED_ROI_NAME ...]
                        Space separated list of ROI name/s from CIFTI label
                        file to be used as the seed ROI/s. The exact ROI from
                        the label file must be known!
  --seed_handling {together,separate}
                        Of the ROI/s you have provided do you want to treat
                        them as together (i.e. averaging ROIs together), or
                        separate (run separate seed based analyses for each
                        ROI)? Choices are "together", or "separate". Default
                        argument is "separate".
  --seed_analysis_output {dense,parcellated}
                        The output of the seed based analysis. Choices are
                        "dense" (i.e. dtseries.nii) and "parcellated" (i.e.
                        ptseries.nii)).
```
