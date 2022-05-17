import argparse

from lib import strings


class ConsoleApp:
    def __init__(self):
        """
        Initial console app function
        """
        self.app_name = strings.__project_name__
        self.app_version = strings.__project_version__
        self.author = 'ZiCode0'
        self.contacts = '[Telegram] @MrFantomz'
        self.args = None

        # define program description
        text = f'{self.app_name} by {self.author} v.{self.app_version}\nContacts: {self.contacts}'

        # initiate the parser with a description
        parser = argparse.ArgumentParser(description=text)
        parser.add_argument("-v", "--version", help="show program version", action="store_true")
        parser.add_argument("-c", '--config', help="specify path to target config json file")
        self.args = parser.parse_args()
        if self.args.version:
            print(self.app_version)
            quit(0)
        elif (not self.args.config) and (not self.args.version):
            parser.print_help()
            quit(0)
