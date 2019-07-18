Bootstrap: docker

From: ubuntu:trusty-20170119

%files

run.py /run.py
modified_files/generate_level1_fsf.sh /generate_level1_fsf.sh
modified_files/RestfMRIAnalysis.sh /RestfMRIAnalysis.sh
modified_files/RestfMRILevel1.sh /RestfMRILevel1.sh
modified_files/RestfMRILevel1.sh /RestfMRILevel2.sh
modified_files/rsfMRI_seed.py /rsfMRI_seed.py
modified_files/task-rest_level1.fsf /task-rest_level1.fsf
modified_files/task-rest_level2.fsf /task-rest_level2.fsf


%environment

export CARET7DIR=/opt/workbench/bin_rh_linux64
export OS=Linux
export FS_OVERRIDE=0
export FIX_VERTEX_AREA=
export FSF_OUTPUT_FORMAT=nii.gz
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH
export PYTHONPATH=""
export FSLDIR=/usr/local/fsl
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
apt-get install -yq --no-install-recommends libglib2.0-0 python wget bc bzip2 ca-certificates libgomp1 perl-modules tar tcsh unzip git libgomp1 perl-modules curl libgl1-mesa-dev libfreetype6 libfreetype6-dev


# Install FSL 6.0.1
apt-get update
cd /tmp
wget https://fsl.fmrib.ox.ac.uk/fsldownloads/fslinstaller.py
python fslinstaller.py -d /usr/local/fsl -E -V 6.0.1 -q -D
export FSLDIR=/usr/local/fsl
. ${FSLDIR}/etc/fslconf/fsl.sh
export PATH=${FSLDIR}/bin:${PATH}
${FSLDIR}/etc/fslconf/fslpython_install.sh

# Install anaconda2 and needed python tools
cd /opt
wget https://repo.continuum.io/archive/Anaconda2-2018.12-Linux-x86_64.sh -O /opt/Anaconda2.sh
bash /opt/Anaconda2.sh -b -p /opt/Anaconda2
export PATH="/opt/Anaconda2/bin:${PATH}"
/opt/Anaconda2/bin/pip install nibabel cifti pandas

# Install the validator 0.26.11, along with pybids 0.6.0
apt-get update
apt-get install -y curl
curl -sL https://deb.nodesource.com/setup_10.x | bash -
apt-get remove -y curl
apt-get install -y nodejs
npm install -g bids-validator@0.26.11
/opt/Anaconda2/bin/pip install git+https://github.com/INCF/pybids.git@0.6.0

# Install Connectome Workbench version 1.3.2
apt-get update
cd /opt
wget http://brainvis.wustl.edu/workbench/workbench-rh_linux64-v1.3.2.zip
unzip workbench-rh_linux64-v1.3.2.zip
export PATH=/opt/workbench/bin_rh_linux64:${PATH}


# Upgrade our libstdc++
echo "deb http://ftp.de.debian.org/debian stretch main" >> /etc/apt/sources.list
apt-get update
apt-get install -y --force-yes libstdc++6 nano

# Make scripts executable
chmod +x /run.py /rsfMRI_seed.py /generate_level1_fsf.sh /RestfMRIAnalysis.sh /RestfMRILevel1.sh /task-rest_level1.fsf

%runscript

exec /run.py "$@"

