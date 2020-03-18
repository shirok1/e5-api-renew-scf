# E5 Renew SCF

如题，[原版刷API脚本](http://file.heimu.ltd/1.py)的修改版，单次执行，专门用于腾讯云的无服务器云函数。

#### 配置

参数获取请参见[office e5刷API脚本分享以及教程](https://blog.432100.xyz/index.php/archives/50/)、[E5刷API脚本分享以及教程](https://huengyamm.xyz/2020/03/15/E5-API/)（这个有图）

需要预先配置以下环境变量：

`Region`：该云函数所在服务器地域，地域代码参见[地域列表](https://cloud.tencent.com/document/product/583/17238#.E5.9C.B0.E5.9F.9F.E5.88.97.E8.A1.A8)

`refresh_token`：`rclone`所获取的同名参数，[点击这里下载`rclone`](http://file.heimu.ltd/rclone.exe)

`ms_id`：Azure AD上的**应用程序(客户端) ID**

`ms_secret`：Azure AD上的**客户端密码**（不是用户密码）

`SecretId`、`SecretKey`：先到腾讯云[API密钥管理](https://console.cloud.tencent.com/cam/capi)创建，用于刷新环境变量中的`refresh_token`

如果你有新的API要加入，只要请求的header格式一致，可以直接加入`api_list`列表（那两个`messageRules`是原本就有两条的，我暂且蒙在鼓里）

另外，云函数不会自己运行，请自行设置触发器

#### 响应

这玩意什么~~都不会响应~~ 请问响应一个null有什么卵用吗

所有`print()`的输出请到云函数的运行日志查看

#### 消耗

测试挂了一天，设置的触发器每5分钟触发一次，共使用资源约75GBs，出流量0.01GB，完全不会超出免费额度；另外，每次触发平均耗时4.5s，内存消耗基本都在20MB左右。

#### TODO

自行递归添加下一个触发器（以实现真正随机时间而不是靠`sleep(random())`卡时间实现）