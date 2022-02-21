import os
import time

from loguru import logger

from lib import strings
from lib.log import logger as logger_lib
from lib.app import ConsoleApp
from lib.core import DrumCorr
from lib.config import JsonConfig
from lib.core import StreamReader
from lib.file.parser import file_parser

from lib.file.reader import DCErrorReadingFile
from lib.file.response import DCErrorFDSNConnectionFail


@logger.catch
def main():
    """
    Main program function
    """
    try:
        # console app instance
        ca = ConsoleApp()
        # file reader instance
        sr = StreamReader()
        # config instance
        conf = JsonConfig(ca.args.config)
        # init logger
        logger_lib.init_logger(project_name=strings.__project_name__,
                               notify_providers=conf.param['notify'])
        # log: init program
        logger.info(strings.Console.start_init)
        # DrumCorr instance
        dc = DrumCorr()
        # log: start program
        logger.info(strings.Console.program_start)
        # get files list
        _template_path, _file_paths = file_parser(conf)
        # log: read template
        logger.info(strings.Console.reading_template.format(
            template=os.path.basename(_template_path)))
        # read template
        t_template_stream = dc.read_file(path=_template_path)
        # apply instrumental correction to template file
        dc.remove_response(stream=t_template_stream,
                           fdsn_url=conf.param['fdsn_server_url'])
        # filter template
        dc.filter_data(t_template_stream,  # data
                       conf.param['filter']['filter_name'],  # filter name
                       **conf.param['filter']['filter_params'])  # filter parameters
        # log: info about loaded files
        logger.info(strings.Console.process_loaded_files.format(
            count=len(_file_paths)))
        # processing files
        for file_index in range(len(_file_paths)):
            try:
                # start file processing timer
                _timer_start = time.process_time()
                # get file
                _file_path = _file_paths[file_index]
                # file name to results
                dc.workspace.current_file_name = os.path.basename(_file_paths[file_index])
                # detection value for xcorr
                dc.workspace.detection_value = conf.param['xcorr_detection_value']
                # get file content
                dc.workspace.stream = dc.read_file(_file_path)
                # apply instrumental correction to input file
                dc.remove_response(stream=dc.workspace.stream,
                                   fdsn_url=conf.param['fdsn_server_url'])
                # filter input file data
                dc.filter_data(dc.workspace.stream,
                               conf.param['filter']['filter_name'],
                               **conf.param['filter']['filter_params'])
                # run correlation detector
                dc.workspace.detects, dc.workspace.sims = dc.xcorr(data=dc.workspace.stream,
                                                                   template=t_template_stream,
                                                                   detect_value=conf.param['xcorr_detection_value'])
                # skip file if correlation results is low
                if not dc.check_xcorr_results(template_minimum_count=conf.param['xcorr_minimum_count']):
                    continue
                # calculate approximate corr
                dc.workspace.approx_xcorr = dc.approx_xcorr(detections=dc.workspace.detects)
                # calculate correlation maximum of file
                dc.get_max_amplitudes()
                # generate report name
                _report_name = dc.workspace.generate_report_name(report_format=conf.param['report_format'])
                # generate report file path
                _report_path = os.path.join(conf.param['data_folder'], _report_name)
                dc.workspace.report_to_file(out_file_name=_report_path)  # results to report file
                # log: file result
                logger.info(strings.Console.calc_file_finished.format(
                    input_file=dc.workspace.current_file_name,
                    elapsed_time=time.process_time() - _timer_start))
                # clean report object
                dc.clean_report()

            # skip error reading file
            # # check file on gaps
            except DCErrorReadingFile as ex:
                logger.warning(ex)
                continue

        # log: exit program
        logger.info(strings.Console.program_exit.format(project_name=strings.__project_name__,
                                                        project_folder=conf.param['data_folder'],
                                                        exit_code=1))

    # # check fdsn connection
    except DCErrorFDSNConnectionFail as ex:
        logger.warning(ex)
        quit()


if __name__ == "__main__":
    main()
