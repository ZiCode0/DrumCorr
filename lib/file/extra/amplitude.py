import datetime


def return_micron_to_seconds(input_amp):
    """
    Return value in micron/seconds format
    :param input_amp:
    :return:
    """
    visual_multiplier = 1000000  # 1 000 000
    return round(input_amp * visual_multiplier, 4)


def average_amplitude(detects):
    """
    Calculate average amplitude value
    :param detects:
    :return:
    """
    return sum([i['max_amplitude'] for i in detects]) / len(detects)


def average_delta_time(detects):
    times = [i['max_amplitude_time'] for i in detects]
    deltas = []
    # calculate deltas list
    for time_index in range(len(times)-1):
        deltas.append(times[time_index+1].datetime - times[time_index].datetime)
    # calculate average deltas
    average_delta = sum(deltas, datetime.timedelta(0)) / len(deltas)
    return average_delta
