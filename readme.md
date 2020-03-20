# E5 Renew SCF

如题，[原版刷API脚本](http://file.heimu.ltd/1.py)的修改版，单次执行，专门用于腾讯云的无服务器云函数。

### 配置

参数获取请参见[office e5刷API脚本分享以及教程](https://blog.432100.xyz/index.php/archives/50/)、[E5刷API脚本分享以及教程](https://huengyamm.xyz/2020/03/15/E5-API/)（后面这个有图）。

入口函数为`index.exe`。

需要预先配置以下环境变量：

`Region`：该云函数所在服务器地域，地域代码参见[地域列表](https://cloud.tencent.com/document/product/583/17238#.E5.9C.B0.E5.9F.9F.E5.88.97.E8.A1.A8)

`refresh_token`：`rclone`所获取的同名参数，[点击这里下载`rclone`](http://file.heimu.ltd/rclone.exe)

`ms_id`：Azure AD上的**应用程序(客户端) ID**

`ms_secret`：Azure AD上的**客户端密码**（不是用户密码）

`SecretId`、`SecretKey`：先到腾讯云[API密钥管理](https://console.cloud.tencent.com/cam/capi)创建，用于刷新环境变量中的`refresh_token`

如果你有新的API要加入，只要请求的header格式一致，可以直接加入`api_list`列表（那两个`messageRules`是原本就有两条的，我暂且蒙在鼓里）。

另外，云函数不会自己运行，请自行设置触发器。

### 随机时间

原本的设想是直接删除旧的触发器，然后添加一个随机时间的触发器，没想到居然不行。

> [TencentCloudSDKException] code:FailedOperation.CreateTrigger message:创建触发器失败 (当前函数状态无法进行此操作)

明明连修改环境变量都可以……没办法，不能在一个函数内实现随机时间了。（除非你想靠`sleep(random())`卡时间，但这样会浪费不少计费时间）

如果你不嫌麻烦的话，确实可以通过两个函数互相调用来实现随机时间。

具体实现分为两种：**A+B类型**，**主+从类型**

#### A+B类型

通过用两个具有完整功能的函数互相设置定时触发器来实现。

环境变量：

`TrigUpdateType`：*AB*

两个函数都要设置下面说的“相同的部分”。

**注意：**云函数提供了包括环境变量在内的**复制**功能，复制前不要在环境变量中填写`refresh_token`。

#### 主+从类型（开发中，~~请忽略~~ 复制功能的存在使得这一类型的存在变得可有可无。。）

主函数直接调用从函数，从函数设置主函数触发器。

主函数环境变量：

`TrigUpdateType`：*MS*

以及下列的“相同的部分”。

从函数设置：

入口函数：`ScfOperate.MSTrigUpdate_Slave`

环境变量：不需要，主函数会传递过去

#### 环境变量设置中相同的部分：

`AnotherFunctionName`：另一个函数的`FunctionName`

`AnotherRegion`：（可选）另一个函数的`Region`，默认相同

`AnotherNamespace`：（可选）另一个函数的`Namespace`，默认相同

`random_time_lowerlimit`、`random_time_toplimit`：（可选）随机时间的下限、上限，默认150、300（秒）

`TriggerName`：（可选）触发器的名称，每次更新都会先删除这个名字的触发器再添加一个同名的，默认值为*RandomTimer*。

无论使用哪种类型，建议只设置一个api触发器，因为程序在初次运行后，就能自动递归触发下一次。

### 响应

这玩意什么~~都不会响应~~ 请问响应一个null有什么卵用吗。

目前还想不到能响应什么有用的东西，毕竟大部分时间都是无值守运行。

所有`print()`的输出请到云函数的运行日志查看。

### 消耗

测试挂了一天，设置的触发器每5分钟触发一次，共使用资源约180GBs，出流量0.01GB，完全不会超出免费额度；另外，每次触发平均耗时4s，内存消耗基本都在20MB左右。

### TODO

- [x] ~~自行递归添加下一个触发器（以实现真正随机时间而不是靠`sleep(random())`卡时间实现）~~
  
- [x] 搞懂为什么不能在定义全局变量的时候用环境变量赋值

 > 目前自行定义的环境变量和一些会有变动的环境只能在入口函数中获取，是因为是在调用入口函数的时候注入的。——腾讯云工作人员回复（为什么不写在文档里？）

- [ ] 把那些手打的`params`用字典转json代替（对于那种连多打一个逗号都要报错的解析器表示强烈cnm

- [ ] 欢迎issue。