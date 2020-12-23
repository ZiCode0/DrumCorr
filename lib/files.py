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


def file_parser(conf):
    """
    Parse file list from selected data folder
    :return: list of founded file paths, list of founded file names
    """
    extensions = ['asc', 'mseed']
    files_paths = []
    for ext in extensions:
        files_paths += glob.glob(conf.param['data_folder'] + "/*." + ext)
    del ext
    # template prefix and postfix
    template_prefix, template_postfix = conf.param['template_filename_format'].split('{file_name}')
    # file prefix and postfix list
    exclude_fixes = [pattern.split('{file_name}') for pattern in conf.param['exclude_filename_formats']]
    # select one template
    template_path = [v for v in files_paths
                     if os.path.basename(v).startswith(template_prefix)
                     and os.path.basename(v).endswith(template_postfix)][0]
    files_paths.remove(template_path)  # exclude template from list
    # apply exclude on file list
    for ex in exclude_fixes:
        files_paths = [v for v in files_paths
                       if not (os.path.basename(v).startswith(ex[0])
                               and os.path.basename(v).endswith(ex[1]))]
    # sort file names by digits
    if len(files_paths) > 1:
        files_names = sorted(files_paths,
                             key=lambda x: float(re.findall('(\d+)', x)[0]))
    return template_path, files_paths
