from ishell.command import Command
from lib import my_console

# 查看命令帮助
class HelpCommand(Command):
    def run(self, line):
        my_console.print_childs_help()