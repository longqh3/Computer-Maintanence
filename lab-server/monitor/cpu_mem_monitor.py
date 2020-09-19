# -*- coding: utf-8 -*-
import psutil
import time
import os
import pandas as pd
import requests

# 监控CPU和内存异常信息
def cpu_mem_monitor():
    # 监控CPU异常
    cpu_per = int(psutil.cpu_percent(1))  # 每秒cpu使用率，（1，true） 每一核cpu的每秒使用率； 36
    # 监控内存占用异常
    mem = psutil.virtual_memory()  # 查看内存信息:(total,available,percent,used,free)
    mem_per = int(mem[2])
    # 执行相关操作
    if cpu_per > 50:
        terminate_notify("cpu")
    if mem_per > 50:
        terminate_notify("mem")

def terminate_notify(error_type):
    # 应用ps命令执行监控
    with os.popen(f"ps -eo pid,ppid,%mem,%cpu,comm,user --sort=-%{error_type} | head", "r") as p:
        text = p.read()
        ps_list = text.split("\n")
        df_list = [row.split() for row in ps_list]
        sys_info_df = pd.DataFrame(df_list[1:], columns=df_list[0])
        # 终止排名第一位的进程
        os.system(f"kill {sys_info_df.PID[0]}")
        # 上报相关异常信息至邮箱或微信推送中
        # 微信推送
        send_wechat_notify(sys_info_df)

def send_wechat_notify(sys_info_df):
    # 直接调用Server酱服务进行微信推送
    # Server酱URL
    url = 'SCU46870Teff161add8ab0bbbbb1739e61bde143e5df5030cdac90'
    d = {'text':"Warning: master节点资源异常信息",
         'desp':f"{sys_info_df.USER[0]}用户在master上运行相关程序，CPU或内存已达最大负载的50%，现已将相关任务{sys_info_df.COMMAND[0]}关闭！请及时提醒相关人员"}
    requests.post(url, data = d)

def send_email(info):
    sender = '***@qq.com'
    recevier = '***@qq.com'
    subject = 'Warning'
    username = '***@qq.com'
    password = '***'  # 相应的密码
    msg = MIMEText(info, 'plain', 'utf-8')
    msg['Subject'] = Header(subject, 'utf-8')
    msg['From'] = sender
    msg['To'] = recevier
    smtp = smtplib.SMTP()
    smtp.connect('smtp.qq.com')
    smtp.login(username, password)
    smtp.sendmail(sender, recevier, msg.as_string())
    smtp.quit()

if __name__ == "__main__":
    while(1):
        cpu_mem_monitor()
        # 每隔100秒，检查一次当前服务器的使用情况
        time.sleep(100)