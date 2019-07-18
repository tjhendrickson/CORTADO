#!/bin/bash

set -x

#~ND~FORMAT~MARKDOWN~
#~ND~START~
#
# # RestfMRIAnalysis.sh
#
# ## Copyright (c) 2011-2019 The Human Connectome Project and The Connectome Coordination Facility
#
# ## Author(s)
#
# * Timothy Hendrickson, University of Minnesota Informatics Institute, Minneapolis, Minnesota
# ## Product
#
# [Human Connectome Project][HCP] (HCP) Pipelines
#
# ## License
#
# See the [LICENSE](https://github.com/Washington-University/Pipelines/blob/master/LICENCE.md) file
#
# ## Description
#
# This script is a simple dispatching script for running Resting State Seed fMRI Analysis.
#
# <!-- References -->                                                                                                             
# [HCP]: http://www.humanconnectome.org
# [FSL]: http://fsl.fmrib.ox.ac.uk
#
#~ND~END~   

# If any command used in this script exits with a non-zero value, this script itself exits 
# and does not attempt any further processing.
set -e

########################################## READ_ARGS ##################################


# Parse expected arguments from command-line array
echo "READ_ARGS: Parsing Command Line Options"
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
		--indir=*)
			indir=${argument#*=}
			index=$(( index + 1 ))
			;;
		--outdir=*)
			outdir=${argument#*=}
			index=$(( index + 1 ))
			;;
		--lvl1tasks=*)
			LevelOnefMRINames=${argument#*=}
			index=$(( index + 1 ))
			;;
		--lvl1fsfs=*)
			LevelOnefsfNames=${argument#*=}
			index=$(( index + 1 ))
			;;		
		--lvl2task=*)
			LevelTwofMRIName=${argument#*=}
			index=$(( index + 1 ))
			;;
		--lvl2fsf=*)
			LevelTwofsfNames=${argument#*=}
			index=$(( index + 1 ))
			;;
		--lowresmesh=*)
			LowResMesh=${argument#*=}
			index=$(( index + 1 ))
			;;
		--grayordinatesres=*)
			GrayordinatesResolution=${argument#*=}
			index=$(( index + 1 ))
			;;
		--origsmoothingFWHM=*)
			OriginalSmoothingFWHM=${argument#*=}
			index=$(( index + 1 ))
			;;
		--confound=*)
			Confound=${argument#*=}
			index=$(( index + 1 ))
			;;
		--finalsmoothingFWHM=*)
			FinalSmoothingFWHM=${argument#*=}
			index=$(( index + 1 ))
			;;		
		--temporalfilter=*)
			TemporalFilter=${argument#*=}
			index=$(( index + 1 ))
			;;
		--vba=*)
			VolumeBasedProcessing=${argument#*=}
			index=$(( index + 1 ))
			;;
		--regname=*)
			RegName=${argument#*=}
			index=$(( index + 1 ))
			;;
		--parcellation=*)
			Parcellation=${argument#*=}
			index=$(( index + 1 ))
			;;
		--parcellationfile=*)
			ParcellationFile=${argument#*=}
			index=$(( index + 1 ))
			;;
		--seedROI=*)
			seedROI=${argument#*=}
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


# Write command-line arguments to log file
echo "READ_ARGS: outdir: ${outdir}"
echo "READ_ARGS: indir: ${indir}"
echo "READ_ARGS: LevelOnefMRINames: ${LevelOnefMRINames}"
echo "READ_ARGS: LevelOnefsfNames: ${LevelOnefsfNames}"
echo "READ_ARGS: LevelTwofMRIName: ${LevelTwofMRIName}"
echo "READ_ARGS: LevelTwofsfName: ${LevelTwofsfName}"
echo "READ_ARGS: LowResMesh: ${LowResMesh}"
echo "READ_ARGS: GrayordinatesResolution: ${GrayordinatesResolution}"
echo "READ_ARGS: OriginalSmoothingFWHM: ${OriginalSmoothingFWHM}"
echo "READ_ARGS: Confound: ${Confound}"
echo "READ_ARGS: FinalSmoothingFWHM: ${FinalSmoothingFWHM}"
echo "READ_ARGS: TemporalFilter: ${TemporalFilter}"
echo "READ_ARGS: VolumeBasedProcessing: ${VolumeBasedProcessing}"
echo "READ_ARGS: RegName: ${RegName}"
echo "READ_ARGS: Parcellation: ${Parcellation}"
echo "READ_ARGS: ParcellationFile: ${ParcellationFile}"
echo "READ_ARGS: seedROI: ${seedROI}"
########################################## MAIN #########################################

# Determine locations of necessary directories (using expected naming convention)
AtlasFolder="${indir}/${Subject}/MNINonLinear"
ResultsFolder="${AtlasFolder}/Results"
ROIsFolder="${AtlasFolder}/ROIs"
DownSampleFolder="${AtlasFolder}/fsaverage_LR${LowResMesh}k"


# Run Level 1 analyses for each phase encoding direction (from command line arguments)
echo "MAIN: RUN_LEVEL1: Running Level 1 Analysis for Both Phase Encoding Directions"
i=1
# Level 1 analysis names were delimited by '@' in command-line; change to space in for loop
for LevelOnefMRIName in $( echo $LevelOnefMRINames | sed 's/@/ /g' ) ; do
	echo "MAIN: RUN_LEVEL1: LevelOnefMRIName: ${LevelOnefMRIName}"	
	# Get corresponding fsf name from $LevelOnefsfNames list
	LevelOnefsfName=`echo $LevelOnefsfNames | cut -d "@" -f $i`
	echo "MAIN: RUN_LEVEL1: Issuing command: /RestfMRILevel1.sh $Subject $ResultsFolder $ROIsFolder $DownSampleFolder $LevelOnefMRIName $LevelOnefsfName $LowResMesh $GrayordinatesResolution $OriginalSmoothingFWHM $Confound $FinalSmoothingFWHM $TemporalFilter $VolumeBasedProcessing $RegName $Parcellation $ParcellationFile $seedROI"
	/RestfMRILevel1.sh \
	  $Subject \
	  $ResultsFolder \
	  $ROIsFolder \
	  $DownSampleFolder \
	  $LevelOnefMRIName \
	  $LevelOnefsfName \
	  $LowResMesh \
	  $GrayordinatesResolution \
	  $OriginalSmoothingFWHM \
	  $Confound \
	  $FinalSmoothingFWHM \
	  $TemporalFilter \
	  $VolumeBasedProcessing \
	  $RegName \
	  $Parcellation \
	  $ParcellationFile \
	  $seedROI
	i=$(($i+1))
done

echo "MAIN: Completed"

