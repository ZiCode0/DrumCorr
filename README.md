# DrumCorr
[![forthebadge](https://forthebadge.com/images/badges/built-with-love.svg)](https://forthebadge.com)
[![forthebadge](https://forthebadge.com/images/badges/uses-brains.svg)](https://forthebadge.com)
[![forthebadge](https://forthebadge.com/images/badges/not-a-bug-a-feature.svg)](https://forthebadge.com)

[comment]: [![License](https://img.shields.io/pypi/l/obspy.svg)](https://pypi.python.org/pypi/obspy/)
[comment]: [![LGPLv3](https://www.gnu.org/graphics/lgplv3-88x31.png)](https://www.gnu.org/licenses/lgpl.html)

[![LICENSE](https://img.shields.io/static/v1?label=LICENSE&message=GPLv3&color=brightgreen&style=for-the-badge&color=grey)](https://www.gnu.org/licenses/lgpl.html)
[![Github watchers](https://img.shields.io/github/watchers/ZiCode0/DrumCorr?label=Watch&style=for-the-badge)](https://github.com/ZiCode0/DrumCorr)


DrumCorr is a Python project for calculating auto and cross correlation based on the Obspy library.

## Installation

Simply clone the repository and run the main file:

```bash
# git clone
git clone https://github.com/ZiCode0/DrumCorr.git
cd DrumCorr
# create python virtual environment
python -m venv .venv
# enter venv, linux:
source .venv/bin/activate  # windows: .venv\\Scripts\\activate.bat
# install dependencies
pip install -r requirements.txt
# run script
python main.py
```


## Usage
1. Enter virtual environment:
```bash 
source .venv/bin/activate
```
2. Prepare data folder as in example. Place data files with template, marked with `+` in file name.
<img src="example/data_folder.png" width="400">
3. Place and edit configuration Json file in this one.
Example can be found here: [example/config.json](example/config.json).
4. Specify the config file when running program.
```bash
python main.py -c data/2011-09-06/config.json
```



## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.