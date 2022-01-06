import os
import sys
import time

from ishell.console import Console
from ishell.command import Command
import boto3


class MyConsole(Console):
    def print_childs_help(self):
        print("Help:")
        for command_name in self.childs.keys():
            print("%15s - %s" % (command_name, self.childs[command_name].help))


console = MyConsole(prompt="aws-key-tools", prompt_delim=">")
access_key = ""
secret_key = ""
current_arn = ""


# 初始化access_key 和 secret_key
class InitCommand(Command):
    def run(self, line):
        # 读取access_key 和 secret_key
        global access_key
        global secret_key
        access_key = input("access_key:")
        secret_key = input("secret_key:")
        # 将access_key 和 secret_key 写入配置文件
        # TODO 修改配置文件地址
        # 获取家目录
        home_path = os.path.expanduser("~")
        # 检查.aws 文件夹是否存在，不存在则创建

        if not os.path.exists(home_path + "/.aws"):
            os.mkdir(home_path + "/.aws")
        config_path = os.path.join(home_path, ".aws", "config")
        # [default]
        # aws_access_key_id=foo
        # aws_secret_access_key=bar
        # aws_session_token=baz
        with open(config_path, mode="w", encoding="utf-8") as f:
            f.write("[default]\n")
            f.write("aws_access_key_id=" + access_key + "\n")
            f.write("aws_secret_access_key=" + secret_key + "\n")
        print("设置成功")


# 获取对应用户的信息
class UserInfoCommand(Command):
    def run(self, line):
        iam = boto3.resource('iam')
        current_user = iam.CurrentUser()
        global current_arn
        current_arn = current_user.arn
        print("\nUserInfo:")
        print("\tarn:\t\t\t", current_user.arn)
        print("\tuser_id:\t\t", current_user.user_id)
        print("\tcurrent_user:\t\t", current_user.user_name)
        print("\tcreate_date:\t\t", current_user.create_date)
        print("\tpath:\t\t\t", current_user.path)
        print("\tpermissions_boundary:\t", current_user.permissions_boundary)
        print("\ttags:\t\t\t", current_user.tags)
        print("\tpassword_last_used:\t", current_user.password_last_used)
        access_key_iterator = current_user.access_keys.all()
        for access_key in access_key_iterator:
            print("\taccess_key:\t\t", access_key.id)
        print()


# 获取key对应的用户权限
class UserPrivilegesCommand(Command):
    def run(self, line):
        iam = boto3.resource('iam')
        # arn = iam.CurrentUser().arn if current_arn == "" else current_arn
        # print(arn)
        # arn="iam::455720863430:user/derian"
        policy = iam.Policy("arn")
        print("UserPrivileges:")
        print("\tattachment_count:\t", policy.attachment_count)
        print("\tcreate_date:\t\t", policy.create_date)
        print("\tdefault_version_id:\t", policy.default_version_id)
        print("\tdescription:\t\t", policy.description)
        print("\tis_attachable:\t\t", policy.is_attachable)
        print("\tpath:\t\t\t", policy.path)
        print("\tpermissions_boundary_usage_count:\t", policy.permissions_boundary_usage_count)
        print("\tpolicy_id:\t\t", policy.policy_id)
        print("\tpolicy_name:\t\t", policy.policy_name)
        print("\ttags:\t\t\t", policy.tags)
        print("\tupdate_date:\t\t", policy.update_date)

class Instance:
    pass

# 列出所有地区的ec2主机信息
class EC2InfoCommand(Command):
    def run(self, line):
        ec2 = boto3.client('ec2', region_name='us-east-1')
        response = ec2.describe_regions()  # 获取所有的地区 yes hhhh
        for region in response['Regions']:
            print("%s" % region['RegionName'])
            ec2 = boto3.client('ec2', region_name=region['RegionName'])
            response = ec2.describe_instances()
            # 判断是否有实例
            if len(response['Reservations']) == 0:
                print("\tNo instances")
                continue
            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    # 输出InstanceId、KeyName、PrivateIpAddress、PublicIpAddress、Architecture、IamInstanceProfile、RootDeviceName、PlatformDetails
                    print("\tInstanceId:\t\t%s" % instance['InstanceId'])
                    print("\tKeyName:\t\t%s" % instance['KeyName'])
                    print("\tPublicIpAddress:\t%s" % instance['PublicIpAddress'])
                    print("\tPrivateIpAddress:\t%s" % instance['PrivateIpAddress'])
                    print("\tIamInstanceProfile:\t%s" % instance['IamInstanceProfile']['Arn'])
                    # arn = iam.CurrentUser().arn if current_arn == "" else current_arn
                    PlatformDetails = instance.get("Platform") if instance.get("Platform") else instance.get(
                        "PlatformDetail")
                    print("\tPlatformDetails:\t%s" % PlatformDetails)
                    print("\tArchitecture:\t\t%s" % instance['Architecture'])
                    print("\tRootDeviceName:\t\t%s" % instance['RootDeviceName'])

                    print()


# 远程命令执行
class RemoteCommandExecute(Command):
    def run(self, line):
        # 用户输入 实例id 对应地区 操作系统 命令
        instance_id = 'i-08b14f120c367285d'
        region_name = 'us-west-1'
        document_name = 'AWS-RunShellScript'


        while 1:
            cmd = input('shell>').strip()
            if cmd == "exit":
                break

            ssm_client = boto3.client('ssm', region_name=region_name)
            response = ssm_client.send_command(
                InstanceIds=[instance_id, ],
                DocumentName=document_name,
                Parameters={'commands': [cmd]},
            )
            command_id = response['Command']['CommandId']

            # 等待命令的结束
            i = 0
            while 1:
                output = ssm_client.get_command_invocation(
                    CommandId=command_id,
                    InstanceId=instance_id,
                )
                if output.get("Status") == "Success" and output.get("StatusDetails") == "Success":
                    break
                i += 1
                time.sleep(i)
                if i > 3:
                    break

            # 输出命令执行的结果
            cmd_output = output.get("StandardOutputContent") + output.get("StandardErrorContent").strip()
            print(cmd_output)


# 创建IAM角色
class IAMRoleCommand(Command):
    def run(self, line):
        print("Showing all host info...")


# 根据ak生成aws控制台访问链接
class CreateAwsUrl(Command):
    def run(self, line):
        print("根据当前高权限生成一个aws控制台访问的url")


# 退出当前程序
class ExitCommand(Command):
    def run(self, line):
        sys.exit()


# 查看命令帮助
class HelpCommand(Command):

    def run(self, line):
        console.print_childs_help()


def main():
    help_command = HelpCommand("help", help="查看命令帮助")
    init_command = InitCommand("init", "初始化 access_key 和 secret_key")
    userinfo_command = UserInfoCommand("userinfo", help="获取用户信息")
    user_privileges_command = UserPrivilegesCommand("privileges",
                                                    help="获取用户权限")
    ec2_info_command = EC2InfoCommand("ec2info", help="获取所有地区的EC2（Elastic Computer Cloud）")
    remote_command_command = RemoteCommandExecute("exec", help="远程命令执行")
    iam_role_command = IAMRoleCommand("create-role", help="创建IAM角色")
    exit_command = ExitCommand("exit", help="退出程序")

    console.addChild(help_command)
    console.addChild(init_command)
    console.addChild(userinfo_command)
    console.addChild(user_privileges_command)
    console.addChild(ec2_info_command)
    console.addChild(remote_command_command)
    console.addChild(iam_role_command)
    console.addChild(exit_command)

    print("第一次运行工具，请务必先执行init命令, 然后才能执行其他命令")
    console.loop()


if __name__ == "__main__":
    main()
