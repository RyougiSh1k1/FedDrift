#!/bin/bash

# install pyflakes to do code error checking
echo "pip3 install pyflakes --cache-dir $HOME/.pip-cache"
pip3 install pyflakes --cache-dir $HOME/.pip-cache

# Conda Installation
wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh
bash miniconda.sh -b -p $HOME/miniconda
source "$HOME/miniconda/etc/profile.d/conda.sh"
hash -r
conda config --set always_yes yes --set changeps1 no
conda update -q conda
conda info -a

echo "conda create -q -n fedml python=3.7.4"
conda create -q -n fedml python=3.7.4

echo "conda activate fedml"
conda activate fedml

# Install PyTorch (please visit pytorch.org to check your version according to your physical machines
conda install pytorch torchvision cudatoolkit=10.2 -c pytorch

# Install MPI
conda install -c anaconda mpi4py

# Install Wandb
pip install --upgrade wandb

# Install other required package
pip install setproctitle
