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
    echo " Usage ${scriptName}  --taskname=<task-name> --temporal-filter=<temporal-filter> --originalsmoothing=<original-smoothing>"
    echo "                      --outdir=<out-dir>"
    echo ""
    echo "   <task-name>    - name of task file for which to produce level 2 FSF file"
    echo "                    (e.g. tfMRI_EMOTION_LR, tfMRI_EMOTION_RL, tfMRI_WM_LR, tfMRI_WM_RL, etc.)"
    echo "   <temporal-filter> - temporal filtering previously applied to the data (should be 2000)"
    echo "   <original-smoothing> - spatial smoothing already applied to the data (should be 2mm (or 2))"
    echo "   <out-dir>      - output directory in which to place generated level 2 FSF file"
    echo ""
    echo ""
    echo ""
    echo " Generated FSF file will be at: "
    echo "   <out-dir>/"


}

# Function description
#  Get the command line options for this script
#
# Global output variables
#  ${taskname} - task name
# ${temporalfilter} - temporal filter
# ${originalsmoothing} - original spatial smoothing
#  ${outdir} - output directory
#

# Source fsl
export PATH=/usr/local/fsl/bin:${PATH}

get_options() {
    local scriptName=$(basename ${0})
    local arguments=($@)

    # initialize global output variables
    unset taskname
    unset temporalfilter
    unset originalsmoothing
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
    echo "   <temporal-filter>: ${temporalfilter}"
    echo "   <original-smoothing>: ${originalsmoothing}"
    echo "   <task-name>: ${taskname}"
    echo "   <out-dir>: ${outdir}"
    echo "-- ${scriptName}: Specified command-line options - End --"
    echo ""
}

#
# Main processing
#
main() {
    get_options $@
    
    TemporalFilterString="_hp200"
    OriginalSmoothingString="_s4"

	
	echo ""
	echo "Preparing FSF file for: "
	echo "  ${taskname}"
	echo ""

	# figure out where the template FSF file is
	fsf_template_file="/task-rest_level2.fsf"

	# does ${outdir} exist? if not create it
	if [ ! -d ${outdir} ]; then
		mkdir -p ${outdir}
	fi

	# copy the template file to the intended destination FSF file
	cp -p /task-rest_level2.fsf ${outdir}/${taskname}${TemporalFilterString}${OriginalSmoothingString}_level2.fsf

	echo ""
	echo "Level 2 FSF file generated at: "
	echo "  ${outdir}/${taskname}${TemporalFilterString}${OriginalSmoothingString}_level2.fsf"
	echo ""

}

# Invoke the main function
main $@





