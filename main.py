import os
import sys
import time

from ishell.console import Console
from ishell.command import Command
import boto3
from enumerate_iam.main import enumerate_iam
from  aws_consoler.cli import api 


class MyConsole(Console):
    def print_childs_help(self):
        print("Help:")
        for command_name in self.childs.keys():
            print("%15s - %s" % (command_name, self.childs[command_name].help))

# 可以把read_key 加载MyConsole 的构造函数中

console = MyConsole(prompt="aws-key-tools", prompt_delim=" >")
access_key = ""
secret_key = ""
current_arn = ""
ec2_lst = []


def read_key():
    """读取文件中的key"""
    global access_key
    global secret_key
    # 先检查全局变量的值 
    if access_key and secret_key:
        return access_key, secret_key
    home_path = os.path.expanduser("~")
    config_path = os.path.join(home_path, ".aws", "config")
    # 如果存在配置文件,则读取配置文件
    if os.path.exists(config_path):
        with open(config_path, mode="r", encoding="utf-8") as f:
            for line in f.readlines():
                if line.startswith("aws_access_key_id"):
                    access_key = line.split("=")[1].strip()
                if line.startswith("aws_secret_access_key"):
                    secret_key = line.split("=")[1].strip()
    else:
        #提示用户输入
        access_key = input("access_key:").strip()
        secret_key = input("secret_key:").strip()
        # 将access_key 和 secret_key 写入配置文件
        # 检查.aws 文件夹是否存在，不存在则创建,这个目录得检查一下呀
        if not os.path.exists(home_path + "/.aws"):
            os.mkdir(home_path + "/.aws")
        with open(config_path, mode="w", encoding="utf-8") as f:
            f.write("[default]\n")
            f.write("aws_access_key_id=" + access_key + "\n")
            f.write("aws_secret_access_key=" + secret_key + "\n") 
    return access_key, secret_key



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
        enumerate_iam(access_key=access_key, secret_key=secret_key,session_token=None, region=None)




class EC2Instance:
    def __init__(self, id, region, instance_id, key_name, public_ip, private_ip, iam_instance_profile, platform_details,
                 architecture,
                 root_device):
        self.id = id
        self.region = region
        self.instance_id = instance_id
        self.key_name = key_name
        self.public_ip = public_ip
        self.private_ip = private_ip
        self.iam_instance_profile = iam_instance_profile
        self.platform_details = platform_details
        self.architecture = architecture
        self.root_device = root_device

    def info(self):
        print(f"id:\t\t\t{self.id}")
        print(f"Region:\t\t\t{self.region}")
        print(f"InstanceId:\t\t{self.instance_id}")
        print(f"KeyName:\t\t{self.key_name}")
        print(f"PublicIpAddress:\t{self.public_ip}")
        print(f"PrivateIpAddress:\t{self.private_ip}")
        print(f"IamInstanceProfile:\t{self.iam_instance_profile}")
        print(f"PlatformDetails:\t{self.platform_details}")
        print(f"Architecture:\t\t{self.architecture}")
        print(f"RootDeviceName:\t\t{self.root_device}")
        print()


# 列出所有地区的ec2主机信息
class EC2InfoCommand(Command):
    def show_ec2(self):
        for ec2 in ec2_lst:
            ec2.info()
        print(f"一共获取的ec2数量为：{len(ec2_lst)}")

    def run(self, line):
        print("ec2信息获取中...")
        if len(ec2_lst):
            self.show_ec2()
            return
        ec2 = boto3.client('ec2', region_name='us-east-1')
        response = ec2.describe_regions()  # 获取所有的地区 yes hhhh
        i = 1
        for region in response['Regions']:
            region_name = region['RegionName']
            ec2 = boto3.client('ec2', region_name=region_name)
            response = ec2.describe_instances()
            # 判断是否有实例
            if len(response['Reservations']) == 0:
                print(region_name)
                print("\tNo instances")
                continue
            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    # 实例化ec2对象
                    id = i
                    instance_id = instance.get("InstanceId")
                    key_name = instance.get("KeyName")
                    public_ip = instance.get("PublicIpAddress")
                    private_ip = instance.get("PrivateIpAddress")
                    iam_instance_profile = instance.get("IamInstanceProfile").get('Arn')
                    platform_details = instance.get("Platform") if instance.get("Platform") else instance.get(
                        "PlatformDetail")
                    architecture = instance.get("Architecture")
                    root_device = instance.get("RootDeviceName")
                    ec2_obj = EC2Instance(id, region_name, instance_id, key_name, public_ip, private_ip,
                                          iam_instance_profile,
                                          platform_details, architecture, root_device)
                    ec2_lst.append(ec2_obj)
                    i += 1
        self.show_ec2()


# 远程命令执行
class RemoteCommandExecute(Command):
    platform_dic = {
        "linux": "AWS-RunShellScript",
        "windows": "AWS-RunPowerShellScript",
    }

    def run(self, line):
        while 1:
            # 用户输入 实例id 对应地区 操作系统 命令
            id = input("请输入ec2的id: ").strip()
            if int(id) > len(ec2_lst):
                print("请输入正确的ec2 id")
                continue
            ec2 = ec2_lst[int(id) - 1]
            instance_id = ec2.instance_id
            region_name = ec2.region
            document_name = self.platform_dic.get(ec2.platform_details)
            if not document_name:
                platform_details = input("无法获取ec2对应平台信息，请手动输入: ").strip()
                document_name = self.platform_dic.get(platform_details)
            while 1:
                cmd = input('shell>').strip()
                if cmd == "exit":
                    return

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
        print("根据当前权限生成一个aws控制台访问的url") #可以的，只要修改本地包就好了，这个就是args[]
        api(access_key=access_key, secret_key=secret_key)
        
# 我先测一下哈

# 退出当前程序
class ExitCommand(Command):
    def run(self, line):
        sys.exit()


# 查看命令帮助
class HelpCommand(Command):

    def run(self, line):
        console.print_childs_help()


def main():
    global access_key,secret_key
    access_key,secret_key = read_key() 
    # 初始化命令行控制台
    help_command = HelpCommand("help", help="查看命令帮助")
    userinfo_command = UserInfoCommand("userinfo", help="获取用户信息")
    user_privileges_command = UserPrivilegesCommand("privileges",
                                                    help="获取用户权限")
    ec2_info_command = EC2InfoCommand("ec2", help="获取所有地区的EC2（Elastic Computer Cloud）") 
    remote_command_command = RemoteCommandExecute("exec", help="远程命令执行")
    iam_role_command = IAMRoleCommand("create-role", help="创建IAM角色")
    create_aws_url_command = CreateAwsUrl("aws-url", help="根据当前高权限生成一个aws控制台访问的url")
    exit_command = ExitCommand("exit", help="退出程序")

    console.addChild(help_command)
    console.addChild(userinfo_command)
    console.addChild(user_privileges_command)
    console.addChild(ec2_info_command)
    console.addChild(remote_command_command)
    console.addChild(iam_role_command)
    console.addChild(create_aws_url_command)
    console.addChild(exit_command)
    console.loop()


if __name__ == "__main__":
    main()
