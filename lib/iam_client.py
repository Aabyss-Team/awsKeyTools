import boto3 
import json 

class IAMClient():
    """单例模式"""
    def __new__(cls, *args, **kwargs):
        """ 这里保证了IAMClient的单例"""
        if not hasattr(cls, '_instance'):
            cls._instance = super(IAMClient, cls).__new__(cls)
        return cls._instance

    def __init__(self, *args, **kwargs):
        """_iam_client 在这里保证了单例"""
        if not hasattr(self, '_iam_client'):
            self._iam_client = boto3.client('iam')  #这里不实例化了吗？对呀，

    def get_attached_policies(self, user_name):
        """获取对应用户的托管策略，我在这里不访问了吗？？？？对呀，我先创建IAMClient对象呀，调用这个对象的方法不就好了？靠"""
        attached_response = self._iam_client.list_attached_user_policies(
            UserName=user_name, PathPrefix='/', MaxItems=123)
        attached_policy_lst = attached_response.get("AttachedPolicies")
        #稍等，别急嘛，我不看怎么封装。。。。。绝
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

    def get_inline_policies(self, user_name):
        """获取对应用户的内置策略"""
        response = self._iam_client.list_user_policies(UserName=user_name, )
        policy_lst = response.get("PolicyNames")
        # 内敛策略的名称
        # print(policy_lst)
        for p in policy_lst:
            user_policy_response = self._iam_client.get_user_policy(
                UserName=user_name, PolicyName=p)
            policy_document = json.dumps(
                user_policy_response.get("PolicyDocument"), indent=2)
            print(f"内联策略: {p}\n{policy_document}")

    # 创建实例配置文件并附加
    def create_instance_profile(self):
        # 1.创建policy ssm_policy
        with open("AmazonSSMManagedInstanceCore.json",
                  mode="r",
                  encoding="utf-8") as f:
            json2 = f.read()
        self._iam_client.create_policy(
            PolicyName='ssm_policy',
            Path='/',
            PolicyDocument=json2,
        )
        # arn:aws:iam::455720863430:policy/ssm_policy
        # 2.创建角色 AmazonSSMManagedInstance
        with open("ec2-role-trust-policy.json", mode="r",
                  encoding="utf-8") as f:
            json1 = f.read()
        self._iam_client.create_role(
            Path='/',
            RoleName='AmazonSSMManagedInstance',
            AssumeRolePolicyDocument=json1,
            Description=
            'Allows EC2 instances to call AWS services on your behalf.',
        )
        # arn:aws:iam::455720863430:role/AmazonSSMManagedInstance
        # 3.给角色加policy
        with open("AmazonSSMManagedInstanceCore.json",
                  mode="r",
                  encoding="utf-8") as f:
            json2 = f.read()
        self._iam_client.put_role_policy(RoleName='AmazonSSMManagedInstance',
                                         PolicyName='ssm_policy',
                                         PolicyDocument=json2)
        # 4.创建实例配置文件 arn:aws:iam::455720863430:instance-profile/SSMFullAccessProfile
        instance_profile_name = "SSMFullAccessProfile"
        response3 = self._iam_client.create_instance_profile(
            InstanceProfileName=instance_profile_name)
        instance_profile_arn = response3.get("InstanceProfile").get("Arn")
        # 5.添加角色到实例配置文件
        self._iam_client.add_role_to_instance_profile(
            InstanceProfileName=instance_profile_name,
            RoleName='AmazonSSMManagedInstance')
        return instance_profile_arn, instance_profile_name

    def get_instance_profile(self):
        """检查是否存在实例配置文件"""
        response = self._iam_client.list_instance_profiles(PathPrefix='/',
                                                           MaxItems=123)
        instance_profiles_lst = response.get("InstanceProfiles")
        for instance_profile in instance_profiles_lst:
            name = instance_profile.get("InstanceProfileName")
            if name == "SSMFullAccessProfile":
                # 已经存在
                instance_profile_arn = instance_profile.get("Arn")
                print("检测到已经创建过实例配置文件，正在关联...")
                return instance_profile_arn, name
        print("检测到没有创建实例配置文件，正在创建实例配置文件...")
        return self.create_instance_profile()
