# Ubuntu下screen的使用
## 运行
- 输入 screen 回车 即可进入


## 退出
- ctrl + A + D 即可退出

## 删除绘画
- screen -X -S 想要删除的screen quit

## 其他命令
- screen -ls 查看正在运行的screen程序
- screen -r 23544.pts-2.VM-0-9-ubuntu 进入（恢复离线）
- screen -d 23544.pts-2.VM-0-9-ubuntu 让其进入离线
- screen -wipe 检查目前所有的screen作业，并删除已经无法使用的screen作业
- 具体详见: [点击](https://blog.csdn.net/han0373/article/details/81352663)