__project_name__ = 'DrumCorr'
__project_version__ = '1.2.1'


class Console:
    start_init = 'Start program init..'
    program_start = f'Program {__project_name__} v.{__project_version__} started.'
    reading_template = 'Reading template from <{template}>..'
    process_loaded_files = 'Processing {count} files..'
    calc_file_finished = 'File <{input_file}> report calculated, elapsed time: {elapsed_time}'
    low_corr_warning = 'Correlation returns 0 or low ({res_num}) number of results for' \
                       '\nfile: <{file_name}>, quit..'
    error_reading_file = 'Error reading file. Check file on gaps.'
    error_fdsn_connection = 'Failed to connect FDSN server: {server_url}. Stop parsing..'
    program_exit = 'Program {project_name} finished for folder <{project_folder}>, exit code {exit_code}'


class Report:
    mail_subject = '{project_name}: Error report'.format(project_name=__project_name__)


class Environment:
    init_body = 'GMAIL_LOGIN=""\nGMAIL_PASSWORD=""\nTELEGRAM_ID=""\nTELEGRAM_TOKEN=""'
