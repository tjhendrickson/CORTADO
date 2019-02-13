#!/bin/bash

set -x
#
# Author(s): Timothy B. Brown (tbbrown at wustl dot edu)
#

#
# Function description
#  Show usage information for this script
#
usage() {
    local scriptName=$(basename ${0})
    echo ""
    echo " Usage ${scriptName} --studyfolder=<study-folder> --subject=<subject-id> --taskname=<task-name> \\"
    echo "                     --templatedir=<template-dir> --outdir=<out-dir>"
    echo ""
    echo "   <study-folder> - folder in which study data resides in sub-folders named by subject ID"
    echo "   <subject-id>   - subject ID"
    echo "   <task-name>    - name of task for which to produce level 1 FSF file"
    echo "                    (e.g. tfMRI_EMOTION_LR, tfMRI_EMOTION_RL, tfMRI_WM_LR, tfMRI_WM_RL, etc.)"
    echo "   <temporal-filter> - temporal filtering previously applied to the data (should be 2000)"
    echo "   <original-smoothing> - spatial smoothing already applied to the data (should be 2mm (or 2))"
    echo "   <regressor-file> - time series from seed to be used for seed-based  analysis. "
    echo "   <template-dir> - folder in which to find FSF template files"
    echo "   <out-dir>      - output directory in which to place generated level 1 FSF file"
    echo ""
    echo " Image file for which to produce an FSF file will be expected to be found at: "
    echo "   <study-folder>/<subject-id>/MNINonLinear/Results/<task-name>/<task-name>.nii.gz"
    echo ""
    echo " Template file for generation of an FSF file will be expected to be found at: "
    echo "   <template-dir>/<task-name>_hp2000_s2_level1.fsf"
    echo ""
    echo " Generated FSF file will be at: "
    echo "   <out-dir>/<task-name>_hp2000_s2_level1.fsf"


}

# Function description
#  Get the command line options for this script
#
# Global output variables
#  ${StudyFolder} - study folder
#  ${Subject} - subject ID
#  ${taskname} - task name
# ${temporalfilter} - temporal filter
# ${originalsmoothing} - original spatial smoothing
#  ${templatedir} - template directory
#  ${outdir} - output directory
#

# Source fsl
export PATH=/usr/local/fsl/bin:${PATH}

get_options() {
    local scriptName=$(basename ${0})
    local arguments=($@)

    # initialize global output variables
    unset StudyFolder
    unset Subject
    unset taskname
    unset temporalfilter
    unset originalsmoothing
    unset templatedir
    unset outdir

    # parse arguments
    local index=0
    local numArgs=${#arguments[@]}
    local argument

    while [ ${index} -lt ${numArgs} ]; do
		argument=${arguments[index]}

		case ${argument} in
			--help)
				usage
				exit 1
				;;
			--studyfolder=*)
				StudyFolder=${argument#*=}
				index=$(( index + 1 ))
				;;
			--subject=*)
				Subject=${argument#*=}
				index=$(( index + 1 ))
				;;				
			--taskname=*)
				taskname=${argument#*=}
				index=$(( index + 1 ))
				;;
            --temporalfilter=*)
                temporalfilter=${argument#*=}
                index=$(( index + 1 ))
                ;;
            --originalsmoothing=*)
                originalsmoothing=${argument#*=}
                index=$(( index + 1 ))
                ;;
			--regressor_file=*)
				regressor_file=${argument#*=}
				index=$(( index + 1 ))
				;;
			--templatedir=*)
				templatedir=${argument#*=}
				index=$(( index + 1 ))
				;;
			--outdir=*)
				outdir=${argument#*=}
				index=$(( index + 1 ))
				;;
			*)
				usage
				echo ""
				echo "ERROR: Unrecognized Option: ${argument}"
				echo ""
				exit 1
				;;
		esac
    done

    # check required parameters
    if [ -z ${StudyFolder} ]; then
		usage
		echo ""
		echo "ERROR: <study-folder> not specified"
		echo ""
		exit 1
    fi
	
    if [ -z ${Subject} ]; then
		usage
		echo ""
		echo "ERROR: <subject-id> not specified"
		echo ""
		exit 1
    fi
	
    if [ -z ${taskname} ]; then
		usage
		echo ""
		echo "ERROR: <task-name> not specified"
		echo ""
		exit 1
    fi
    if [ -z ${temporalfilter} ]; then
		usage
		echo ""
		echo "ERROR: <temporal-filter> not specified"
		echo ""
		exit 1
    fi
    if [ -z ${originalsmoothing} ]; then
		usage
		echo ""
		echo "ERROR: <original-smoothing> not specified"
		echo ""
		exit 1
    fi
    if [ -z ${regressor_file} ]; then
		usage
		echo ""
		echo "ERROR: <regressor-file> not specified"
		echo ""
		exit 1
    fi
	
    if [ -z ${templatedir} ]; then
		usage
		echo ""
		echo "ERROR: <template-dir> not specified"
		echo ""
		exit 1
    fi
	
    if [ -z ${outdir} ]; then
		usage
		echo ""
		echo "ERROR: <out-dir> not specified"
		echo ""
		exit 1
    fi
	
    # report
    echo ""
    echo "-- ${scriptName}: Specified command-line options - Start --"
    echo "   <study-folder>: ${StudyFolder}"
    echo "   <subject-id>: ${Subject}"
    echo "   <regressor-file>: ${regressor_file}"
    echo "   <temporal-filter>: ${temporalfilter}"
    echo "   <original-smoothing>: ${originalsmoothing}"
    echo "   <task-name>: ${taskname}"
    echo "   <template-dir>: ${templatedir}"
    echo "   <out-dir>: ${outdir}"
    echo "-- ${scriptName}: Specified command-line options - End --"
    echo ""
}

#
# Main processing
#
main() {
    get_options $@
    
    TemporalFilterString="_hp${temporalfilter}"
    OriginalSmoothingString="_s${originalsmoothing}"

    # figure out where the task image file is
    taskfiles=`ls ${StudyFolder}/${Subject}/MNINonLinear/Results/*${taskname}*/*${taskname}_*${TemporalFilterString}_clean.nii.gz`
	for taskfile in $taskfiles;
	do
	    taskfile_base=`basename $taskfile`
	    echo ""
    	    echo "Preparing FSF file for: "
    	    echo "  ${taskfile}"
    	    echo ""

    	    # get the number of time points in the image file
    	    FMRI_NPTS=`fslinfo ${taskfile} | grep -w 'dim4' | awk '{print $2}'`

    	    # figure out where the template FSF file is
	    fsf_template_file=${templatedir}/${taskname}${TemporalFilterString}${OriginalSmoothingString}_level1.fsf

	    # copy the template file to the intended destination FSF file
	    cp -p ${fsf_template_file} ${outdir}/${taskname}${TemporalFilterString}${OriginalSmoothingString}_level1.fsf

	    # modify the destination by putting in the correct number of time points
	    sed -i "s/fmri(npts) [0-9]*/fmri(npts) ${FMRI_NPTS}/" ${outdir}/${taskname}${TemporalFilterString}${OriginalSmoothingString}_level1.fsf
	    sed -i "s:FEATFILE:${taskfile_base}:g" ${outdir}/${taskname}${TemporalFilterString}${OriginalSmoothingString}_level1.fsf
	    sed -i "s:REGRESSOR:${regressor_file}:g" ${outdir}/${taskname}${TemporalFilterString}${OriginalSmoothingString}_level1.fsf

	    echo ""
	    echo "Level 1 FSF file generated at: "
	    echo "  ${outdir}/${taskname}${TemporalFilterString}${OriginalSmoothingString}_level1.fsf"
	    echo ""
       done
}

# Invoke the main function
main $@





