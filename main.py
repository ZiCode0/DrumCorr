import glob
import os
from pathlib import Path
import re
import time

from lib.app import ConsoleApp
from lib.core import DrumCorr
from lib.files import file_parser
from lib.ztools import JsonConfig


def main():
    """
    Calculate cross-correlation for drum beats
    :return: Writes report file of cross-correlation function
    """

    ca = ConsoleApp()
    conf = JsonConfig(ca.args.config)
    dc = DrumCorr()

    dc.get_template(conf.param['template_file'])
    file_paths, file_names = file_parser(conf.param['data_folder'])
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
