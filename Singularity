Bootstrap: docker

From: ubuntu:trusty-20170119

%files

run.py /run.py
modified_files/generate_level1_fsf.sh /generate_level1_fsf.sh
modified_files/RestfMRIAnalysis.sh /RestfMRIAnalysis.sh
modified_files/RestfMRILevel1.sh /RestfMRILevel1.sh
modified_files/rsfMRI_seed.py /rsfMRI_seed.py

%environment

export CARET7DIR=/opt/workbench/bin_rh_linux64
export HCPPIPEDIR=/opt/HCP-Pipelines
export HCPPIPEDIR_Templates=/opt/HCP-Pipelines/global/templates
export HCPPIPEDIR_Bin=/opt/HCP-Pipelines/global/binaries
export HCPPIPEDIR_Config=/opt/HCP-Pipelines/global/config
export HCPPIPEDIR_PreFS=/opt/HCP-Pipelines/PreFreeSurfer/scripts
export HCPPIPEDIR_FS=/opt/HCP-Pipelines/FreeSurfer/scripts
export HCPPIPEDIR_PostFS=/opt/HCP-Pipelines/PostFreeSurfer/scripts
export HCPPIPEDIR_fMRISurf=/opt/HCP-Pipelines/fMRISurface/scripts
export HCPPIPEDIR_fMRIVol=/opt/HCP-Pipelines/fMRIVolume/scripts
export HCPPIPEDIR_tfMRI=/opt/HCP-Pipelines/tfMRI/scripts
export HCPPIPEDIR_dMRI=/opt/HCP-Pipelines/DiffusionPreprocessing/scripts
export HCPPIPEDIR_dMRITract=/opt/HCP-Pipelines/DiffusionTractography/scripts
export HCPPIPEDIR_Global=/opt/HCP-Pipelines/global/scripts
export HCPPIPEDIR_tfMRIAnalysis=/opt/HCP-Pipelines/TaskfMRIAnalysis/scripts
export OS=Linux
export FS_OVERRIDE=0
export FIX_VERTEX_AREA=
export FSF_OUTPUT_FORMAT=nii.gz
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH
export PYTHONPATH=""
export FSLDIR=/usr/share/fsl/5.0
export FSL_DIR="${FSLDIR}"
export FSLOUTPUTTYPE=NIFTI_GZ
export PATH=/usr/lib/fsl/5.0:$PATH
export FSLMULTIFILEQUIT=TRUE
export POSSUMDIR=/usr/share/fsl/5.0
export LD_LIBRARY_PATH=/usr/lib/fsl/5.0
export FSLTCLSH=/usr/bin/tclsh
export FSLWISH=/usr/bin/wish
export FSLOUTPUTTYPE=NIFTI_GZ

%post

# Make script executable
chmod +x /run.py

# Make local folders/files
mkdir /share
mkdir /scratch
mkdir /local-scratch
mkdir /bids_dir
mkdir /output_dir
mkdir /fsf_template_dir
touch /parcel_dlabel.nii

# Install basic utilities
apt-get -qq update
apt-get install -yq --no-install-recommends python wget bc bzip2 ca-certificates curl libglu1-mesa libgomp1 perl-modules tar tcsh unzip git libgomp1 perl-modules curl libfreetype6 libfreetype6-dev


# Install FSL 5.0.11
apt-get update
cd /tmp
wget https://fsl.fmrib.ox.ac.uk/fsldownloads/fslinstaller.py
python fslinstaller.py -d /usr/local/fsl -E -V 5.0.11 -q -D
export FSLDIR=/usr/local/fsl
. ${FSLDIR}/etc/fslconf/fsl.sh
PATH=${FSLDIR}/bin:${PATH}
${FSLDIR}/etc/fslconf/fslpython_install.sh

# Install HCP Pipelines v3.27.0
apt-get update
cd /opt/
wget https://github.com/Washington-University/Pipelines/archive/v3.27.0.tar.gz -O pipelines.tar.gz
mkdir /opt/HCP-Pipelines
tar zxf /opt/pipelines.tar.gz -C /opt/HCP-Pipelines --strip-components=1
rm /opt/pipelines.tar.gz
wget -qO- https://www.doc.ic.ac.uk/~ecr05/MSM_HOCR_v2/MSM_HOCR_v2-download.tgz | tar xz -C /tmp
mv /tmp/homes/ecr05/MSM_HOCR_v2/Ubuntu /opt/HCP-Pipelines/MSMBinaries
apt-get clean
rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Install anaconda and needed python tools
cd /opt
wget https://repo.continuum.io/archive/Anaconda2-2018.12-Linux-x86_64.sh -O /opt/Anaconda2.sh
bash /opt/Anaconda2.sh -b -p /opt/Anaconda2
export PATH="/opt/Anaconda2/bin:${PATH}"
/opt/Anaconda2/bin/pip install nibabel cifti pandas
#is this necessary?
#/opt/Anaconda2/bin/pip install certificates

# Install the validator 0.26.11, along with pybids 0.6.0
apt-get update
apt-get install -y curl
curl -sL https://deb.nodesource.com/setup_10.x | bash -
apt-get remove -y curl
apt-get install -y nodejs
npm install -g bids-validator@0.26.11
/opt/Anaconda2/bin/pip install git+https://github.com/INCF/pybids.git@0.6.0


# Copy needed files into container
cp /generate_level1_fsf.sh /opt/HCP-Pipelines/Examples/Scripts/
cp /RestfMRIAnalysis.sh /opt/HCP-Pipelines/TaskfMRIAnalysis/
cp /RestfMRILevel1.sh /opt/HCP-Pipelines/TaskfMRIAnalysis/

# Install Connectome Workbench dev version
apt-get update
cd /opt
wget http://brainvis.wustl.edu/workbench/workbench-rh_linux64-dev_latest.zip
unzip workbench-rh_linux64-dev_latest.zip
export PATH=/opt/workbench/bin_rh_linux64:${PATH}


# Upgrade our libstdc++
echo "deb http://ftp.de.debian.org/debian stretch main" >> /etc/apt/sources.list
apt-get update
apt-get install -y --force-yes libstdc++6 nano

%runscript

exec /run.py "$@"

