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
# The ${FSLDIR}/etc/fslversion file is used to determine the version of [FSL][FSL] in use.
#
# <!-- References -->                                                                                                             
# [HCP]: http://www.humanconnectome.org
# [FSL]: http://fsl.fmrib.ox.ac.uk
#
#~ND~END~   

# If any command used in this script exits with a non-zero value, this script itself exits 
# and does not attempt any further processing.
set -e


########################################## PREPARE FUNCTIONS ########################################## 


# function to test FSL versions
determine_old_or_new_fsl()
{
	# NOTE: 
	#   Don't echo anything in this function other than the last echo
	#   that outputs the return value
	#   
	local fsl_version=${1}
	local old_or_new
	local fsl_version_array
	local fsl_primary_version
	local fsl_secondary_version
	local fsl_tertiary_version

	# parse the FSL version information into primary, secondary, and tertiary parts
	fsl_version_array=(${fsl_version//./ })

	fsl_primary_version="${fsl_version_array[0]}"
	fsl_primary_version=${fsl_primary_version//[!0-9]/}
	
	fsl_secondary_version="${fsl_version_array[1]}"
	fsl_secondary_version=${fsl_secondary_version//[!0-9]/}
	
	fsl_tertiary_version="${fsl_version_array[2]}"
	fsl_tertiary_version=${fsl_tertiary_version//[!0-9]/}

	# determine whether we are using "OLD" or "NEW" FSL 
	# 5.0.6 and below is "OLD"
	# 5.0.7 and above is "NEW"
	if [[ $(( ${fsl_primary_version} )) -lt 5 ]]
	then
		# e.g. 4.x.x    
		old_or_new="OLD"
	elif [[ $(( ${fsl_primary_version} )) -gt 5 ]]
	then
		# e.g. 6.x.x    
		old_or_new="NEW"
	else
		# e.g. 5.x.x
		if [[ $(( ${fsl_secondary_version} )) -gt 0 ]]
		then
			# e.g. 5.1.x
			old_or_new="NEW"
		else
			# e.g. 5.0.x
			if [[ $(( ${fsl_tertiary_version} )) -le 6 ]]
			then
				# e.g. 5.0.5 or 5.0.6
				old_or_new="OLD"
			else
				# e.g. 5.0.7 or 5.0.8
				old_or_new="NEW"
			fi
		fi
	fi
	
	echo ${old_or_new}
}


########################################## READ_ARGS ##################################

# Explcitly set tool name for logging
log_SetToolName "RestfMRIAnalysis.sh"

# Show version of HCP Pipeline Scripts in use if requested
opts_ShowVersionIfRequested $@

# Parse expected arguments from command-line array
log_Msg "READ_ARGS: Parsing Command Line Options"
Path=`opts_GetOpt1 "--path" $@`
LevelOnefMRINames=`opts_GetOpt1 "--lvl1tasks" $@`
LevelOnefsfNames=`opts_GetOpt1 "--lvl1fsfs" $@`
LevelTwofMRIName=`opts_GetOpt1 "--lvl2task" $@`
LevelTwofsfNames=`opts_GetOpt1 "--lvl2fsf" $@`
LowResMesh=`opts_GetOpt1 "--lowresmesh" $@`
GrayordinatesResolution=`opts_GetOpt1 "--grayordinatesres" $@`
OriginalSmoothingFWHM=`opts_GetOpt1 "--origsmoothingFWHM" $@`
Confound=`opts_GetOpt1 "--confound" $@`
FinalSmoothingFWHM=`opts_GetOpt1 "--finalsmoothingFWHM" $@`
TemporalFilter=`opts_GetOpt1 "--temporalfilter" $@`
VolumeBasedProcessing=`opts_GetOpt1 "--vba" $@`
RegName=`opts_GetOpt1 "--regname" $@`
Parcellation=`opts_GetOpt1 "--parcellation" $@`
ParcellationFile=`opts_GetOpt1 "--parcellationfile" $@`
seedROI=`opts_GetOpt1 "--seedROI" $@`


# Write command-line arguments to log file
log_Msg "READ_ARGS: Path: ${Path}"
log_Msg "READ_ARGS: LevelOnefMRINames: ${LevelOnefMRINames}"
log_Msg "READ_ARGS: LevelOnefsfNames: ${LevelOnefsfNames}"
log_Msg "READ_ARGS: LowResMesh: ${LowResMesh}"
log_Msg "READ_ARGS: GrayordinatesResolution: ${GrayordinatesResolution}"
log_Msg "READ_ARGS: OriginalSmoothingFWHM: ${OriginalSmoothingFWHM}"
log_Msg "READ_ARGS: Confound: ${Confound}"
log_Msg "READ_ARGS: FinalSmoothingFWHM: ${FinalSmoothingFWHM}"
log_Msg "READ_ARGS: TemporalFilter: ${TemporalFilter}"
log_Msg "READ_ARGS: VolumeBasedProcessing: ${VolumeBasedProcessing}"
log_Msg "READ_ARGS: RegName: ${RegName}"
log_Msg "READ_ARGS: Parcellation: ${Parcellation}"
log_Msg "READ_ARGS: ParcellationFile: ${ParcellationFile}"
log_Msg "READ_ARGS: seedROI: ${seedROI}"

########################################## MAIN #########################################

# Determine if required FSL version is present
fsl_version_get fsl_ver
old_or_new_version=$(determine_old_or_new_fsl ${fsl_ver})
if [ "${old_or_new_version}" == "OLD" ]
then
	# Need to exit script due to incompatible FSL VERSION!!!!
	log_Msg "MAIN: TEST_FSL_VERSION: ERROR: Detected pre-5.0.7 version of FSL in use (version ${fsl_ver}). Rest fMRI Analysis not invoked. Exiting."
	exit 1
else
	log_Msg "MAIN: TEST_FSL_VERSION: Beginning analyses with FSL version ${fsl_ver}"
fi

# Determine locations of necessary directories (using expected naming convention)
AtlasFolder="${Path}/${Subject}/MNINonLinear"
ResultsFolder="${AtlasFolder}/Results"
ROIsFolder="${AtlasFolder}/ROIs"
DownSampleFolder="${AtlasFolder}/fsaverage_LR${LowResMesh}k"


# Run Level 1 analyses for each phase encoding direction (from command line arguments)
log_Msg "MAIN: RUN_LEVEL1: Running Level 1 Analysis for Both Phase Encoding Directions"
i=1
# Level 1 analysis names were delimited by '@' in command-line; change to space in for loop
for LevelOnefMRIName in $( echo $LevelOnefMRINames | sed 's/@/ /g' ) ; do
	log_Msg "MAIN: RUN_LEVEL1: LevelOnefMRIName: ${LevelOnefMRIName}"	
	# Get corresponding fsf name from $LevelOnefsfNames list
	LevelOnefsfName=`echo $LevelOnefsfNames | cut -d "@" -f $i`
	log_Msg "MAIN: RUN_LEVEL1: Issuing command: /opt/HCP-Pipelines/TaskfMRIAnalysis/RestfMRILevel1.sh $Subject $ResultsFolder $ROIsFolder $DownSampleFolder $LevelOnefMRIName $LevelOnefsfName $LowResMesh $GrayordinatesResolution $OriginalSmoothingFWHM $Confound $FinalSmoothingFWHM $TemporalFilter $VolumeBasedProcessing $RegName $Parcellation $ParcellationFile $seedROI"
	/opt/HCP-Pipelines/TaskfMRIAnalysis/RestfMRILevel1.sh \
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

log_Msg "MAIN: Completed"

