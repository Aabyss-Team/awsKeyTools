import os 
access_key = ""
secret_key = ""


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