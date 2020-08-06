 #!/bin/bash

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
#set -e

########################################## READ_ARGS ##################################

# Parse expected arguments from command-line array
get_options(){
	scriptName=`basename ${0}`
    arguments=($@)
    
    # initialize global output variables
	unset outdir
    unset AtlasFolder
    unset Pipeline
	unset ICAoutputs
    unset FinalFile
	unset volFinalFile
	unset BoldRef
	unset fMRIFilename
	unset fMRIFolderName
	unset LevelTwoFolderName
	unset LowResMesh
	unset GrayordinatesResolution
	unset OriginalSmoothingFWHM
	unset Confound
	unset FinalSmoothingFWHM
	unset TemporalFilter
	unset RegName
	unset Parcellation
	unset ParcellationFile
	unset seedROI

	# parse arguments
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
			--outdir=*)
				outdir=${argument#*=}
				index=$(( index + 1 ))
				;;
			--AtlasFolder=*)
				AtlasFolder=${argument#*=}
				index=$(( index + 1 ))
				;;
			--pipeline=*)
				Pipeline=${argument#*=}
				index=$(( index + 1 ))
				;;
			--ICAoutputs=*)
				ICAoutputs=${argument#*=}
				index=$(( index + 1 ))
				;;
			--finalfile=*)
				FinalFile=${argument#*=}
				index=$(( index + 1 ))
				;;
			--volfinalfile=*)
				volFinalFile=${argument#*=}
				index=$(( index + 1 ))
				;;
			--boldref=*)
				BoldRef=${argument#*=}
				index=$(( index + 1 ))
				;;
			--fmrifilename=*)
				fMRIFilename=${argument#*=}
				index=$(( index + 1 ))
				;;
			--fmrifoldername=*)
				fMRIFolderName=${argument#*=}
				index=$(( index + 1 ))
				;;		
			--lvl2fmrifoldername=*)
				LevelTwoFolderName=${argument#*=}
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

# Output command line arguments to stdout
echo "READ_ARGS: outdir: ${outdir}"
echo "READ_ARGS: Pipeline: ${Pipeline}"
echo "READ_ARGS: AtlasFolder: ${AtlasFolder}"
echo "READ_ARGS: ICAoutputs: ${ICAoutputs}"
echo "READ_ARGS: File Derivative to Use for Analysis: ${FinalFile}"
echo "READ_ARGS: Volumetric File Derivative to Use for Analysis: ${volFinalFile}"
echo "READ_ARGS: Rest Reference Image: ${BoldRef}"
echo "READ_ARGS: fMRIFilename: ${fMRIFilename}"
echo "READ_ARGS: fMRIFolderName: ${fMRIFolderName}"
echo "READ_ARGS: LevelTwoFolderName: ${LevelTwoFolderName}"
echo "READ_ARGS: LowResMesh: ${LowResMesh}"
echo "READ_ARGS: GrayordinatesResolution: ${GrayordinatesResolution}"
echo "READ_ARGS: OriginalSmoothingFWHM: ${OriginalSmoothingFWHM}"
echo "READ_ARGS: Confound: ${Confound}"
echo "READ_ARGS: FinalSmoothingFWHM: ${FinalSmoothingFWHM}"
echo "READ_ARGS: TemporalFilter: ${TemporalFilter}"
echo "READ_ARGS: RegName: ${RegName}"
echo "READ_ARGS: Parcellation: ${Parcellation}"
echo "READ_ARGS: ParcellationFile: ${ParcellationFile}"
echo "READ_ARGS: seedROI: ${seedROI}"
}
########################################## MAIN #########################################
#main() {
	get_options $@
	
	#echo "$LevelTwoFolderName"
	#exit

	# Determine locations of necessary directories (using expected naming convention)
	DownSampleFolder="${AtlasFolder}/fsaverage_LR${LowResMesh}k"
	ResultsFolder="${AtlasFolder}/Results"
	ROIsFolder="${AtlasFolder}/ROIs"
	# Run Level 1 analyses (from command line arguments)
	
	if [ $LevelTwoFolderName = "NONE" ]; then

	echo "MAIN: RUN_LEVEL1: Running Level 1 Analysis"
	echo "MAIN: RUN_LEVEL1: Issuing command: /RestfMRILevel1.sh --outdir=$outdir --pipeline=$Pipeline --ICAoutputs=$ICAoutputs --finalfile=$FinalFile --volfinalfile=${volFinalFile} --boldref=${BoldRef} --fmrifilename=$fMRIFilename --fmrifoldername=$fMRIFolderName --ResultsFolder=$ResultsFolder --ROIsFolder=$ROIsFolder --DownSampleFolder=$DownSampleFolder --lowresmesh=$LowResMesh --grayordinatesres=$GrayordinatesResolution --origsmoothingFWHM=$OriginalSmoothingFWHM --confound=$Confound --finalsmoothingFWHM=$FinalSmoothingFWHM --temporalfilter=$TemporalFilter  --regname=$RegName --parcellation=$Parcellation --parcellationfile=$ParcellationFile --seedROI=$seedROI"
	/RestfMRILevel1.sh \
	--outdir=$outdir \
		--pipeline=$Pipeline \
		--ICAoutputs=$ICAoutputs \
		--finalfile=$FinalFile \
		--volfinalfile=$volFinalFile \
		--boldref=${BoldRef} \
		--fmrifilename=$fMRIFilename \
		--fmrifoldername=$fMRIFolderName \
		--ResultsFolder=$ResultsFolder \
		--ROIsFolder=$ROIsFolder \
		--DownSampleFolder=$DownSampleFolder \
		--lowresmesh=$LowResMesh \
		--grayordinatesres=$GrayordinatesResolution \
		--origsmoothingFWHM=$OriginalSmoothingFWHM \
		--confound=$Confound \
		--finalsmoothingFWHM=$FinalSmoothingFWHM \
		--temporalfilter=$TemporalFilter \
		--regname=$RegName \
		--parcellation=$Parcellation \
		--parcellationfile=$ParcellationFile \
		--seedROI=$seedROI
	else
		# Combine Data Across Phase Encoding Directions in the Level 2 Analysis
		echo "MAIN: RUN_LEVEL2: Combine Data Across Phase Encoding Directions in the Level 2 Analysis"
		echo "MAIN: RUN_LEVEL2: Issuing command: /RestfMRILevel2.sh --outdir=$outdir --pipeline=$Pipeline --ICAoutputs=$ICAoutputs --fmrifilenames=$LevelOnefMRINames --lvl2fmrifoldername=$LevelTwoFolderName --finalsmoothingFWHM=$FinalSmoothingFWHM --temporalfilter=$TemporalFilter --regname=$RegName --parcellation$Parcellation --seedROI=$seedROI"
		/RestfMRILevel2.sh \
		--outdir=$outdir \
		--pipeline=$Pipeline
		--ICAoutputs=$ICAoutputs \
		--fmrifilenames=$LevelOnefMRINames \
		--lvl2fmrifoldername=$LevelTwoFolderName \
		--finalsmoothingFWHM=$FinalSmoothingFWHM \
		--temporalfilter=$TemporalFilter \
		--regname=$RegName \
		--parcellation$Parcellation \ 
		--seedROI=$seedROI \
	fi

	echo "MAIN: Completed"
#}

# Invoke the main function
#main $@

