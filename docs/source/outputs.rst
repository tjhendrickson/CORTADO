Outputs of CORTADO
==================

Unless specified, CORTADO will automatically output a CSV file.

1. Each row indicates a different scanning session
2. The first two columns indicate the subject and session IDs (pulled directly from subject and session BIDS identifiers) with the remaining columns being ROIs based on the parcellation file chosen
3. The name of the CSV file will be in the form of 
   rsfMRIScanName_Atlas_REG_NAME_hp2000_clean_PARCEL_NAME_FIXclean_level1_seedSEED_NAME.csv
	* "REG_NAME, PARCEL_NAME and "SEED_NAME" correspond to arguments specified
	* "rsfMRIScanName" is pulled directly from the rsfMRI data file name
4. The CSV file will be outputted to the bound folder pointing to "/output_dir" (see :doc:`singularity`)

With more complicated use-cases CORTADO will output differently named CSV files. Email Tim Hendrickson at hendr522@umn.edu with questions.

