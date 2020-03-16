# 问题一
1. 问题描述

2020.3.15日下午服务器无法通过ssh连接，经现场确认后发现是pbs系统出现故障，并提示以下错误信息

```
03/15/2020 20:06:08;0001;   pbs_mom.32064;Svr;pbs_mom;LOG_ERROR::read_tcp_reply, Mismatching protocols. Expected protocol 4 but read reply for 0
03/15/2020 20:06:08;0001;   pbs_mom.32064;Svr;pbs_mom;LOG_ERROR::read_tcp_reply, Could not read reply for protocol 4 command 4: End of File
03/15/2020 20:06:08;0001;   pbs_mom.32064;Svr;pbs_mom;LOG_ERROR::mom_server_update_stat, Couldn't read a reply from the server
03/15/2020 20:06:08;0001;   pbs_mom.32064;Svr;pbs_mom;LOG_ERROR::send_update_to_a_server, Could not contact any of the servers to send an update
03/15/2020 20:06:08;0001;   pbs_mom.32064;Svr;pbs_mom;LOG_ERROR::send_update_to_a_server, Status not successfully updated for 181256 MOM status update intervals
```

2. 问题分析

pbs系统报错主要集中于read_tcp_reply、mom_server_update_stat、send_update_to_a_server这三类错误中，有理由推测，故障原因在于它想同步多个节点上的pbs日志信息，但因为网络问题无法同步，多次尝试也失败，陷入死循环进而导致宕机。

3. 问题搜索

    1. [torque-6.1.2 安装问题，子节点down状态如何启动](http://muchong.com/html/201810/12721088.html)

    主要集中于torque系统初始启动问题，但本次问题出现在运行过程中，排除。

    2. [pbs_mom networking split into multiple IPs](https://github.com/adaptivecomputing/torque/issues/220)

    问题可能在于受信任的ip地址不一致上，pbs-mom和子节点的ip地址以及端口存在差异，故而无法互相访问（可能性1）

    3. [Error message when running jobs using torque. read_tcp_reply, Mismatching protocols. Expected protocol 4 but read reply for 0](https://stackoverflow.com/questions/40995829/error-message-when-running-jobs-using-torque-read-tcp-reply-mismatching-protoc)

    问题还可能在于缺少mom_hierarchy文件上，该问题中通过创建mom_hierarchy文件完成修复，但我倾向于是网络端口问题

