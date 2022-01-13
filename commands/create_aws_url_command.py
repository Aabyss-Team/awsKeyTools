from ishell.command import Command
from .key import access_key, secret_key
from aws_consoler.cli import api

# 根据ak生成aws控制台访问链接
class CreateAwsUrl(Command):
    def run(self, line):
        print("根据当前权限生成一个aws控制台访问的url")  # 可以的，只要修改本地包就好了，这个就是args[]
        api(access_key=access_key, secret_key=secret_key)