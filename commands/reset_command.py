from .key import write_key 
from ishell.command import Command

class ResetCommand(Command):
    def run(self, line):
        write_key()
