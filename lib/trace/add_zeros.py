import numpy as np

from lib.file.reader import StreamReader
from lib.file.reader import NewInputData


def trace_to_left(trace, zeros_sample_count):
    """
    Add zeros at the beginning of trace with selected zeros count
    :param trace: target trace
    :param zeros_sample_count: zeros count to add to the left of trace
    :return: modified trace
    """
    zero_tail = NewInputData()
    zero_tail.sampling_rate = trace.stats.sampling_rate
    zero_tail.station = trace.stats.station
    zero_tail.network = trace.stats.network
    zero_tail.channel = trace.stats.channel
    zero_tail.samples_count = zeros_sample_count
    zero_tail.start_time = trace.stats.starttime - zeros_sample_count / trace.stats.sampling_rate  # delta_start_utc
    zero_tail.data = np.zeros(int(zeros_sample_count))
    sr = StreamReader()
    zero_tail = sr.create_stream(zero_tail)[0]

    trace_result = zero_tail.__add__(trace=trace,
                                     method=1,
                                     interpolation_samples=0)
    # trace_result.plot()  # enable for #debug
    return trace_result
