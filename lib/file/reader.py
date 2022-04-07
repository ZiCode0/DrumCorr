import numpy as np
from obspy import UTCDateTime, read, Trace, Stream

from lib import strings
from lib.file.extra import calibration_parser


class DCErrorReadingFile(Exception):
    """
    Custom error reading file instance
    """
    pass


class NewInputData:
    data = None
    start_time = None
    station = None  # station name
    channel = None  # channel name
    network = None  # network code
    location = ''  # location code
    sampling_rate = None  # 128
    samples_count = 0


class StreamReader:
    def __init__(self):
        """
        Universal stream reader
        """
        pass

    @staticmethod
    def create_stream(data):
        """
        Convert NewInputData to obspy Stream
        :param data: NewInputData class convert to obspy stream
        :return: stream
        """
        # Fill header attributes
        stats = {'network': data.network,
                 'station': data.station,
                 'location': data.location,
                 'channel': data.channel,
                 'npts': data.data.size,
                 'sampling_rate': data.sampling_rate, 'mseed': {'dataquality': 'D'},
                 'starttime': data.start_time}
        st = Stream([Trace(data=data.data, header=stats)])  # create stream
        return st

    @staticmethod
    def read_file_using_obspy(file_path):
        """
        Universal reader of file formats based on obspy function
        Read more about available formats:
        https://docs.obspy.org/packages/autogen/obspy.core.stream.read.html#supported-formats
        :type file_path: input target filename
        :return: obspy data stream
        """
        file_data = read(file_path)
        return file_data

    def read(self, path, plot_result=False):
        """
        Get obspy stream data for selected file
        :param plot_result: True if plot results
        :type path: input file name
        """
        try:
            stream = self.read_file_using_obspy(path)
            return stream
        except:  # TODO: Define exception
            """
            Try to read and convert to mseed format
            """
            first_line_is_header = True
            new_data = NewInputData()  # temp format to collect information

            def header_parser(header_line):
                """
                ASCII header parser
                Header example: 201109261033044948 KZV SHZ P2 7.8125 432636
                time: 2011-09-26 10:33:04.4948
                :param header_line: input header string
                :return:
                """
                hd = header_line.split()
                hd[0] = hd[0][:14] + '.' + hd[0][14:]  # make convertible to UTC format
                hd_time = UTCDateTime(hd[0])  # convert to UTC time format
                new_data.start_time = hd_time  # set time
                new_data.station = hd[1]
                new_data.channel = hd[2]
                new_data.network = hd[3]
                calc_rate = 1000 / float(hd[4])  # calculate sampling rate from DIMAS's format
                new_data.sampling_rate = float(calc_rate)  # set sampling rate
                new_data.samples_count = int(hd[5])  # set total count of sample

            with open(path, "r+") as f:
                lines = f.readlines()
                for line_idx in range(len(lines) - 1):
                    # print(lines[line])
                    if '~' in lines[line_idx]:
                        # add characteristic dictionary record
                        # self.pheader.add_record_from_str(lines[line])
                        continue
                    elif ('[' in lines[line_idx]) or (lines[line_idx].startswith('[')):
                        # add extra args
                        # self.pheader.add_extras(lines[line])
                        continue
                    elif lines[line_idx] == '\n':
                        continue
                    else:
                        if first_line_is_header:
                            header_parser(header_line=lines[line_idx])
                            first_line_is_header = False
                        else:
                            try:
                                new_data.data = np.array(lines[line_idx: -1])
                                # converting to array of floats
                                # using np.astype
                                new_data.data = new_data.data.astype(np.float)
                            except Exception:
                                raise DCErrorReadingFile(strings.Console.error_reading_file)

                            stream = self.create_stream(new_data)
                            if plot_result:
                                stream.plot()
                            return stream
