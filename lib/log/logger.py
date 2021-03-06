from loguru import logger

from lib.log import notify


def init_logger(project_name, notify_providers=None, log_level='DEBUG'):
    """
    Logger for program.
    Use providers to add report errors.
    :type project_name: name of current program
    :param notify_providers: list of notification providers if needed
    :type log_level: log level to filter output
    """
    # set log format
    logger.add('{project_name}.log'.format(project_name=project_name),
               format='{time:!UTC} {level} {message}',
               level=log_level,
               rotation='1 MB',
               compression='zip')
    # add report providers
    if notify_providers:
        providers = notify.Providers()
        for p in notify_providers:
            providers.add(p, logger)
