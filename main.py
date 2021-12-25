from ishell.console import Console
from ishell.command import Command
console = Console(prompt="aws-key-tools ", prompt_delim=">")
## 获取对应用户的信息
class UserInfoCommand(Command):
    def run(self, line):
        print("Showing all userinfo...")
## 获取key对应的用户权限
class UserPrivilegesCommand(Command):
    def run(self, line):
        print("Showing privileges for user...")
## 列出所有地区的ec2主机信息
class EC2InfoCommand(Command):
    def run(self, line):
        print("Showing all hostinfo...")
## 远程命令执行
class RemoteCommandCommand(Command):
    def run(self, line):
        print("Showing all hostinfo...")
## 创建IAM角色
class IAMRoleCommand(Command):
    def run(self, line):
        print("Showing all hostinfo...")

def main():       
    userinfo_command = UserInfoCommand("userinfo", help="获取用户信息")
    user_privileges_command= UserPrivilegesCommand("privileges", help="获取用户权限")
    ec2_info_command = EC2InfoCommand("ec2info", help="获取ec2信息")
    remote_command_command = RemoteCommandCommand("remote", help="远程命令执行")
    iam_role_command = IAMRoleCommand("create-role", help="创建IAM角色")
    console.addChild(userinfo_command)
    console.addChild(user_privileges_command)
    console.addChild(ec2_info_command)
    console.addChild(remote_command_command)
    console.addChild(iam_role_command)
    console.loop()

if __name__ == "__main__":
    main()