from json import dumps, load
import os


class JsonConfig:
    def __init__(self, file_path: str):
        """
        Json input arguments parser
        :param file_path: input file path to input file
        """
        self.param = {'notify': None,
                      'data_folder': os.path.dirname(file_path)}
        self.param = {**self.param, **load(open(file_path, "r"))['config']}

    def print_config(self):
        """
        Print input arguments
        """
        out_dump = dumps(self.param,
                         indent=4,
                         sort_keys=True)
        out_dump = out_dump.replace(',', '')
        out_dump = out_dump.replace('{', '').replace('}', '')
        out_dump = out_dump.replace('[', '').replace(']', '')
        print('Config loaded:\n{config}'.format(config=out_dump))


if __name__ == '__main__':
    conf = JsonConfig('./../config/example/config_example.json')
    conf.print_config()
