#!/opt/Anaconda2/bin/python

import nibabel.cifti2
import pandas as pd
import os
import cifti
import re
import pdb

def write_regressor(output_dir,cifti_file, parcel_file, seed_ROI_name, regressor_file):
    
    print('output_dir: ' + output_dir)
    print('cifti_file: ' + cifti_file)
    print('parcel_file: ' + parcel_file)
    print('seed_ROI_name: ' + str(seed_ROI_name))
    print('regressor_file: ' + regressor_file)
    
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)
    read_parcel_file = cifti.read(parcel_file)
    parcel_file_label_tuple = read_parcel_file[1][0][0][1]
    parcel_labels = []
    for value in parcel_file_label_tuple:
            if not '???' in parcel_file_label_tuple[value][0]:
                    parcel_labels.append(parcel_file_label_tuple[value][0])
    try:
        cifti_load = nibabel.cifti2.cifti2.load(cifti_file)
    except IOError:
        print("file does not exist")
    except:
        print("file does not look like a cifti file")

    # if not parcellated, first parcellate, then proceed to write regressor
    cifti_file_basename = os.path.basename(cifti_file)
    cifti_file_folder = output_dir
    if ".dtseries.nii" in cifti_file_basename:
        cifti_prefix = cifti_file_basename.split(".dtseries.nii")[0]
        os.system("/opt/workbench/bin_rh_linux64/wb_command -cifti-parcellate %s %s %s %s" 
                  % (cifti_file, 
                     parcel_file, 
                     "COLUMN", 
                     os.path.join(cifti_file_folder,cifti_prefix) + ".ptseries.nii"))
        cifti_file = os.path.join(cifti_file_folder,cifti_prefix) + ".ptseries.nii"
        try:
            cifti_load = nibabel.cifti2.cifti2.load(cifti_file)
        except IOError:
            print("file does not exist")
        except:
            print("file does not look like a cifti file")
    else:
        raise Exception("Best to include a dtseries file to ensure that the file is parcellated properly")
    
    regressor_file_path = os.path.join(cifti_file_folder,regressor_file)
    
    #create regressor file
    df = pd.DataFrame(cifti_load.get_fdata())
    df.columns = parcel_labels
    if type(seed_ROI_name) == str:
        df.to_csv(regressor_file_path,header=False,index=False,columns=[seed_ROI_name],sep=' ')
    else:
        df['avg'] = df[seed_ROI_name].mean(axis=1)
        df.to_csv(regressor_file_path,header=False,index=False,columns=['avg'],sep=' ')








