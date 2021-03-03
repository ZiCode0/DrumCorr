import io
from parse import *


example_header_text = '''~CHINFONEED 1 55.1132000000 160.2938000000 1500 0 0 -90 3.51969e+007 1
~POLZERCOEFF 1 0
~POLZINFO 10 4 A 1 1.32011e+013 1 1 0
~POL -2.74017 4.49874
~POL -2.74017 -4.49874
~POL -299.259 0
~POL -99.5268 0
~POL -0.168108 0
~POL -0.238117 0
~POL -152.109 31.2558
~POL -152.109 -31.2558
~POL -17.1487 139.986
~POL -17.1487 -139.986
~ZER 0 0
~ZER 0 0
~ZER 0 0
~ZER 0 0
'''


class PreHeader:
    def __init__(self):
        """
        Class to define specific station characteristic from header
        """
        self.dict = {}
        self.header_line_format = '~{key} {value}'

    def add_record(self, line_dict):
        """
        Add record to characteristic dictionary
        :param line_dict: line record in dictionary format
        :return: updated self.dict
        """
        current_key = next(iter(line_dict))
        if current_key in list(self.dict.keys()):
            buf = []
            # convert first line args to whole list object
            while type(self.dict[current_key][0]) is not list:
                buf.append(self.dict[current_key][0])
                self.dict[current_key].pop(0)
                if len(self.dict[current_key]) == 0:
                    self.dict[current_key].insert(0, buf)
            # add values list to existing key
            self.dict[current_key] += [line_dict[current_key]]
        else:
            # add new key values list
            self.dict[current_key] = line_dict[current_key]
        # print()  # uncomment for #debug

    def add_record_from_str(self, text_line):
        """
        Parse input string line to add characteristic dictionary record
        :param text_line: target string line
        :return: updated self.dict
        """
        res_line_dict = self.get_pheader_line_dict(text_line)
        self.add_record(res_line_dict)

    def get_pheader_line_dict(self, header_text_line):
        """
        Convert header line to dictionary format
        :param header_text_line: target string line
        :return: line as dictionary
        """
        args = parse(self.header_line_format, header_text_line).named
        args['value'] = args['value'].replace('\n', '').split()
        res_dict = {args['key']: args['value']}
        return res_dict

    def parse_pheader_text(self, header_text):
        """
        Parse text-object to characteristic dictionary
        :param header_text: target text with characteristic lines
        :return: updated self.dict
        """
        header_text = io.StringIO(header_text)
        for line in header_text.readlines():
            line_dict = self.get_pheader_line_dict(line)
            self.add_record(line_dict)

    def add_extras(self, line):
        """
        Add extra characteristics
        :param line: input line with extra params
        :return: updated self.dict
        """
        line = line.replace('\n', '')
        self.dict['extra'] += [line]


if __name__ == "__main__":
    hd = PreHeader()
    hd.parse_pheader_text(example_header_text)
    print(hd.dict)
