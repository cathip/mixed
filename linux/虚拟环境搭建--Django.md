# 安装nginx
- yum install nginx
- systemctl start nginx.service
- systemctl enable nginx.service

# 安装python
- yum install https://centos7.iuscommunity.org/ius-release.rpm -y 
- yum install python36u  -y
- yum install python36u-pip python36u-devel  -y
- csdn教程 ： https://blog.csdn.net/wzhwei1987/article/details/84102589

# 创建python 虚拟环境
- cd /home/
- mkdir django
- cd django
- apt-get install python3-venv
- python3.6 -m venv venv
- activate 进入虚拟环境
- deactivate 退出虚拟环境

# 安装python相关包
- 虚拟环境目录下执行  pip3 install -r  plist.txt

- ubuntu 安装到mysqlclient时会报错 \
原因缺少配置文件 安装  apt-get install  libmysqld-dev
