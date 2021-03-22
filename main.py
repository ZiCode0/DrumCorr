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
    Main program function
    """
    ca = ConsoleApp()  # console app instance
    conf = JsonConfig(ca.args.config)  # config instance
    logger_lib.init_logger(project_name=strings.__project_name__,
                           notify_providers=conf.param['notify'])  # init config
    logger.info(strings.Console.start_init)  # log: init program
    dc = DrumCorr()  # DrumCorr core instance
    if 'experimental' in conf.param:  # experimental future if enabled
        dc.experimental_futures(conf.param['experimental'])
    logger.info(strings.Console.program_start)  # log: start program

    template_path, file_paths = file_parser(conf)  # get files list

    logger.info(strings.Console.reading_template.format(
        template=os.path.basename(template_path)))  # log: read template
    template_object = dc.get_template(template_path)  # read template

    logger.info(strings.Console.process_loaded_files.format(
        count=len(file_paths)))  # log: info about loaded files
    for file_index in range(len(file_paths)):  # processing files
        t = time.process_time()  # start file processing timer

        file = file_paths[file_index]  # get file
        dc.workspace.current_file_name = os.path.basename(file_paths[file_index])  # file name to results
        dc.workspace.detection_value = conf.param['xcorr_detection_value']  # detection value for xcorr

        dc.workspace.stream = dc.read_file(file)  # get file content
        dc.transform_data(dc.workspace.stream)  # transform digital data to m/sec
        # run correlation detector
        dc.workspace.detects, dc.workspace.sims = dc.xcorr(data=dc.workspace.stream,
                                                           template=template_object,
                                                           detect_value=conf.param['xcorr_detection_value'])
        # skip file if correlation results is low
        if not dc.check_xcorr_results(template_minimum_count=conf.param['xcorr_minimum_count']):
            continue
        dc.workspace.approx_xcorr = dc.approx_xcorr(detections=dc.workspace.detects)  # calculate approximate corr
        # calculate correlation maximum of file
        dc.get_max_amplitudes()
        # generate report name
        report_name = dc.workspace.generate_report_name(report_format=conf.param['report_format'])
        # generate report file path
        report_path = os.path.join(conf.param['data_folder'], report_name)
        dc.workspace.report_to_file(out_file_name=report_path,
                                    experimental=dc.experimental)  # results to report file
        # log: file result
        logger.info(strings.Console.calc_file_finished.format(
            input_file=dc.workspace.current_file_name,
            elapsed_time=time.process_time() - t))
        dc.clean_report()  # clean report object
    # log: exit program
    logger.info(strings.Console.program_exit.format(project_name=strings.__project_name__,
                                                    project_folder=conf.param['data_folder'],
                                                    exit_code=1))


if __name__ == "__main__":
    main()
