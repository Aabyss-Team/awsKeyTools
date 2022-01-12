from ishell.command import Command
import boto3

ec2_lst = []


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
        ec2 = boto3.client('ec2', region_name='us-east-1') # 怎么改？
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
                    platform_details = instance.get(
                        "Platform") if instance.get(
                            "Platform") else instance.get("PlatformDetail")
                    architecture = instance.get("Architecture")
                    root_device = instance.get("RootDeviceName")
                    ec2_obj = EC2Instance(id, region_name, instance_id,
                                          key_name, public_ip, private_ip,
                                          iam_instance_profile_arn,
                                          platform_details, architecture,
                                          root_device)
                    ec2_lst.append(ec2_obj)
                    i += 1
        self.show_ec2()


class EC2Instance:
    def __init__(self, id, region, instance_id, key_name, public_ip,
                 private_ip, iam_instance_profile_arn, platform_details,
                 architecture, root_device):
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
