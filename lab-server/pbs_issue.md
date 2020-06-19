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

pbs系统报错主要集中于read_tcp_reply, mom_server_update_stat, send_update_to_a_server这三类错误中，有理由推测，故障原因在于它想同步多个节点上的pbs日志信息，但因为网络问题无法同步，多次尝试也失败，陷入死循环进而导致宕机。

3. 问题搜索

    1. [torque-6.1.2 安装问题，子节点down状态如何启动](http://muchong.com/html/201810/12721088.html)

    主要集中于torque系统初始启动问题，但本次问题出现在运行过程中，**排除**。

    2. [pbs_mom networking split into multiple IPs](https://github.com/adaptivecomputing/torque/issues/220)

    问题可能在于受信任的ip地址不一致上，pbs-mom和子节点的ip地址以及端口存在差异，故而无法互相访问（可能性1）

    3. [Error message when running jobs using torque. read_tcp_reply, Mismatching protocols. Expected protocol 4 but read reply for 0](https://stackoverflow.com/questions/40995829/error-message-when-running-jobs-using-torque-read-tcp-reply-mismatching-protoc)

    问题还可能在于缺少mom_hierarchy文件上，该问题中通过创建mom_hierarchy文件完成修复，但我倾向于是网络端口问题

4. 问题解决

对pbs(Torque)系统相关文档进行查阅后发现，管理端对应pbs_server服务，运算端对应pbs_mom服务，调度则对应pbs_sched服务，故而在不同节点上运行相应服务以完成系统配置，**即可解决问题**。

```
# for master node
# pbs_sched service cannot be initialized, returned "LOG_ERROR::Address already in use (98)"
for i in pbs_server pbs_sched trqauthd; do service $i restart; done
for i in pbs_server pbs_sched trqauthd; do service $i status; done
# for slave node
for i in pbs_mom trqauthd; do service $i restart; done
for i in pbs_mom trqauthd; do service $i status; done
```

# 问题二

1. 问题描述

师姐在服务器上的R内运行INLA包内特定函数时，出现`/lib64/libm.so.6: version 'GLIBC_2.27' not found(required by ~/.conda/envs/test/lib/R/library/INLA/bin/linux/64bit/libgfortran.so.4)`错误，需要通过修改服务器运行环境中依赖库或更改INLA包内预编译程序加以解决

2. 问题分析

应用`strings /lib64/libc.so.6 |grep GLIBC_`命令查看系统glibc库版本，该问题出现，可能为以下原因：系统的glibc版本太低，软件编译时使用了较高版本的glibc。故而有以下两种解决方案。

    1. 更新当前系统上的glibc(缺少root权限，且千万要慎之又慎)

        1. 编译安装——最硬核解决方案(需要root权限)

        安装前置依赖包，并直接通过编译方式升级glibc，再将个人需要的glibc与软件包关联。实现案例：[/lib64/libm.so.6: version `GLIBC_2.23' not found](https://www.codetd.com/article/9164912)、[Centos6 升级glibc-2.17](https://cloud.tencent.com/developer/article/1463094)(采用rpm进行glibc安装)、[无ROOT权限更新Glibc库并调用](https://fiercex.github.io/post/make_glibc/)(从GCC出发，编译安装glibc，修改调用并进一步安装python3，很详细但很复杂)、[Linux提示“libc.so.6: version `GLIBC_2.14' not found”系统的glibc版本太低](https://www.linuxidc.com/Linux/2017-01/139806.htm)(很详尽的安装、编译、环境变量设置教程，如**可用可以考虑**，但圄于gcc版本、Linux版本限制无法实现)

        或者直接执行`yum update glibc`亦可

        2. 使用conda来尝试安装glibc库(完 全 失 败)，极易搞乱个人环境，**千万不要尝试**

        于[Anaconda官网](https://anaconda.org)上搜索glibc相关库，惊喜地查到了一个glibc 2.30版本的库，虽然下载量不大，但好像更新很快、版本很高。但我在这里完全忽略了一点，就是**glibc是系统底层库**，轻易对其不作备份、无法回滚地更改，只是自己折磨自己。果不其然，费尽千辛万苦(直接conda安装，网络连接失败；本地下载安装，文件格式不对，需要将tar.bz2.tar解压为tar.bz2格式才能离线安装)，本以为能一朝功成，但等来的只是该环境下调用任何程序(R、Python)的返回的`Segment Fault`，仿佛在嘲笑我的无知emmm(最后只得通过删除并新建环境加以解决)

        浪费接近8小时时间后，我终于放弃了折腾，选择其他方案。

        这里有个小插曲，如果**给conda重复添加镜像，那么那个被重复添加的镜像地址会被置于第一位**。在这里，清华源取代了conda-forge成为了第一位，于是，我光荣地忘却原有的R和Python是如何安装的了(如果R、Python版本存在冲突，以第一位的源内信息为准)，这里又浪费将近2小时时间，我佛了。

        3. 失败案例

        [非root用户更新glibc版本的悲惨故事](https://blog.csdn.net/lalaxumelala/article/details/103178680)(系 统 崩 溃)

    2. 更换软件版本使之与系统适配(后通过该方式解决)

    经过师姐与R包开发者联系，其对于在低版本Linux系统上运行R包提出的解决方案为：安装测试版本，并执行`inla.binary.install()`命令，选择Centos 7版本对应的依赖环境，亦即将运行依赖环境替换为低版本glibc编译的环境(其实结合报错信息也应该发现是整体环境出现的问题)。

    毫不意外的，因为网络原因，R内直接执行命令失败。于是离线下载相应依赖环境tgz压缩包，并在依赖环境文件夹内进行解压，**问题解决**

3. 问题反思

    1. 总结一下，假如你在平台A编译的程序，放在平台B上跑：如果报错提示GLIBC版本低，那**千万不要手动升级GLIBC**，不然会出现很多问题，系统都有可能崩溃。最好的解决方案就是在平台B上重新编译；如果报错提示GLIBCXX版本低，那就有两种解决方案，要么在平台B重新编译，要么[手动升级平台B的GLIBCXX](https://blog.csdn.net/yuejisuo1948/article/details/88062832)。事实上我们这里采用的就是修改程序依赖环境而非glibc来完成运行，**尽可能联系开发者**，让其提供在低版本glibc环境下编译的依赖环境。

    2. 其实可以直接通过编译方式来安装glibc_2.27版本至**个人目录**(千万不可直接替换系统的glibc)下，并将运行的软件依赖库(libgfortran.so.4)ln到相应so.4文件即可，**但此处不能通过此种方法解决**，因为Centos版本太低了，十分难以实现编译安装。

    3. conda其实功能很强大，可以直接通过获取预编译文件夹的形式来避免编译过程中出现的各种奇葩问题，且其不仅支持Python包、R包(`conda install r-sf`)，还支持一系列系统包(可完善一些环境配置工作，但可能需要手动进行查找)。但切不可滥用，需要思考好用处后再行考虑，并**新建环境**进行，避免对base环境造成破坏。

        1. R包在安装失败时，可以**考虑通过conda进行安装**，其会自动完成相应环境的配置，亦或是直接下载可执行库文件夹(在缺少root权限并编译失败的情况下尤其有用)。千万不要硬顶着把所有依赖库都下好，那只是在折磨自己，即使有root权限(很容易搞乱系统环境)