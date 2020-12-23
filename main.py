import os
import time

from loguru import logger

import lib.logger as logger_lib
from lib import strings
from lib.app import ConsoleApp
from lib.core import DrumCorr
from lib.files import file_parser
from lib.ztools import JsonConfig


@logger.catch
def main():
    """
    Calculate auto-correlation for drumbeats
    :return: Writes report file of auto-correlation function
    """
    ca = ConsoleApp()
    logger_lib.init_logger(strings.__project_name__)
    logger.info(strings.Console.start_init)
    conf = JsonConfig(ca.args.config)
    dc = DrumCorr()
    logger.info(strings.Console.program_start)
    logger.info(strings.Console.reading_template.format(
        template=conf.param['template_file']))
    dc.get_template(conf.param['template_file'])
    file_paths, file_names = file_parser(conf.param['data_folder'])
    logger.info(strings.Console.process_loaded_files.format(
        count=len(file_names)))
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
        report_name = dc.report.generate_report_name(report_format=conf.param['report_format'])
        report_path = os.path.join(conf.param['data_folder'], report_name)
        dc.report.report_to_file(out_file_name=report_path)  # export results to file
        logger.info(strings.Console.calc_file_finished.format(
            input_file=dc.report.current_file_name,
            elapsed_time=time.process_time() - t))

        dc.clean_report()


if __name__ == "__main__":
    main()
