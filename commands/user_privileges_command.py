from ishell.command import Command
from enumerate_iam.main import enumerate_iam
from lib import IAMClient 
from .key import access_key, secret_key
import  commands.user_info_command  as user_info_command

# 获取key对应的用户权限
class UserPrivilegesCommand(Command):
    def run(self, line):
        last_arg = line.strip().split()[-1]
        # 1.通过api的方式枚举，使用enum参数激活
        if last_arg == "enum":
            enumerate_iam(access_key=access_key,
                          secret_key=secret_key,
                          session_token=None,
                          region=None)
        else:
            # 2.获取当前用户的aws托管策略和内嵌策略
            # 获取当前用户名
            try:
                user_name = user_info_command.current_user.user_name
            except Exception:
                print("请先使用 userinfo 获取当前用户，然后才能查看用户对应的权限")
                return
            # 获取当前用户的aws托管策略和内嵌策略
            client = IAMClient()
            client.get_attached_policies(user_name=user_name)
            client.get_inline_policies(user_name=user_name)
