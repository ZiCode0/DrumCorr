__project_name__ = 'DrumCorr'


class Console:
    start_init = 'Start program init..'
    program_start = 'Program {project_name} started.'.format(project_name=__project_name__)
    reading_template = 'Reading template from <{template}>..'
    process_loaded_files = 'Processing {count} files..'
    calc_file_finished = 'File <{input_file}> report calculated, elapsed time: {elapsed_time}'
    low_corr_warning = 'Correlation returns 0 or low ({res_num}) number of results for' \
                       '\nfile: <{file_name}>, quit..'
    experimental_enabled = 'Experimental futures enabled..'
    program_exit = 'Program {project_name} finished for folder <{project_folder}>, exit code {exit_code}'


class Report:
    mail_subject = '{project_name}: Error report'.format(project_name=__project_name__)


class Environment:
    init_body = 'GMAIL_LOGIN=""\nGMAIL_PASSWORD=""\nTELEGRAM_ID=""\nTELEGRAM_TOKEN=""'
