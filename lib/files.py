import glob
import os
import re
from pathlib import Path


class Files:
    @staticmethod
    def list_files(data_path, extensions='.asc'):
        """
        Function to list all files from target folder with subdirectories.
        Using selected target file extension to filter files
        :param data_path: target data folder
        :param extensions: target file extension
        :return:
        """
        result_paths = []
        for root, dirs, files in os.walk(data_path):
            for file in files:
                for ext in extensions:
                    if file.endswith(ext):
                        # print(os.path.join(root, file))
                        result_paths.append(os.path.join(root, file))
        return result_paths


def file_parser(folder_path):
    """
    Parse file list from selected data folder
    :return: list of founded file paths, list of founded file names
    """
    extensions = ['asc']
    files_paths = []
    for ext in extensions:
        files_paths += glob.glob(folder_path + "/*." + ext)
    files_names = []
    for file in files_paths:
        ff = Path(file)
        files_names.append(os.path.basename(ff))

    # sort file names by digits
    files_names = sorted(files_names,
                         key=lambda x: float(re.findall('(\d+)', x)[0]))

    # recreate sorted file paths
    files_paths = []
    for file in files_names:
        files_paths.append(os.path.join(folder_path, file))

    return files_paths, files_names
