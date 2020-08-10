Running CORTADO
=====================================

Hosting
-------

The containerization of this application is maintained and hosted on Singularity Hub. To inspect build, click: |build-location|

Pull the most recent container by typing the command below into a linux terminal, (**NOTE: you do not have to do this every time before executing the container!**)::  
  
	singularity pull shub://tjhendrickson/CORTADO


Singularity Usage
-----------------

 At any time you can look at usage by typing in a terminal::
 
  singularity run /path/to/CORTADO/container -h

To run the container properly, you will likely have to "bind" several folders with the "-B" flag so the container can see needed data. 
For example consider the case in which your inputted data is within the folder "/local_input_dir", your intended output folder is "/local_output_dir" and your parcellation file of interest is in "/parcel_file_location". The command would be::

	singularity run -B /local_input_dir:/input_dir -B /local_output_dir:/output_dir -B /parcel_file_location:/media /path/to/CORTADO/container --input_dir /input_dir --output_dir /output_dir --parcellation_file /media/NameOfParcelFile.dlabel.nii ...
 
Notice the use of the folders "/input_dir", "/output_dir", and "/media" following the ":" and within the container. Leave those as is, and just change out the actual paths to your data.

Now let us take this a step further. Imagine again that the input, output, and parcel file data are in the same location. 
You are additionally interested in: 
1) running a batch on an entire dataset 
2) Would like to use the Yeo 2011 atlas for your parcellation file 
3) The left thalamus is your seed of interest. 
Your command would be::

	singularity run -B /local_input_dir:/input_dir -B /local_output_dir:/output_dir -B /parcel_file_location:/media /path/to/CORTADO/container --input_dir /input_dir --output_dir /output_dir  --group batch --parcellation_file /media/Yeo2011.dlabel.nii --parcellation_name THALAMUS_LEFT 

There are more complicated cases such as combining across multiple ROIs, averaging rsfMRI scans together within a sessions, and others, however, that is beyond the scope. For more advanced use cases please contact Tim Hendrickson at hendr522@umn.edu.

.. |build-location| image:: https://www.singularity-hub.org/static/img/hosted-singularity--hub-%23e32929.svg
    :alt: build location
    :scale: 100%
    :target: https://singularity-hub.org/collections/3125