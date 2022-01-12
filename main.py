import os
import sys
import time
import json
from pprint import pprint

from ishell.console import Console
from ishell.command import Command
import boto3
from enumerate_iam.main import enumerate_iam
from aws_consoler.cli import api


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
current_user = ""
ec2_lst = []

def write_key():
    """写入文件中的key"""
    home_path = os.path.expanduser("~")
    config_path = os.path.join(home_path, ".aws", "config")
    #提示用户输入
    global access_key
    global secret_key
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
        write_key()
    return access_key, secret_key


# 获取对应用户的信息
class UserInfoCommand(Command):
    def run(self, line):
        iam = boto3.resource('iam')
        global current_arn
        global current_user
        current_user = iam.CurrentUser()
        current_arn = current_user.arn
        print("\nUserInfo:")
        print("\tuser_id:\t\t", current_user.user_id)
        print("\tuser_name:\t\t", current_user.user_name)
        print("\tcreate_date:\t\t", current_user.create_date)
        print("\tarn:\t\t\t", current_user.arn)
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
        last_arg = line.strip().split()[-1]
        # 1.通过api的方式枚举，使用enum参数激活
        if last_arg == "enum":
            enumerate_iam(access_key=access_key, secret_key=secret_key, session_token=None, region=None)
        else:
            # 2.获取当前用户的aws托管策略和内嵌策略
            # 获取当前用户名
            try:
                user_name = current_user.user_name
            except Exception:
                print("请先使用 userinfo 获取当前用户，然后才能查看用户对应的权限")
                return
            # 获取当前用户的aws托管策略和内嵌策略
            # # 内嵌策略
            client = boto3.client('iam')
            attached_response = client.list_attached_user_policies(
                UserName=user_name,
                PathPrefix='/',
                MaxItems=123
            )
            attached_policy_lst = attached_response.get("AttachedPolicies")
            iam = boto3.resource('iam')
            # 如果托管策略存在，打印json
            for p_dic in attached_policy_lst:
                # 获取托管的策略版本
                arn = p_dic.get("PolicyArn")
                name = p_dic.get("PolicyName")
                policy = iam.Policy(arn)
                # 获取托管策略的版本
                v_id = policy.default_version_id
                policy_version = iam.PolicyVersion(arn, v_id)
                # 打印json
                document = json.dumps(policy_version.document, indent=2)
                print(f"aws托管策略: {name}\n{document}")

            # 内联策略
            response = client.list_user_policies(
                UserName=user_name,
            )
            policy_lst = response.get("PolicyNames")
            # 内敛策略的名称
            # print(policy_lst)
            for p in policy_lst:
                user_policy_response = client.get_user_policy(
                    UserName=user_name,
                    PolicyName=p
                )
                policy_document = json.dumps(user_policy_response.get("PolicyDocument"), indent=2)
                print(f"内联策略: {p}\n{policy_document}")


class EC2Instance:
    def __init__(self, id, region, instance_id, key_name, public_ip,
                 private_ip, iam_instance_profile_arn,
                 platform_details, architecture, root_device):
        self.id = id
        self.region = region
        self.instance_id = instance_id
        self.key_name = key_name
        self.public_ip = public_ip
        self.private_ip = private_ip
        self.iam_instance_profile_arn = iam_instance_profile_arn
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
        print(f"IamInstanceProfileArn:\t{self.iam_instance_profile_arn}")
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

                    iam_instance_profile = instance.get("IamInstanceProfile")
                    # 这个是None
                    iam_instance_profile_arn = iam_instance_profile.get(
                        'Arn') if iam_instance_profile else None
                    platform_details = instance.get("Platform") if instance.get("Platform") else instance.get(
                        "PlatformDetail")
                    architecture = instance.get("Architecture")
                    root_device = instance.get("RootDeviceName")
                    ec2_obj = EC2Instance(id, region_name, instance_id, key_name, public_ip, private_ip,
                                          iam_instance_profile_arn,
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

    def create_instance_profile(self):
        # 创建实例配置文件
        client = boto3.client('iam')
        # 创建policy ssm_policy
        with open("AmazonSSMManagedInstanceCore.json", mode="r", encoding="utf-8") as f:
            json2 = f.read()
        client.create_policy(
            PolicyName='ssm_policy',
            Path='/',
            PolicyDocument=json2,
        )

        # arn:aws:iam::455720863430:policy/ssm_policy

        # # 创建角色 AmazonSSMManagedInstance
        with open("ec2-role-trust-policy.json", mode="r", encoding="utf-8") as f:
            json1 = f.read()
        client.create_role(
            Path='/',
            RoleName='AmazonSSMManagedInstance',
            AssumeRolePolicyDocument=json1,
            Description='Allows EC2 instances to call AWS services on your behalf.',
        )

        # arn:aws:iam::455720863430:role/AmazonSSMManagedInstance

        # 给角色加policy
        with open("AmazonSSMManagedInstanceCore.json", mode="r", encoding="utf-8") as f:
            json2 = f.read()
        client.put_role_policy(
            RoleName='AmazonSSMManagedInstance',
            PolicyName='ssm_policy',
            PolicyDocument=json2
        )
        # 创建实力配置文件 arn:aws:iam::455720863430:instance-profile/SSMFullAccessProfile
        instance_profile_name = "SSMFullAccessProfile"
        response3 = client.create_instance_profile(
            InstanceProfileName=instance_profile_name)
        instance_profile_arn = response3.get("InstanceProfile").get("Arn")

        # 添加角色到实例配置文件
        client.add_role_to_instance_profile(
            InstanceProfileName=instance_profile_name,
            RoleName='AmazonSSMManagedInstance'
        )
        return instance_profile_arn, instance_profile_name

    def run(self, line):
        while 1:
            # 用户输入 实例id 对应地区 操作系统 命令
            if not ec2_lst:
                print("请先执行 ec2 命令获取ec2主机或当前key没有获取主机的权限")
                return
            id = input("请输入ec2的id: ").strip()
            try:
                ec2 = ec2_lst[int(id) - 1]
            except Exception:
                print("请输入正确的ec2 id")
                continue
            try:
                instance_id = ec2.instance_id
                region_name = ec2.region
            except Exception:
                print("请先使用 ec2 命令获取ec2主机信息，然后再来执行命令吧！")
                return
            document_name = self.platform_dic.get(ec2.platform_details)
            if not document_name:
                platform_details = input("无法获取ec2对应平台信息，请手动输入: ").strip()
                document_name = self.platform_dic.get(platform_details)
            # 检测ec2是否关联了实例配置文件
            if not ec2.iam_instance_profile_arn:
                print("检测到当前ec2主机未关联实例配置文件，正在尝试关联...")
                # 判断是否已经创建了实例配置文件
                # 获取实例配置文件
                client = boto3.client('iam')
                response = client.list_instance_profiles(
                    PathPrefix='/',
                    MaxItems=123
                )
                instance_profiles_lst = response.get("InstanceProfiles")
                for instance_profile in instance_profiles_lst:
                    name = instance_profile.get("InstanceProfileName")
                    if name == "SSMFullAccessProfile":
                        # 已经存在
                        instance_profile_name = name
                        instance_profile_arn = instance_profile.get("Arn")
                        print("检测到已经创建过实例配置文件，正在关联...")
                        break
                else:
                    # 不存在
                    print("检测到没有创建实例配置文件，正在创建实例配置文件...")
                    instance_profile_arn, instance_profile_name = self.create_instance_profile()

                client_ec2 = boto3.client('ec2', region_name=region_name)
                response = client_ec2.associate_iam_instance_profile(IamInstanceProfile={
                    'Arn': instance_profile_arn,
                    'Name': instance_profile_name,
                },
                    InstanceId=instance_id)
                if response.get("ResponseMetadata").get("HTTPStatusCode") == 200:
                    ec2.iam_instance_profile_arn = instance_profile_arn
                    print("实例配置文件添加成功 (ec2命令可以查看)，但是失效需要一定的等待时间，一般10分钟左右，请稍后再执行命令")
                    return
                else:
                    print("ec2实例配置文件关联失败")
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


# 根据ak生成aws控制台访问链接
class CreateAwsUrl(Command):
    def run(self, line):
        print("根据当前权限生成一个aws控制台访问的url")  # 可以的，只要修改本地包就好了，这个就是args[]
        api(access_key=access_key, secret_key=secret_key)


class ResetCommand(Command):
    def run(self, line):
        """写入文件中的key"""
        home_path = os.path.expanduser("~")
        config_path = os.path.join(home_path, ".aws", "config")
        # 提示用户输入
        global access_key
        global secret_key
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

        # 退出当前程序


class ExitCommand(Command):
    def run(self, line):
        sys.exit()


# 查看命令帮助
class HelpCommand(Command):
    def run(self, line):
        console.print_childs_help()

class ResetCommand(Command):
    def run(self,line):
        write_key()

def main():
    global access_key, secret_key
    access_key, secret_key = read_key()
    # 初始化命令行控制台
    help_command = HelpCommand("help", help="查看命令帮助")
    userinfo_command = UserInfoCommand("userinfo", help="获取用户信息")
    user_privileges_command = UserPrivilegesCommand("privileges",
                                                    help="获取用户权限", dynamic_args=True)
    ec2_info_command = EC2InfoCommand("ec2", help="获取所有地区的EC2（Elastic Computer Cloud）")
    remote_command_command = RemoteCommandExecute("exec", help="ec2远程命令执行")
    create_aws_url_command = CreateAwsUrl("aws-url", help="根据当前高权限生成aws控制台访问url")
    reset_command = ResetCommand("reset", help="重置aws_ak")

    exit_command = ExitCommand("exit", help="退出程序")

    console.addChild(help_command)
    console.addChild(userinfo_command)
    console.addChild(user_privileges_command)
    console.addChild(ec2_info_command)
    console.addChild(remote_command_command)
    console.addChild(create_aws_url_command)
    console.addChild(reset_command)
    console.addChild(exit_command)
    console.loop()


if __name__ == "__main__":
    main()
