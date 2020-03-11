#!/bin/bash
set -e

#~ND~FORMAT~MARKDOWN~
#~ND~START~
#
# # RestfMRILevel2.sh
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
# This script runs Level 2 Resting State Seed fMRI Analysis.
#
# <!-- References -->                                                                                                             
# [HCP]: http://www.humanconnectome.org
# [FSL]: http://fsl.fmrib.ox.ac.uk
#
#~ND~END~   


set -e
set -x


# Requirements for this script
#  installed versions of FSL 6.0.1
#  environment: FSLDIR, CARET7DIR 

########################################## PREPARE FUNCTIONS ########################################## 

export PATH=/usr/local/fsl/bin:${PATH}

show_tool_versions()
{
	# Show wb_command version
	echo "TOOL_VERSIONS: Showing Connectome Workbench (wb_command) version"
	${CARET7DIR}/wb_command -version

	echo "TOOL_VERSION: Showing FSL version"
	cat /usr/local/fsl/etc/fslversion
}



########################################## READ COMMAND-LINE ARGUMENTS ##################################
get_options(){
local scriptName=$(basename $0)
	local arguments=($@)
    
    	# initialize global output variables
	unset outdir
	unset Pipeline
	unset ICAoutputs
	unset fMRIFilenames
	unset LevelTwoFolderName
	unset FinalSmoothingFWHM
	unset TemporalFilter
	unset RegName
	unset Parcellation
	unset seedROI

	# parse arguments
	echo "READ_ARGS: Parsing Command Line Options"
    	local index=0
    	local numArgs=${#arguments[@]}
    	local argument

	while [ ${index} -lt ${numArgs} ]; do
		argument=${arguments[index]}

		case ${argument} in
			--outdir=*)
				outdir=${argument#*=}
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
			--fmrifilenames=*)
				fMRIFilenames=${argument#*=}
				index=$(( index + 1 ))
				;;
			--lvl2fmrifoldername=*)
				LevelTwoFolderName=${argument#*=}
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
			--seedROI=*)
				seedROI=${argument#*=}
				index=$(( index + 1 ))
				;;
			*)
				echo ""
				echo "ERROR: Unrecognized Option: ${argument}"
				echo ""
				exit 1
				;;
		esac
	done
	# Write command-line arguments to log file
	echo "READ_ARGS: outdir: ${outdir}"
	echo "READ_ARGS: Pipeline: ${Pipeline}"
	echo "READ_ARGS: ICAstring: ${ICAoutputs}"
	echo "READ_ARGS: fMRIFilenames: ${fMRIFilenames}"
	echo "READ_ARGS: LevelTwoFolderName: ${LevelTwoFolderName}"
	echo "READ_ARGS: FinalSmoothingFWHM: ${FinalSmoothingFWHM}"
	echo "READ_ARGS: TemporalFilter: ${TemporalFilter}"
	echo "READ_ARGS: RegName: ${RegName}"
	echo "READ_ARGS: Parcellation: ${Parcellation}"
	echo "READ_ARGS: seedROI: ${seedROI}"
}

main(){
	
	# Log versions of tools used by this script
	get_options $@
	show_tool_versions

	########################################## MAIN ##################################

	##### DETERMINE ANALYSES TO RUN (DENSE, PARCELLATED, VOLUME) #####

	# initialize run variables
	runParcellated=false; runVolume=false; runDense=false;
	Analyses=""; ExtensionList=""; ScalarExtensionList="";


	# Determine whether to run Parcellated, and set strings used for filenaming
	if [[ "${Parcellation}" != "NONE" ]] ; then
		# Run Parcellated Analyses
		runParcellated=true;
		ParcellationString="_${Parcellation}"
		if [[ "${Pipeline}" = "HCP" ]]; then
			ExtensionList="${ExtensionList}ptseries.nii "
			ScalarExtensionList="${ScalarExtensionList}pscalar.nii "
			Analyses="${Analyses}ParcellatedStats "; # space character at end to separate multiple analyses
		elif [[ "${Pipeline}" = "fmriprep" ]]; then
			ExtensionList="${ExtensionList}_parcellated_timeseries.nii.gz"
			ScalarExtensionList="${ScalarExtensionList}_parcellated_scalar.nii.gz"
			Analyses="${Analyses}ParcellatedStats "; # space character at end to separate multiple analyses
		fi
		echo "MAIN: DETERMINE_ANALYSES: Parcellated Analysis requested"
	fi

	if [[ "${Pipeline}" = "fmriprep" ]]; then
		runVolume=true;
		echo "MAIN: DETERMINE_ANALYSES: Volume Analysis requested"
	fi


	# Determine whether to run Dense, and set strings used for filenaming
	if [[ "${Parcellation}" = "NONE" ]]; then
		# Run Dense Analyses
		runDense=true;
		ParcellationString=""
		if [[ "${Pipeline}" = "HCP" ]]; then
			ExtensionList="${ExtensionList}dtseries.nii "
			ScalarExtensionList="${ScalarExtensionList}dscalar.nii "
			Analyses="${Analyses}GrayordinatesStats "; # space character at end to separate multiple analyses
		elif [[ "${Pipeline}" = "fmriprep" ]]; then
			ExtensionList="${ExtensionList}_dense_timeseries.nii.gz "
			ScalarExtensionList="${ScalarExtensionList}_dense_scalar.nii.gz "
			Analyses="${Analyses}GrayordinatesStats "; # space character at end to separate multiple analyses
		fi
		echo "MAIN: DETERMINE_ANALYSES: Dense Analysis requested"
	fi

	# Determine whether to run Volume, and set strings used for filenaming
	if [[ $VolumeBasedProcessing = "YES" ]] ; then
		runVolume=true;
		ExtensionList="${ExtensionList}nii.gz "
		ScalarExtensionList="${ScalarExtensionList}volume.dscalar.nii "
		Analyses="${Analyses}StandardVolumeStats "; # space character at end to separate multiple analyses	
		echo "MAIN: DETERMINE_ANALYSES: Volume Analysis requested"
	fi

	echo "MAIN: DETERMINE_ANALYSES: Analyses: ${Analyses}"
	echo "MAIN: DETERMINE_ANALYSES: ParcellationString: ${ParcellationString}"
	echo "MAIN: DETERMINE_ANALYSES: ExtensionList: ${ExtensionList}"
	echo "MAIN: DETERMINE_ANALYSES: ScalarExtensionList: ${ScalarExtensionList}"


	##### SET VARIABLES REQUIRED FOR FILE NAMING #####

	### Set smoothing and filtering string variables used for file naming

	# Set variables used for different registration procedures
	if [[ "${RegName}" != "NONE" ]] ; then
		RegString="_${RegName}"
	else
		RegString=""
	fi
	SmoothingString="_s${FinalSmoothingFWHM}"
	TemporalFilterString="_hp${TemporalFilter}"
	echo "MAIN: SET_NAME_STRINGS: SmoothingString: ${SmoothingString}"
	echo "MAIN: SET_NAME_STRINGS: TemporalFilterString: ${TemporalFilterString}"
	echo "MAIN: SET_NAME_STRINGS: RegString: ${RegString}"

	### Figure out where the Level1 .feat directories are located
	# Change '@' delimited arguments to space-delimited lists for use in for loops
	fMRIFilenames=`echo $fMRIFilenames | sed 's/@/ /g'`

	# Loop over list to make string with paths to the Level1 .feat directories
	LevelOneFEATDirSTRING=""
	NumFirstLevelFolders=0; # counter
	for fMRIFilename in $fMRIFilenames ; do 
	NumFirstLevelFolders=$(($NumFirstLevelFolders+1));
	# get fsf name that corresponds to fMRI name
	LevelOneFEATDirSTRING="${LevelOneFEATDirSTRING}${outdir}/${fMRIFilename}${ParcellationString}${ICAoutputs}_level1_seed${seedROI}.feat "; # space character at end is needed to separate multiple FEATDir strings
	done
	
	echo "Level One FEAT Dirs: ${LevelOneFEATDirSTRING}"

	### Determine list of contrasts for this analysis
	FirstFolder=`echo $LevelOneFEATDirSTRING | cut -d " " -f 1`
	ContrastNames="seed${seedROI}"
	NumContrasts=1


	##### MAKE DESIGN FILES AND LEVEL2 DIRECTORY #####

	# Make LevelTwoFEATDir
	LevelTwoFEATDir="${outdir}/${LevelTwoFolderName}${TemporalFilterString}${SmoothingString}${RegString}${ParcellationString}${ICAoutputs}_level2_seed${seedROI}.feat"
	if [ -e ${LevelTwoFEATDir} ] ; then
    	rm -r ${LevelTwoFEATDir}
    	mkdir ${LevelTwoFEATDir}
    else
    	mkdir -p ${LevelTwoFEATDir}
    fi

	# Edit template.fsf and place it in LevelTwoFEATDir
	cat ${outdir}/${LevelTwoFolderName}_hp200_s4_level2.fsf | sed s/_hp200_s4/${TemporalFilterString}${SmoothingString}${RegString}${ParcellationString}/g > ${LevelTwoFEATDir}/design.fsf

	# Make additional design files required by flameo
	echo "Make design files"
	cd ${LevelTwoFEATDir}; # Run feat_model inside LevelTwoFEATDir so relative paths work
	feat_model ${LevelTwoFEATDir}/design
	cd $OLDPWD; # Go back to previous directory using bash built-in $OLDPWD


	##### RUN flameo (FIXED-EFFECTS GLM ANALYSIS ON LEVEL2) #####

	### Loop over Level 2 Analyses requested
	echo "Loop over Level 2 Analyses requested: ${Analyses}"
	analysisCounter=1;
	for Analysis in ${Analyses} ; do
		echo "Run Analysis: ${Analysis}"
		Extension=`echo $ExtensionList | cut -d' ' -f $analysisCounter`;
		ScalarExtension=`echo $ScalarExtensionList | cut -d' ' -f $analysisCounter`;

		### Exit if cope files are not present in Level 1 folders
		fileCount=$( ls ${FirstFolder}/${Analysis}/cope1.${Extension} 2>/dev/null | wc -l );
		if [[ "$fileCount" -eq 0 ]]; then
			echo "ERROR: Missing expected cope files in ${FirstFolder}/${Analysis}"
			echo "ERROR: Exiting $g_script_name"
			exit 1
		fi

		### Copy Level 1 stats folders into Level 2 analysis directory
		echo "Copy over Level 1 stats folders and convert CIFTI to NIFTI if required"
		mkdir -p ${LevelTwoFEATDir}/${Analysis}
		i=1
		for LevelOneFEATDir in ${LevelOneFEATDirSTRING} ; do
			mkdir -p ${LevelTwoFEATDir}/${Analysis}/${i}
			cp ${LevelOneFEATDir}/${Analysis}/* ${LevelTwoFEATDir}/${Analysis}/${i}
			i=$(($i+1))
		done

		### convert CIFTI files to fakeNIFTI if required
		if [[ "${Analysis}" != "StandardVolumeStats" ]] ; then
			echo "Convert CIFTI files to fakeNIFTI"
			fakeNIFTIused="YES"
			for CIFTI in ${LevelTwoFEATDir}/${Analysis}/*/*.${Extension} ; do
				fakeNIFTI=$( echo $CIFTI | sed -e "s|.${Extension}|.nii.gz|" );
				${CARET7DIR}/wb_command -cifti-convert -to-nifti $CIFTI $fakeNIFTI
				rm $CIFTI
			done
		else
			fakeNIFTIused="NO"
		fi

		### Create dof and Mask files for input to flameo (Level 2 analysis)
		echo "Create dof and Mask files for input to flameo (Level 2 analysis)"
		MERGESTRING=""
		i=1
		while [[ "$i" -le "${NumFirstLevelFolders}" ]] ; do
			dof=`cat ${LevelTwoFEATDir}/${Analysis}/${i}/dof`
			fslmaths ${LevelTwoFEATDir}/${Analysis}/${i}/res4d.nii.gz -Tstd -bin -mul $dof ${LevelTwoFEATDir}/${Analysis}/${i}/dofmask.nii.gz
			MERGESTRING=`echo "${MERGESTRING}${LevelTwoFEATDir}/${Analysis}/${i}/dofmask.nii.gz "`
			i=$(($i+1))
		done
		fslmerge -t ${LevelTwoFEATDir}/${Analysis}/dof.nii.gz $MERGESTRING
		fslmaths ${LevelTwoFEATDir}/${Analysis}/dof.nii.gz -Tmin -bin ${LevelTwoFEATDir}/${Analysis}/mask.nii.gz

		### Create merged cope and varcope files for input to flameo (Level 2 analysis)
		echo "Merge COPES and VARCOPES for ${NumContrasts} Contrasts"
		copeCounter=1
		while [[ "$copeCounter" -le "${NumContrasts}" ]] ; do
			echo "Contrast Number: ${copeCounter}"
			COPEMERGE=""
			VARCOPEMERGE=""
			i=1
			while [[ "$i" -le "${NumFirstLevelFolders}" ]] ; do
			COPEMERGE="${COPEMERGE}${LevelTwoFEATDir}/${Analysis}/${i}/cope${copeCounter}.nii.gz "
			VARCOPEMERGE="${VARCOPEMERGE}${LevelTwoFEATDir}/${Analysis}/${i}/varcope${copeCounter}.nii.gz "
			i=$(($i+1))
			done
			fslmerge -t ${LevelTwoFEATDir}/${Analysis}/cope${copeCounter}.nii.gz $COPEMERGE
			fslmerge -t ${LevelTwoFEATDir}/${Analysis}/varcope${copeCounter}.nii.gz $VARCOPEMERGE
			copeCounter=$(($copeCounter+1))
		done

		### Run 2nd level analysis using flameo
		echo "Run flameo (Level 2 analysis) for ${NumContrasts} Contrasts"
		copeCounter=1
		while [[ "$copeCounter" -le "${NumContrasts}" ]] ; do
			echo "Contrast Number: ${copeCounter}"
			echo "$( which flameo )"
			echo "Command: flameo --cope=${Analysis}/cope${copeCounter}.nii.gz \\"
			echo "  --vc=${Analysis}/varcope${copeCounter}.nii.gz \\"
			echo "  --dvc=${Analysis}/dof.nii.gz \\"
			echo "  --mask=${Analysis}/mask.nii.gz \\"
			echo "  --ld=${Analysis}_fixedEffects \\"
			echo "  --dm=design.mat \\"
			echo "  --cs=design.grp \\"
			echo "  --tc=design.con \\"
			echo "  --runmode=fe"

			cd ${LevelTwoFEATDir}; # run flameo within LevelTwoFEATDir so relative paths work
			flameo --cope=${Analysis}/cope${copeCounter}.nii.gz \
				--vc=${Analysis}/varcope${copeCounter}.nii.gz \
				--dvc=${Analysis}/dof.nii.gz \
				--mask=${Analysis}/mask.nii.gz \
				--ld=${Analysis}_fixedEffects \
				--dm=design.mat \
				--cs=design.grp \
				--tc=design.con \
				--runmode=fe

			echo "Successfully completed flameo for Contrast Number: ${copeCounter}"
			cd $OLDPWD; # Go back to previous directory using bash built-in $OLDPWD
			copeCounter=$(($copeCounter+1))
		done

		### Cleanup Temporary Files (which were copied from Level1 stats directories)
		echo "Cleanup Temporary Files"
		i=1
		while [[ "$i" -le "${NumFirstLevelFolders}" ]] ; do
			rm -r ${LevelTwoFEATDir}/${Analysis}/${i}
			i=$(($i+1))
		done

		### Convert fakeNIFTI Files back to CIFTI (if necessary)
		if [[ "$fakeNIFTIused" = "YES" ]] ; then
			echo "Convert fakeNIFTI files back to CIFTI"
			CIFTItemplate="${LevelOneFEATDir}/${Analysis}/pe1.${Extension}"

			# convert flameo input files for review: ${LevelTwoFEATDir}/${Analysis}_fixedEffects/*.nii.gz
			# convert flameo output files for each cope: ${LevelTwoFEATDir}/${Analysis}_fixedEffects*.nii.gz
			for fakeNIFTI in  ${LevelTwoFEATDir}/${Analysis}/*.nii.gz ${LevelTwoFEATDir}/${Analysis}_fixedEffects/*.nii.gz; do
				CIFTI=$( echo $fakeNIFTI | sed -e "s|.nii.gz|.${Extension}|" );
				${CARET7DIR}/wb_command -cifti-convert -from-nifti $fakeNIFTI $CIFTItemplate $CIFTI -reset-timepoints 1 1
				rm $fakeNIFTI
			done
		fi
		
		### Generate Files for Viewing
		echo "Generate Files for Viewing"
		# Initialize strings used for fslmerge command
		zMergeSTRING=""
		bMergeSTRING=""
		touch ${LevelTwoFEATDir}/Contrasttemp.txt
		[[ "${Analysis}" = "StandardVolumeStats" ]] && touch ${LevelTwoFEATDir}/wbtemp.txt
		[[ -e "${LevelTwoFEATDir}/Contrasts.txt" ]] && rm ${LevelTwoFEATDir}/Contrasts.txt

		# Loop over contrasts to identify cope and zstat files to merge into wb_view scalars
		copeCounter=1;
		while [[ "$copeCounter" -le "${NumContrasts}" ]] ; do
			Contrast=`echo $ContrastNames | cut -d " " -f $copeCounter`
			# Contrasts.txt is used to store the contrast names for this analysis
			echo ${Contrast} >> ${LevelTwoFEATDir}/Contrasts.txt
			# Contrasttemp.txt is a temporary file used to name the maps in the CIFTI scalar file
			echo "${LevelTwoFolderName}_level2_${Contrast}${TemporalFilterString}${SmoothingString}${RegString}${ParcellationString}" >> ${LevelTwoFEATDir}/Contrasttemp.txt

			if [[ "${Analysis}_fixedEffects" = "StandardVolumeStats" ]] ; then

				### Make temporary dtseries files to convert into scalar files
				# Converting volume to dense timeseries requires a volume label file
				echo "OTHER" >> ${LevelTwoFEATDir}/wbtemp.txt
				echo "1 255 255 255 255" >> ${LevelTwoFEATDir}/wbtemp.txt
				${CARET7DIR}/wb_command -volume-label-import ${LevelTwoFEATDir}/StandardVolumeStats/mask.nii.gz ${LevelTwoFEATDir}/wbtemp.txt ${LevelTwoFEATDir}/StandardVolumeStats/mask.nii.gz -discard-others -unlabeled-value 0
				rm ${LevelTwoFEATDir}/wbtemp.txt

				# Convert temporary volume CIFTI timeseries files
				${CARET7DIR}/wb_command -cifti-create-dense-timeseries ${LevelTwoFEATDir}/${LevelTwoFolderName}_level2_zstat_${Contrast}${TemporalFilterString}${SmoothingString}${RegString}${ParcellationString}.volume.dtseries.nii -volume ${LevelTwoFEATDir}/StandardVolumeStats/zstat1.nii.gz ${LevelTwoFEATDir}/StandardVolumeStats/mask.nii.gz -timestep 1 -timestart 1
				${CARET7DIR}/wb_command -cifti-create-dense-timeseries ${LevelTwoFEATDir}/${LevelTwoFolderName}_level2_cope_${Contrast}${TemporalFilterString}${SmoothingString}${RegString}${ParcellationString}.volume.dtseries.nii -volume ${LevelTwoFEATDir}/StandardVolumeStats/cope1.nii.gz ${LevelTwoFEATDir}/StandardVolumeStats/mask.nii.gz -timestep 1 -timestart 1

				# Convert volume CIFTI timeseries files to scalar files
				${CARET7DIR}/wb_command -cifti-convert-to-scalar ${LevelTwoFEATDir}/${LevelTwoFolderName}_level2_zstat_${Contrast}${TemporalFilterString}${SmoothingString}${RegString}${ParcellationString}.volume.dtseries.nii ROW ${LevelTwoFEATDir}/${LevelTwoFolderName}_level2_zstat_${Contrast}${TemporalFilterString}${SmoothingString}${RegString}${ParcellationString}.${ScalarExtension} -name-file ${LevelTwoFEATDir}/Contrasttemp.txt
				${CARET7DIR}/wb_command -cifti-convert-to-scalar ${LevelTwoFEATDir}/${LevelTwoFolderName}_level2_cope_${Contrast}${TemporalFilterString}${SmoothingString}${RegString}${ParcellationString}.volume.dtseries.nii ROW ${LevelTwoFEATDir}/${LevelTwoFolderName}_level2_cope_${Contrast}${TemporalFilterString}${SmoothingString}${RegString}${ParcellationString}.${ScalarExtension} -name-file ${LevelTwoFEATDir}/Contrasttemp.txt

				# Delete the temporary volume CIFTI timeseries files
				rm ${LevelTwoFEATDir}/${LevelTwoFolderName}_level2_{cope,zstat}_${Contrast}${TemporalFilterString}${SmoothingString}${RegString}${ParcellationString}.volume.dtseries.nii
			else
				### Convert CIFTI dense or parcellated timeseries to scalar files
				${CARET7DIR}/wb_command -cifti-convert-to-scalar ${LevelTwoFEATDir}/${Analysis}_fixedEffects/zstat1.${Extension} ROW ${LevelTwoFEATDir}/${LevelTwoFolderName}_level2_zstat_${Contrast}${TemporalFilterString}${SmoothingString}${RegString}${ParcellationString}.${ScalarExtension} -name-file ${LevelTwoFEATDir}/Contrasttemp.txt
				${CARET7DIR}/wb_command -cifti-convert-to-scalar ${LevelTwoFEATDir}/${Analysis}_fixedEffects/cope1.${Extension} ROW ${LevelTwoFEATDir}/${LevelTwoFolderName}_level2_cope_${Contrast}${TemporalFilterString}${SmoothingString}${RegString}${ParcellationString}.${ScalarExtension} -name-file ${LevelTwoFEATDir}/Contrasttemp.txt
			fi

			# These merge strings are used below to combine the multiple scalar files into a single file for visualization
			zMergeSTRING="${zMergeSTRING}-cifti ${LevelTwoFEATDir}/${LevelTwoFolderName}_level2_zstat_${Contrast}${TemporalFilterString}${SmoothingString}${RegString}${ParcellationString}.${ScalarExtension} "
			bMergeSTRING="${bMergeSTRING}-cifti ${LevelTwoFEATDir}/${LevelTwoFolderName}_level2_cope_${Contrast}${TemporalFilterString}${SmoothingString}${RegString}${ParcellationString}.${ScalarExtension} "

			# Remove Contrasttemp.txt file
			rm ${LevelTwoFEATDir}/Contrasttemp.txt
			copeCounter=$(($copeCounter+1))
		done

		# Perform the merge into viewable scalar files
		${CARET7DIR}/wb_command -cifti-merge ${LevelTwoFEATDir}/${LevelTwoFolderName}_level2_zstat${TemporalFilterString}${SmoothingString}${RegString}${ParcellationString}.${ScalarExtension} ${zMergeSTRING}
		${CARET7DIR}/wb_command -cifti-merge ${LevelTwoFEATDir}/${LevelTwoFolderName}_level2_cope${TemporalFilterString}${SmoothingString}${RegString}${ParcellationString}.${ScalarExtension} ${bMergeSTRING}
		
		analysisCounter=$(($analysisCounter+1))
	done  # end loop: for Analysis in ${Analyses}
	echo "Complete"
}

main $@
