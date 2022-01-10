## 使用
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



## 功能需求

每个功能点对应一个函数 , 可以写一个简单的菜单栏

提供用户输入对应功能的编号

- 查看key对应的用户信息
- 查看key对应的用户权限
- 列出所有地区的ec2主机信息(标注出托管状态)
  - 操作系统  公网ip 内网ip 实例id 计算机名称等
- ec2远程执行命令
- 创建IAM角色并添加到ec2上

新增功能
- 提示用户必须init操作 （实现）
- 封装列举的实例到一个对象中 （实现）
- 权限枚举模块(阅读源码自己实现)
- ak生成aws_web控制端url (实现)
- 假如ec2没有IAM角色或者对应的IAM角色的策略中没有ssm权限，需要手动赋予IAM角色或者修改policy
   



## 相关文档：
https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html
https://docs.aws.amazon.com/index.html?nc2=h_ql_doc

