import glob
import os
from pathlib import Path
import re
import time

from obspy.signal.cross_correlation import correlation_detector

from lib.app import ConsoleApp
from lib.reader import StreamReader
from lib.result_report import Report
from lib.ztools import JsonConfig


class DrumCorr:
    """
    Cross-correlation in DrumBeats template analyzing
    """

    def __init__(self):
        self.report = Report(self.get_value_by_utc_time)

    def clean_report(self):
        self.report = Report(self.get_value_by_utc_time)

    @staticmethod
    def filter_data(data, filter_name, filter_params):
        """
        Filtering function
        :type data: target stream data
        :param filter_name: filter name. Default: bandpass
        :param filter_params: input filter parameters
        :return: filtered <obspy.core.stream.Stream>
        """
        if filter_name == 'bandpass':
            # local_filter_min = float(ca.filter_min)
            # local_filter_max = float(ca.filter_max)
            filtered_data = data.filter(filter_name,
                                        freqmin=float(filter_params[0]),
                                        freqmax=float(filter_params[0]))
            return filtered_data

    @staticmethod
    def set_first_beat_as_template(data, plot_result=False):
        """
        Get template for selected file: 20110926-10-33-obspy.asc
        :param plot_result: plot template
        :param data: input stream data
        :return:
        """
        st = data[0].stats.starttime
        pick_start = 18
        pick_end = pick_start + 18
        template_stream = data.slice(st + pick_start, st + pick_end)
        if plot_result:
            template_stream.plot()
        return template_stream

    def get_template(self, template_filename):
        """
        Get template for first-step xcorrelation
        :type template_filename: template filename to load
        """
        try:
            # template_file = read(template_filename)
            template_file = self.read_file(template_filename)
            return template_file
        except:
            return None

    @staticmethod
    def xcorr(data, template, detect_value=0.5):
        pass_step = 0.1  # pass step in seconds

        # samples / seconds
        # 128 s     1 sec
        #  64 s   0.5 sec
        #  32 s  0.25 sec +
        #  16 s 0.125 sec

        detections, sims = correlation_detector(stream=data,
                                                templates=template,
                                                heights=detect_value,
                                                distance=pass_step,
                                                plot=None)
        if len(detections) != 0:
            del detections[0]
        return detections, sims

    @staticmethod
    def approx_xcorr(detections):
        approx_mass = []
        for detect in detections:
            approx_mass.append(detect['similarity'])
        approx_result = sum(approx_mass) / len(approx_mass)
        return approx_result

    def get_value_by_utc_time(self, stream, utc_time, function_method=0, trace_index=0, deepness=12):
        """
        Function to get stream value using selected UTC time
        :param stream: target stream
        :param utc_time: time point to select value
        :param trace_index: index of stream trace to search value
        :param function_method: select variant of function logic
        :param deepness:
        :return: result value(float)
        """

        if function_method == 0:
            """
            OLD VERSION OF CODE USING OBSPY FUNCTIONS
            CAUSES PYTHON MEMORY ERROR WHILE CALCULATING BIG DATA
            """
            if self.report.times is not None:
                index = self.report.times.searchsorted(utc_time)
                result_value = stream[trace_index].data[index]
                return result_value
            else:
                self.report.times = stream[trace_index].times('utcdatetime')
                index = self.report.times.searchsorted(utc_time)
                result_value = stream[trace_index].data[index]
                return result_value

        elif function_method == 1:
            """
            Modification of first method with division of target stream 
            """
            # TODO: Rewrite to solve bug

            pp = stream[trace_index].data.shape[0] / deepness
            partial_seconds_size = float(int(pp / 128))  # time part
            past_index = 0  # sum of last indexes to find latitude

            for stream_part_count in range(deepness):
                if stream_part_count == deepness - 1:
                    stream_part = stream.slice(
                        stream[trace_index].meta.starttime + partial_seconds_size * stream_part_count,
                        stream[trace_index].meta.endtime)

                    times = stream_part[trace_index].times('utcdatetime')
                    s_index = times.searchsorted(utc_time)
                    if s_index:
                        print(past_index + s_index, stream[trace_index].data[past_index + s_index])
                        return stream[trace_index].data[past_index + s_index]
                    else:
                        past_index += pp

                else:
                    stream_part = stream.slice(
                        stream[trace_index].meta.starttime + partial_seconds_size * stream_part_count,
                        stream[trace_index].meta.starttime + partial_seconds_size * (stream_part_count + 1))

                    times = stream_part[trace_index].times('utcdatetime')
                    s_index = times.searchsorted(utc_time)
                    if s_index:
                        print(past_index + s_index, stream[trace_index].data[past_index + s_index])
                        return stream[trace_index].data[past_index + s_index]
                    else:
                        past_index += pp

        elif function_method == 2:
            """
            ALTERNATIVE METHOD TO SELECTING STREAM VALUE
            Direct addressing to values
            """
            # TODO: Rewrite to solve bug

            start = stream[0].meta.starttime
            vector_delta = utc_time - start
            vv = int(vector_delta / stream[0].meta.delta)

            # print()  # place breakpoint for debugging

            result_value = stream[0].data[vv]
            return result_value

    def return_xcorr_max(self, stream, detects):
        """
        Returns max corr value from array of detects.
        Searching in 0 trace of input stream.
        :param stream: stream to find amplitude value by time
        :param detects: array of detections
        :return: xcorr value, maximum amplitude value
        """
        #  searching maximum object
        max_detect = None
        for detect in detects:
            if max_detect:
                if detect['similarity'] > max_detect['similarity']:
                    max_detect = detect
            else:
                max_detect = detect
        #  searching amplitude
        max_detect_amplitude = self.get_value_by_utc_time(stream=stream,
                                                          utc_time=max_detect['time'])
        return max_detect['similarity'], max_detect_amplitude

    @staticmethod
    def low_high_detects_sort_by_average(detects, min_value, max_value=None):
        """
        Sort array of detect to low and high using average number
        :type detects: array/list of detects to sort
        :type min_value: minimum value to calculate average level number
        :type max_value: maximum value to calculate average level number.
        Default input None value to force calculate.
        :return: average_level, low list, high list
        """
        min_array = []
        max_array = []
        average_level = 0
        if max_value:  # pass calculate max value
            average_level = (min_value + max_value) / 2
        for detect in detects:
            if detect['similarity'] > average_level:
                max_array.append(detect)
            else:
                min_array.append(detect)
        return average_level, min_array, max_array

    def check_xcorr_results(self, template_minimum_count):
        if len(self.report.detects) > template_minimum_count:
            return 1
        else:
            print(("[!] Cross-correlation returns 0 or low ({res_num}) number of results of\n"
                   "    file: <{file_name}>, quit..").format(res_num=len(self.report.detects),
                                                             file_name=self.report.current_file_name))
            return 0

    @staticmethod
    def read_file(file):
        sr = StreamReader()
        return sr.read(input_filename=file)


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

    return files_paths


def main():
    """
    Calculate cross-correlation for drum beats
    :return: Writes report file of cross-correlation function
    """

    ca = ConsoleApp()
    conf = JsonConfig(ca.args.config)
    dc = DrumCorr()

    dc.get_template(conf.param['template_file'])
    file_paths = file_parser(conf.param['data_folder'])
    for file_index in range(len(file_paths)):
        t = time.process_time()

        file = file_paths[file_index]
        dc.report.current_file_name = file_names[file_index]  # file name to results
        dc.report.detection_value = conf.param['xcorr_detection_value']  # detection value for xcorr

        dc.report.stream = dc.read_file(file)
        norm_stream = dc.report.stream.normalize()  # normalize
        template_object = dc.get_template(conf.param['template_file'])
        dc.report.detects, dc.report.sims = dc.xcorr(data=norm_stream,
                                                     template=template_object,
                                                     detect_value=conf.param['xcorr_detection_value'])
        if not dc.check_xcorr_results(template_minimum_count=conf.param['xcorr_minimum_count']):
            continue
        dc.report.beats_count = len(dc.report.detects)
        dc.report.approx_xcorr = dc.approx_xcorr(detections=dc.report.detects)
        dc.report.max_xcorr_value, dc.report.max_xcorr_amplitude = dc.return_xcorr_max(dc.report.stream,
                                                                                       dc.report.detects)
        dc.report.report_print()  # print results
        report_name = dc.report.generate_report_name(report_format=conf.param['report_format'])
        report_path = os.path.join(conf.param['data_folder'], report_name)
        dc.report.report_to_file(out_file_name=report_path)  # export results to file

        print('[+] File <{input_file}> report calculated, elapsed time: {elapsed_time}'.format(
            input_file=dc.report.current_file_name,
            elapsed_time=time.process_time() - t))

        dc.clean_report()


if __name__ == "__main__":
    main()
