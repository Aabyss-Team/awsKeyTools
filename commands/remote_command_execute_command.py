from ishell.command import Command
from lib import IAMClient 
from .ec2_info_command import ec2_lst
import boto3
import time 

# 远程命令执行
class RemoteCommandExecute(Command):
    platform_dic = {
        "linux": "AWS-RunShellScript",
        "windows": "AWS-RunPowerShellScript",
    }

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
                # 获取实例配置文件
                instance_profile_arn, instance_profile_name = IAMClient(
                ).get_instance_profile()
                print(instance_profile_arn)
                # 关联实例配置文件
                client_ec2 = boto3.client('ec2', region_name=region_name)
                try:
                    response = client_ec2.associate_iam_instance_profile(
                        IamInstanceProfile={
                            'Arn': instance_profile_arn,
                            'Name': instance_profile_name,
                        },
                        InstanceId=instance_id)
                except Exception:
                    print("实例配置文件创建成功,但是关联失败，请重新执行exec")
                    return
                if response.get("ResponseMetadata").get(
                        "HTTPStatusCode") == 200:
                    ec2.iam_instance_profile_arn = instance_profile_arn
                    print(
                        "实例配置文件关联成功 (ec2命令可以查看)，但是失效需要一定的等待时间，一般10分钟左右，请稍后再执行命令"
                    )
                    return
                else:
                    print("ec2实例配置文件关联失败")
            while 1:
                cmd = input('shell>').strip()
                if cmd == "exit":
                    return
                ssm_client = boto3.client('ssm', region_name=region_name)
                response = ssm_client.send_command(
                    InstanceIds=[
                        instance_id,
                    ],
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
                    if output.get("Status") == "Success" and output.get(
                            "StatusDetails") == "Success":
                        break
                    i += 1
                    time.sleep(i)
                    if i > 3:
                        break

                # 输出命令执行的结果
                cmd_output = output.get("StandardOutputContent") + output.get(
                    "StandardErrorContent").strip()
                print(cmd_output)

