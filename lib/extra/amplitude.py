def return_micron_to_seconds(input_amp):
    """
    Return value in micron/seconds format
    :param input_amp:
    :return:
    """
    visual_multiplier = 1000000  # 1 000 000
    return round(input_amp * visual_multiplier, 4)
