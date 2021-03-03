import math
import numpy as np
from loguru import logger

from obspy.signal.cross_correlation import correlation_detector
from obspy.signal.trigger import recursive_sta_lta

from lib import strings
from lib.reader import StreamReader
from lib.workspace import Workspace
from lib.extra import calibration


class DrumCorr:
    def __init__(self):
        """
        Main program core.
        Calculates the correlation based on the ratio of the pattern and the sliding window
        """
        self.workspace = Workspace(self.get_value_by_utc_time)
        self.corr_step = 0.1
        self.wave_len = 1  # wave len in seconds
        self.experimental = 0  # enable experimental futures

    def experimental_futures(self, experimental_flag):
        """
        Set experimental future by config
        :param experimental_flag: int(0,1)
        """
        self.experimental = experimental_flag
        if self.experimental:
            logger.warning(strings.Console.experimental_enabled)  # log: start program

    def clean_report(self):
        self.workspace = Workspace(self.get_value_by_utc_time)

    @staticmethod
    def filter_data(data, filter_name, filter_params):
        """
        Filter function
        :type data: target stream data
        :param filter_name: filter name. Default: bandpass
        :param filter_params: input filter parameters
        :return: filtered <obspy.core.stream.Stream>
        """
        if filter_name == 'bandpass':
            filtered_data = data.filter(filter_name,
                                        freqmin=float(filter_params[0]),
                                        freqmax=float(filter_params[0]))
            return filtered_data

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

    def xcorr(self, data, template, detect_value=0.5):
        # pass_step = 0.1  # pass step in seconds

        # samples / seconds
        # 128 s     1 sec
        #  64 s   0.5 sec
        #  32 s  0.25 sec +
        #  16 s 0.125 sec

        detections, sims = correlation_detector(stream=data,
                                                templates=template,
                                                heights=detect_value,
                                                distance=self.corr_step,
                                                plot=None)
        if len(detections) != 0:
            # exclude self correlation
            detections = [v for v in detections if v['similarity'] < 0.999]
            # del detections[0]
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

        if self.experimental == 0:
            """
            OLD VERSION OF CODE USING OBSPY FUNCTIONS
            CAUSES PYTHON MEMORY ERROR WHILE CALCULATING BIG DATA
            """
            if self.workspace.times is not None:
                index = self.workspace.times.searchsorted(utc_time)
                result_value = stream[trace_index].data[index]
                return result_value
            else:
                self.workspace.times = stream[trace_index].times('utcdatetime')
                index = self.workspace.times.searchsorted(utc_time)
                result_value = stream[trace_index].data[index]
                return result_value

        elif self.experimental == 1:
            """
            ALTERNATIVE METHOD TO SELECTING STREAM VALUE
            Direct addressing to values
            """
            target_index = math.ceil((utc_time - stream[0].meta.starttime) / stream[0].meta.delta)
            result_value = stream[0].data[target_index]
            return result_value

        elif function_method == 2:
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
        if len(self.workspace.detects) > template_minimum_count:
            return 1
        else:
            logger.warning(strings.Console.low_corr_warning.format(res_num=len(self.report.detects),
                                                                   file_name=self.report.current_file_name))
            return 0

    def get_max_amplitudes(self, trim_before=10, trim_after=20, trigger_start=1.0, trigger_stop=0.9):
        """
        Get high max amplitude values according to wave length
        :param trim_before:
        :param trim_after:
        :param trigger_start:
        :param trigger_stop:
        """
        wave_before = trim_before
        wave_after = trim_after
        trigger_start_detect_value = trigger_start
        trigger_stop_detect_value = trigger_stop
        amp_multi = self.workspace.v['calibrations'].v['amplitude_multiplier']

        for detect_index in range(len(self.workspace.detects)):
            start_detection = self.workspace.detects[detect_index]['time']
            v = self.workspace.stream.slice(start_detection - wave_before,
                                            start_detection + wave_after)
            trace = v[0]
            df = trace.stats.sampling_rate
            # out_file_name = self.report.current_file_name + '-' + str(detect_index) + '.mseed'
            # trace.write(out_file_name, format="MSEED")  # uncomment for #debug

            # sta lta detector
            cft = recursive_sta_lta(trace.data, int(5 * df), int(10 * df))
            # plot_trigger(trace, cft, 1.0, 0.9)  # uncomment for #debug
            # print()  # uncomment for #debug

            # temp trigger index vars
            trigger_start_index = None
            trigger_stop_index = None

            # found start and stop indexes of trigger detector
            for index in range(trace.data.size):
                if not trigger_start_index:
                    # write index on start of detector
                    if cft[index] >= trigger_start_detect_value:
                        trigger_start_index = index
                elif not trigger_stop_index:
                    # write index on stop of detector
                    if cft[index] <= trigger_stop_detect_value:
                        trigger_stop_index = index
                else:
                    break

            # write index stop trigger as the end of trace
            if not trigger_stop_index:
                trigger_stop_index = trace.data.size - 1

            # trim current trace data
            trace.trim(trace.meta.starttime + trigger_start_index / df,
                       trace.meta.starttime + trigger_stop_index / df)

            # write zero maximum amplitude and time on detector fail
            if trace.data.size == 0:
                self.workspace.detects[detect_index]['max_amplitude'] = 0
                self.workspace.detects[detect_index]['max_amplitude_time'] = 0

            # calc and write maximum for selected trace
            else:
                # find absolute maximum amplitude in the trace with time of it
                # trace.data.max()
                max_amp_value = trace.data[0]
                max_amp_index = 0
                for value_index in range(len(trace.data)):
                    if trace.data[value_index] > max_amp_value:
                        max_amp_value = trace.data[value_index]
                        max_amp_index = value_index
                max_amp_time = trace.meta.starttime + max_amp_index / 128

                # why 1 000 000 ??
                # visual_multiplier = 1000000
                self.workspace.detects[detect_index]['max_amplitude'] = max_amp_value

                self.workspace.detects[detect_index]['max_amplitude_time'] = max_amp_time
            # print()  # uncomment for #debug

    def transform_data(self, stream):
        # multi = 0.3519690e+08
        multi = (1, self.workspace.v['calibrations']
                 .v['amplitude_multiplier'])[self.workspace.v['calibrations']
                                                      .v['amplitude_multiplier'] is not None]
        # stream[0].data = []
        # #bug: amp
        stream[0].data = np.array([i / multi for i in stream[0].data.tolist()])
        return stream

    def read_file(self, file):
        sr = StreamReader()
        file, chars = sr.read(input_filename=file)
        # get characteristic
        self.workspace.v['chars'] = chars
        try:
            self.workspace.v['calibrations'] = calibration.Calibrations(self.workspace.v['chars'])
        except:
            pass
        return file
        # update multiplier for selected file if possible
        # self.transfer_d
