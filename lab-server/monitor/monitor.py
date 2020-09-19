# -*- coding: utf-8 -*-
import psutil
import datetime
from xlrd import open_workbook
from xlutils.copy import copy
import time
 
# 监控CPU信息
def cpu():
    cpu = psutil.cpu_count(False)    # cpu核数 默认逻辑CPU核数， False查看真实cpu核数 2
    cpu_per = int(psutil.cpu_percent(1))  # 每秒cpu使用率，（1，true） 每一核cpu的每秒使用率； 36
    # print(cpu, cpu_per)
    return cpu_per
 
# 监控内存信息
def mem():
    mem = psutil.virtual_memory()  # 查看内存信息:(total,available,percent,used,free)
    # print(mem)
    mem_total = int(mem[0]/1024/1024)
    mem_used = int(mem[3]/1024/1024)
    mem_per = int(mem[2])
    mem_info = {
        'mem_total': mem_total,
        'mem_used': mem_used,
        'mem_per': mem_per,
    }
    return mem_info
 
# 监控磁盘使用率
def disk():
    c_per = int(psutil.disk_usage('C:')[3])   # 查看c盘的使用信息：总空间，已用，剩余，占用比;
    d_per = int(psutil.disk_usage('d:')[3])
    e_per = int(psutil.disk_usage('e:')[3])
    # f_per = int(psutil.disk_usage('f:')[3])
    # print(c_per, d_per, e_per)
    disk_info = {
        'c_per': c_per,
        'd_per': d_per,
        'e_per': e_per,
        # 'f_per': f_per,
    }
    return disk_info
 
# 监控网络流量
def network():
    network = psutil.net_io_counters()  # 查看网络流量的信息；(bytes_sent, bytes_recv, packets_sent, packets_recv, errin, errout, dropin, dropout)
    # print(network)
    network_sent = int(psutil.net_io_counters()[0] / 8 / 1024)  # 每秒接受的kb
    network_recv = int(psutil.net_io_counters()[1]/8/1024)
    network_info = {
        'network_sent': network_sent,
        'network_recv': network_recv
    }
    return network_info
 
# 间隔一定时间(10秒)，输出当前的CPU状态信息
def all_msg():
    msg = []
    now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # append之后是['2019-03-21 15:31:39']
    # now_time = datetime.datetime.strptime(now_time, '%Y-%m-%d %H:%M:%S')  # append之后是[datetime.datetime(2019, 3, 21, 15, 29, 42)]
    msg.append(now_time)  # 获取时间点 (f0)
    cpu_info = cpu()
    msg.append(cpu_info)  # cpu 使用率(f1),单位：%
    mem_info = mem()
    msg.append(mem_info['mem_per'])  # 内存使用率(f2),单位：%
    disk_info = disk()
    msg.append(disk_info['c_per'])  # C磁盘使用率 (f3)，单位：%
    msg.append(disk_info['d_per'])  # d磁盘使用率 (f4)，单位：%
    msg.append(disk_info['e_per'])  # e磁盘使用率 (f5)，单位：%
    network_info = network()
    msg.append(network_info['network_sent'])  # 网络流量接收的量（MB）(f6)
    msg.append(network_info['network_recv'])  # 网络流量发送的量（MB） (f7)
    return msg
 
def write_xls(lis,filename):
    rb = open_workbook(filename)
    wb = copy(rb)
    ws = wb.get_sheet(0)
    for i in range(0, len(lis)):
        ws.write(0, i, lis[i])
    wb.save(filename)
 
def main():
    cnt_times = 1
    while(1):
        msg = all_msg()
        print(msg)  # 实时打印每个十秒写入excel的数据。
        write_xls(msg, "./cs_monitor.xls")
        cnt_times += 1
        # 每隔10秒，统计一次当前计算机的使用情况。
        time.sleep(10)
        # 统计了20000次后跳出当前循环，统计的总共时间是：20000*10/3600 ~= 55.55
        if(cnt_times > 20000):
            break
 
main()
 
 
"""
# 发邮件进行实时报告计算机的状态
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from email.header import Header
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
# 主函数调用，调用其他信息
def main():
    cpu_info = cpu()
    mem_info = mem()
    disk_info = disk()
    network_info = network()
    info = ''' 
                监控信息 
        ========================= 
        cpu使用率： : %s,
        ========================= 
        内存总大小（MB） : %s, 
        内存使用大小（MB） : %s, 
        内存使用率 : %s,
        =========================
        C盘使用率: %s, 
        D盘使用率: %s,
        E盘使用率: %s,
        =========================
        网络流量接收的量（MB） : %s, 
        网络流量发送的量（MB）: %s,
    ''' % (cpu_info,
          mem_info['mem_total'], mem_info['mem_used'], mem_info['mem_per'],
          disk_info['c_per'], disk_info['d_per'], disk_info['e_per'],
          network_info['network_sent'], network_info['network_recv'])
    send_email(info)
main()
"""