from ishell.console import Console

class MyConsole(Console):
    def print_childs_help(self):
        print("Help:")
        for command_name in self.childs.keys():
            print("%15s - %s" % (command_name, self.childs[command_name].help))


# 可以把read_key 加载MyConsole 的构造函数中
my_console = MyConsole(prompt="aws-key-tools", prompt_delim=" >")