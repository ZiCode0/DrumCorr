import numpy as np

from obspy.signal.trigger import delayed_sta_lta, plot_trigger
from obspy import Stream

from lib.trace import add_zeros


def calc_average_sta_range(stream, detects, trim_before, trim_after, average_count=20):
    """
    Using average value of stalta functions to detect maximum of each event in detect list.
    :param stream: target stream
    :param trim_after:
    :param trim_before:
    :param average_count: count of detect
    :param detects:
    :return:
    """
    wave_before = trim_before
    wave_after = trim_after
    detect_trace_parts = []
    detect_trace_parts_sta = None

    # check count of detects is more than average count value
    if len(detects) < average_count:
        # low average count if low count of detects
        average_count = len(detects)

    # slice parts. count equal
    for detect_index in range(len(detects[:average_count])):
        start_detection = detects[detect_index]['time']
        v = stream.slice(start_detection - wave_before,
                         start_detection + wave_after)
        detect_trace_parts.append(v[0])
        # df = trace.stats.sampling_rate

    # equating first trace length to the second. Add zeros to the beginning
    detect_trace_parts = equate_trace_length(traces_array=detect_trace_parts,
                                             window_length=wave_before + wave_after)

    # make stalta on sliced parts
    for trace in detect_trace_parts:
        df = trace.stats.sampling_rate
        cft_d = delayed_sta_lta(trace.data, int(1 * df), int(4 * df))
        if detect_trace_parts_sta is not None:
            detect_trace_parts_sta += cft_d
        else:
            detect_trace_parts_sta = cft_d

    # calc average and normalize
    average_sta = detect_trace_parts_sta / average_count
    average_sta = average_sta / np.linalg.norm(average_sta)

    # time in seconds to slice it from the beginning
    appendix_divide_part = 3
    appendix_part_trace_time = round((detect_trace_parts[0].stats.endtime - detect_trace_parts[0].stats.starttime) /
                                     appendix_divide_part)

    trace_arr = []
    # trim traces, remove unnecessary stalta beginning (named "appendix")
    for detect_index in range(len(detects)):
        start_detection = detects[detect_index]['time']

        # add zeros tale of data to the left part
        sd_minus_wb = start_detection - wave_before
        delta = stream[0].stats.starttime - sd_minus_wb
        if delta > 0:  # if start detection before stream start time
            delta_samples = int(delta * stream[0].stats.sampling_rate)
            stream[0] = add_zeros.trace_add_to_left(trace=stream[0],
                                                    zeros_sample_count=delta_samples)

        v = stream.slice(start_detection - wave_before,
                         start_detection + wave_after)
        v.trim(v[0].stats.starttime + appendix_part_trace_time,
               v[0].stats.endtime)
        trace_arr.append(v)

    # fill first trace with zeros at the beginning if low
    delta = trace_arr[1][0].data.size - trace_arr[0][0].data.size
    trace = add_zeros.trace_add_to_left(trace=trace_arr[0][0],
                                        zeros_sample_count=delta)
    trace_arr[0] = Stream(traces=[trace])

    # trim beginning of stalta (named "appendix")
    sampling_rate = int(detect_trace_parts[0].stats.sampling_rate)
    average_sta = average_sta[appendix_part_trace_time * sampling_rate:]
    '''
    # # enable for #debug
    #
    test_trace = detect_trace_parts[0].slice(detect_trace_parts[0].stats.starttime + appendix_part_trace_time,
                                             detect_trace_parts[0].stats.endtime)
    plot_trigger(test_trace, average_sta, 0.02, 0.00001)  # enable for #debug
    #
    # #
    '''
    result_average_stalta = {'average_stalta_function': average_sta,
                             'streams': trace_arr}

    return result_average_stalta


def calc_max_stalta_index(stalta_function):
    """
    Return maximum index of stalta function
    :param stalta_function: target stalta function
    :return: index of maximum value :type int
    """
    max_value = np.max(stalta_function)
    sl_max_index = (np.where(stalta_function == max_value))[0][0]
    return sl_max_index


def return_sliced_traces_with_max(streams, maximum_index, range_len=4):
    """
    Returns array of trimmed traces according to maximum
    :param maximum_index: index of maximum. Middle point of result trimmed areas
    :param streams: target traces
    :param range_len: length of result traces in seconds. Must be even value.
    :return:
    """
    window_part = int(range_len / 2)
    res_traces = []
    for stream in streams:
        middle_max_time = int(maximum_index / 128)
        start_time = (stream[0].stats.starttime + middle_max_time) - window_part
        end_time = (stream[0].stats.starttime + middle_max_time) + window_part
        v = stream.slice(start_time, end_time)
        res_traces.append(v)
        # trace.plot()  # enable for #debug
        # v.plot()  # enable for #debug
        # print()  # enable for #debug
    return res_traces


def return_trace_max_dict(streams):
    result_array = []
    for stream in streams:
        if stream.traces:  # skip stream with empty traces
            max_value = np.max(stream[0].data)
            max_index = (np.where(stream[0].data == max_value))[0][0]
            max_time = stream[0].stats.starttime + max_index / stream[0].stats.sampling_rate
            result_array.append({'max_amplitude': max_value,
                                 'max_amplitude_time': max_time})
    return result_array


def debug_max_finding(detects):
    """
    Make test to find delta between signal detection and maximum
    :param detects: target detection list
    :return:
    """
    for detect in detects:
        delta = detect['max_amplitude_time'] - detect['time']
        print('{t1}\t{t2}\t{dlt}'.format(t1=detect['time'],
                                         t2=detect['max_amplitude_time'],
                                         dlt=delta)
              )


def equate_trace_length(traces_array, window_length):
    """
    Make traces length equal by size. Add zeros to the left.
    :return: trace_array
    """
    # max samples by window_length
    input_sample_len = window_length * traces_array[0].stats.sampling_rate
    # define that window length is about +-2 then window maximum from array traces
    real_sample_len = max([i.data.size for i in traces_array])
    # if input window length is less then real => overwrite
    if (input_sample_len + 1 >= real_sample_len) \
            and (input_sample_len - 1 <= real_sample_len):
        input_sample_len = real_sample_len

    # parse all traces to input sample length
    for trace_index in range(len(traces_array)):
        if traces_array[trace_index].data.size < input_sample_len:
            delta = input_sample_len - traces_array[trace_index].data.size
            traces_array[trace_index] = add_zeros.trace_add_to_left(trace=traces_array[trace_index],
                                                                    zeros_sample_count=delta)

    return traces_array
