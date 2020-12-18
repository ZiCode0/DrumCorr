__project_name__ = 'DrumCorr'


class Console:
    start_init = 'Start program init..'
    program_start = 'Program {project_name} started.'.format(project_name=__project_name__)
    reading_template = 'Reading template from <{template}>..'
    process_loaded_files = 'Processing {count} files in progress'
    calc_file_finished = 'File <{input_file}> report calculated, elapsed time: {elapsed_time}'


class Report:
    mail_subject = '{project_name}: Error report'.format(project_name=__project_name__)
