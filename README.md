## 功能需求

每个功能点对应一个函数 , 可以写一个简单的菜单栏

提供用户输入对应功能的编号

- 查看key对应的用户信息
- 查看key对应的用户权限
- 列出所有地区的ec2主机信息(标注出托管状态)
  - 操作系统  公网ip 内网ip 实例id 计算机名称等
- ec2远程执行命令
- 创建IAM角色并添加到ec2上


## 相关文档：
https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html
https://docs.aws.amazon.com/index.html?nc2=h_ql_doc

https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ssm.html#SSM.Client.send_command