![awsKeyTools](https://socialify.git.ci/Aabyss-Team/awsKeyTools/image?description=1&font=KoHo&forks=1&issues=1&language=1&name=1&owner=1&pattern=Solid&stargazers=1&theme=Dark)

## 一、安装本工具
环境： 
```bash
linux or mac(windows不支持)
python version >= 3.7
```


安装： 
```bash
git clone https://github.com/Aabyss-Team/awsKeyTools.git
cd awsKeyTools
pip3 install -r requirements.txt
```

如果遇到 ` error: command 'x86_64-linux-gnu-gcc' failed with exit status 1` 报错 

解决方案： sudo apt-get install libncurses5-dev



## 二、使用本工具

第一次使用工具会提示输入ak

```bash
python3 main.py
```

输入你的aws_ak即可

1.查看命令帮助

```
┌──(root💀192)-[~/桌面/awsKeyTools-new_dev (2)]
└─# python3 main.py

                    __                   __                .__          
_____ __ _  _______|  | __ ____ ___.__._/  |_  ____   ____ |  |   ______
\__  \ \/ \/ /  ___/  |/ // __ <   |  |\   __\/  _ \ /  _ \|  |  /  ___/
 / __ \     /\___ \|    <\  ___/\___  | |  | (  <_> |  <_> )  |__\___ \ 
(____  /\/\_//____  >__|_ \___  > ____| |__|  \____/ \____/|____/____  >
     \/           \/     \/   \/\/                                   \/ 
                                                     version : 0.0.1
                                                     by dbg9 and 无在无不在

aws-key-tools > help
Help:
           help - 查看命令帮助
       userinfo - 获取用户信息
     privileges - 获取用户权限
            ec2 - 获取所有地区的EC2（Elastic Computer Cloud）
           exec - ec2远程命令执行
        aws-url - 根据当前高权限生成aws控制台访问url
          reset - 重置aws_ak
           exit - 退出程序
aws-key-tools > 
```

2.获取ak对应的用户信息

```bash
aws-key-tools > userinfo
```

![image-20220113104623065](https://note-1301783483.cos.ap-nanjing.myqcloud.com/image/202201131046285.png)

3.查看用户权限 , 默认查看的是用户对应策略的json文件

```
aws-key-tools > privileges 
```

![image-20220113104835778](https://note-1301783483.cos.ap-nanjing.myqcloud.com/image/202201131048925.png)

使用enum参数可以通过枚举查看用户的权限

```bash
aws-key-tools > privileges enum
```

![image-20220113105804929](https://note-1301783483.cos.ap-nanjing.myqcloud.com/image/202201131058081.png)

4.枚举当前用户可用地区存在的ec2主机

```bash
aws-key-tools > ec2
```

![image-20220113162308876](https://note-1301783483.cos.ap-nanjing.myqcloud.com/image/202201131623225.png)

5.指定ec2远程命令执行

```
aws-key-tools > exec
```

如果无法获取平台信息 , 需要用户手动输入

如果当前ec2没有关联实例配置文件 , 会先检测是否存在实例配置文件 , 如果不存在就是创建 , 然后附加到ec2上

![image-20220113120341066](https://note-1301783483.cos.ap-nanjing.myqcloud.com/image/202201131203216.png)

如果创建并添加报错 , 请再次执行exec , 此时不会创建会直接添加

如果存在已创建的示例配置文件直接附加 

![image-20220113112935706](https://note-1301783483.cos.ap-nanjing.myqcloud.com/image/202201131129849.png)

由于实例配置文件的关联需要一定的时间 , 所以约10分钟后 , 才能执行命令

![image-20220113115250069](https://note-1301783483.cos.ap-nanjing.myqcloud.com/image/202201131152191.png)

输入 `exit` 退出当前命令执行

6.生成aws控制台访问连接 , 需要当前用户有一定的权限才可以成功执行

```bash
aws-key-tools > aws-url
```

![image-20220113113107341](https://note-1301783483.cos.ap-nanjing.myqcloud.com/image/202201131131488.png)

7.重置aws_ak

提示用户重新输入ak

```bash
aws-key-tools > reset
```

8.退出

```bash
aws-key-tools > exit 
```

## 三、参考文档
- https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html
- https://github.com/NetSPI/aws_consoler
- https://github.com/andresriancho/enumerate-iam

## 四、免责声明🧐
1. 本工具仅面向合法授权的企业安全建设行为，如您需要测试本工具的可用性，请自行搭建靶机环境。
2. 在使用本工具进行检测时，您应确保该行为符合当地的法律法规，并且已经取得了足够的授权。请勿对非授权目标进行扫描。
3. 如您在使用本工具的过程中存在任何非法行为，您需自行承担相应后果，我们将不承担任何法律及连带责任。

## 五、感谢各位师傅🙏

## Stargazers

[![Stargazers repo roster for @Aabyss-Team/awsKeyTools](https://reporoster.com/stars/Aabyss-Team/awsKeyTools)](https://github.com/Aabyss-Team/awsKeyTools/stargazers)


## Forkers

[![Forkers repo roster for @Aabyss-Team/awsKeyTools](https://reporoster.com/forks/Aabyss-Team/awsKeyTools)](https://github.com/Aabyss-Team/awsKeyTools/network/members)


## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=Aabyss-Team/awsKeyTools&type=Date)](https://star-history.com/#Aabyss-Team/awsKeyTools&Date)
