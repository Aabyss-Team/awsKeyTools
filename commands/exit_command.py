import sys 
from ishell.command import Command

class ExitCommand(Command):
    def run(self, line):
        sys.exit()

