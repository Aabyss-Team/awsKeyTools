from ishell.console import Console
from ishell.command import Command
import boto3
import os 

console = Console(prompt="aws-key-tools ", prompt_delim=">")
access_key = ""
secret_key = ""
current_arn =""


## 初始化access_key 和 secret_key
class InitCommand(Command):
    def run(self, line):
        #读取access_key 和 secret_key
        global access_key
        global secret_key
        access_key = input("access_key:")
        secret_key = input("secret_key:")
        #将access_key 和 secret_key 写入配置文件
        #TODO 修改配置文件地址
        #获取家目录
        home_path = os.path.expanduser("~")
        #检查.aws 文件夹是否存在，不存在则创建
        if not os.path.exists(home_path + "/.aws"):
            os.mkdir(home_path + "/.aws")
        config_path = os.path.join(home_path, ".aws","config")
        #[default]
        # aws_access_key_id=foo
        # aws_secret_access_key=bar
        # aws_session_token=baz
        with open(config_path, "w") as f:
            f.write("[default]\n")
            f.write("aws_access_key_id=" + access_key + "\n")
            f.write("aws_secret_access_key=" + secret_key + "\n")
        print("设置成功")

# aws //这个呢
# access_key : = AKIAUXGYIDMBL4IKDRHL
# screr_key =  a6JyzYyRaVeFHiHkMiTkR06pMymPpHFHF2SsVRFX
# ap-east-1  //这个呢？地区

# AKIAWUGYUQ3DE2PLHE3K
# lCg1dTBvie5F/u9O5T7NXig9acaGwAoRpdlNhJuI
# 这几个是连在一起吗？
## 获取对应用户的信息
class UserInfoCommand(Command):
    def run(self, line):
        iam = boto3.resource('iam') 
        current_user = iam.CurrentUser()
        global current_arn 
        current_arn = current_user.arn
        print("UserInfo:")
        print("\tarn:\t\t\t", current_user.arn) #这个arn是啥东西？老哥？
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



## 获取key对应的用户权限
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
    init_command = InitCommand("init", "初始化 access_key 和 secret_key")
    userinfo_command = UserInfoCommand("userinfo", help="获取用户信息")
    user_privileges_command = UserPrivilegesCommand("privileges",
                                                    help="获取用户权限")
    ec2_info_command = EC2InfoCommand("ec2info", help="获取ec2信息")
    remote_command_command = RemoteCommandCommand("remote", help="远程命令执行")
    iam_role_command = IAMRoleCommand("create-role", help="创建IAM角色")
    console.addChild(init_command)
    console.addChild(userinfo_command)
    console.addChild(user_privileges_command)
    console.addChild(ec2_info_command)
    console.addChild(remote_command_command)
    console.addChild(iam_role_command)
    console.loop()


if __name__ == "__main__":
    main()