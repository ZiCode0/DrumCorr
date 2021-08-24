import copy
import os

from notifiers.logging import NotificationHandler
from read_env import read_env

from lib import strings


class LocalEnvironment:
    def __init__(self):
        """
        Local Environment instance to store local system variables
        """
        try:
            read_env()
        except FileNotFoundError:
            open('.env', 'w').write(strings.Environment.init_body)
            read_env()
        finally:
            self.vars = {'mail_login': os.environ["GMAIL_LOGIN"],
                         'mail_pass': os.environ["GMAIL_PASSWORD"],
                         'mail_to': 'zedcode.05@gmail.com',
                         'tg_token': os.environ["TELEGRAM_TOKEN"],
                         'tg_id': os.environ["TELEGRAM_ID"]}


local_env = LocalEnvironment()


class TelegramNotificationHandler(NotificationHandler):
    def __init__(self, provider: str, **kwargs):
        super().__init__(provider, **kwargs)
        self.head_message = '<b> HELLO </b>'

    def emit(self, record):
        """
        Custom overrider of the :meth:`~logging.Handler.emit` method
        that takes the ``msg`` attribute from the log record passed
        :param record: :class:`logging.LogRecord`
        """
        record.msg = self.head_message + record.msg

        data = copy.deepcopy(self.defaults)
        data["message"] = self.format(record)
        try:
            self.provider.notify(raise_on_errors=True, **data)
        except Exception:
            self.handleError(record)


class AltTelegramNotificationHandler(NotificationHandler):
    def __init__(self, provider: str, **kwargs):
        super().__init__(provider, **kwargs)
        self.head_message = '<b> HELLO </b>'

    def emit(self, record):
        """
        Custom overrider of the :meth:`~logging.Handler.emit` method
        that takes the ``msg`` attribute from the log record passed
        :param record: :class:`logging.LogRecord`
        """
        tg_emit(head=self.head_message)


def tg_emit(head):
    """
    Decorator to edit message for telegram/mail
    :return:
    """
    def wrapper_function(*args, **kwargs):
        args[1].msg += head
        NotificationHandler.emit(*args, **kwargs)
        # bla-bla
    return wrapper_function


class Providers:
    def __init__(self):
        """
        Notification providers for sending error reports
        """
        self.notify_providers = {'gmail': self.gmail_sender,
                                 'telegram': self.telegram_sender}

    def add(self, arg, args):
        return self.notify_providers[arg](args)

    @staticmethod
    def gmail_sender(logger):
        params = {
            "username": local_env.vars.get('mail_login'),
            "password": local_env.vars.get('mail_pass'),
            "to": local_env.vars.get('mail_to'),
            "subject": strings.Report.mail_subject
        }
        handler = NotificationHandler("gmail", defaults=params)
        logger.add(handler, level="ERROR")
        return logger

    @staticmethod
    def telegram_sender(logger):
        params = {
            "chat_id": local_env.vars.get('tg_id'),
            "token": local_env.vars.get('tg_token'),
            "message": 'test'
        }
        handler = AltTelegramNotificationHandler("telegram", defaults=params)
        logger.add(handler, level="ERROR")
        return logger
