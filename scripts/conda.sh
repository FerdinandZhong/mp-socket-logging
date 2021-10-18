set -e

mkdir ./build
# Download and init conda
MINICONDA_FILENAME=Miniconda3-latest-Linux-x86_64.sh
wget -O ./build/$MINICONDA_FILENAME  https://repo.anaconda.com/miniconda/${MINICONDA_FILENAME}
bash ./build/${MINICONDA_FILENAME} -b -f -p "${HOME}"/miniconda3
export PATH=$HOME/miniconda3/bin:$PATH
eval "$(conda shell.bash hook)"
conda init bash
# shellcheck disable=SC1090
source "$HOME"/.bashrc
