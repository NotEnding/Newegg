#!/bin/bash

# 生成文件
python3 /home/zhengke/Coding/newegg/auxiliary/EmailNotice.py

# 发送邮件（邮件内容用绝对路径）
sendEmail -xu yf_system@starmerx.com -xp Tianhu2017 -t zhengke@starmerx.com -t liyanli@starmerx.com -t zhaolei@starmerx.com -s smtp.exmail.qq.com -f yf_system@starmerx.com -o message-charset=utf-8 -o message-file=/home/zhengke/Coding/newegg/email.txt -u "Newegg spider:detail information"
