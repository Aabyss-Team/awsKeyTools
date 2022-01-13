from lib import my_console 
import commands

def banner():
    banner = """
                    __                   __                .__          
_____ __ _  _______|  | __ ____ ___.__._/  |_  ____   ____ |  |   ______
\__  \\ \/ \/ /  ___/  |/ // __ <   |  |\   __\/  _ \ /  _ \|  |  /  ___/
 / __ \\     /\___ \|    <\  ___/\___  | |  | (  <_> |  <_> )  |__\___ \ 
(____ /\/\_//____  >__|_  \\___  > ____| |__|  \____/ \____/|____/____  >
     \/          \/     \/    \/\/                                   \/ 
                                                     version : 0.0.1
                                                     by dbg9 and 无在无不在
"""
    print(banner)

def main():
    commands.read_key()
    # 初始化命令行控制台
    help_command = commands.HelpCommand("help", help="查看命令帮助")
    userinfo_command = commands.UserInfoCommand("userinfo", help="获取用户信息")
    user_privileges_command = commands.UserPrivilegesCommand("privileges",
                                                    help="获取用户权限",
                                                    dynamic_args=True)
    ec2_info_command = commands.EC2InfoCommand(
        "ec2", help="获取所有地区的EC2（Elastic Computer Cloud）")
    remote_command_command = commands.RemoteCommandExecute("exec", help="ec2远程命令执行")
    create_aws_url_command = commands.CreateAwsUrl("aws-url",
                                          help="根据当前高权限生成aws控制台访问url")
    reset_command = commands.ResetCommand("reset", help="重置aws_ak")
    exit_command = commands.ExitCommand("exit", help="退出程序")
    my_console.addChild(help_command)
    my_console.addChild(userinfo_command)
    my_console.addChild(user_privileges_command)
    my_console.addChild(ec2_info_command)
    my_console.addChild(remote_command_command)
    my_console.addChild(create_aws_url_command)
    my_console.addChild(reset_command)
    my_console.addChild(exit_command)
    my_console.loop()


if __name__ == "__main__":
    banner()
    main()