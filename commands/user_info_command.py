from ishell.command import Command
import boto3 

current_user = ""

# 获取对应用户的信息
class UserInfoCommand(Command):
    def run(self, line):
        iam = boto3.resource('iam')
        global current_user
        current_user = iam.CurrentUser()
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
