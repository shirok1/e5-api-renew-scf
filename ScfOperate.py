import os
import random
import time
import json
from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.scf.v20180416 import scf_client, models

# 定义关于腾讯云的变量
# 规范：全部单词首字母大写，中间无连接符号
global random_time_lowerlimit, random_time_toplimit, SecretId, SecretKey, Region
# 下次触发前的随机时间的范围:
random_time_lowerlimit = 150
random_time_toplimit = 300

# 读取环境变量中的腾讯云api
SecretId = ""
SecretKey = ""

# 读取环境变量中的腾讯云地域
Region = ""


# 写入环境变量（主要是为了更新refresh_token供下次使用）


def EnvWrite(FunctionName, Namespace, ms_id, ms_secret, refresh_token, Another=None):
    global SecretId, SecretKey, Region
    try:
        cred = credential.Credential(SecretId, SecretKey)
        client = scf_client.ScfClient(cred, Region)
    except TencentCloudSDKException as err:
        print(err)
    req = models.UpdateFunctionConfigurationRequest()
    params = '{"FunctionName":"' + FunctionName + '",'
    params += '"Namespace":"' + Namespace + '",'
    params += '"Environment":{"Variables":['
    params += '{"Key":"Region","Value":"' + Region + '"},'
    params += '{"Key":"refresh_token","Value":"' + refresh_token + '"},'
    params += '{"Key":"ms_id","Value":"' + ms_id + '"},'
    params += '{"Key":"ms_secret","Value":"' + ms_secret + '"},'
    params += '{"Key":"SecretId","Value":"' + SecretId + '"},'
    params += '{"Key":"SecretKey","Value":"' + SecretKey + '"},'
    if Another:
        for key in Another:
            if Another[key]:
                params += '{"Key":"'+ key + '","Value":"' + Another[key] + '"},'
    params = params.rstrip(",")
    params += ']}}'
    #print(params)
    req.from_json_string(params)
    try:
        # 以下照抄腾讯云sdk例程
        resp = client.UpdateFunctionConfiguration(req)
        print(resp.to_json_string())
    except TencentCloudSDKException as err:
        print(err)
    return


# 用于AB结构下的触发器更新
def ABTrigUpdate(AnotherFunctionName, AnotherRegion, AnotherNamespace, TriggerName):
    global SecretId, SecretKey, Region
    try:
        cred = credential.Credential(SecretId, SecretKey)
        client = scf_client.ScfClient(cred, AnotherRegion)
    except TencentCloudSDKException as err:
        print(err)
    # 删除旧触发器
    try:
        req = models.DeleteTriggerRequest()
        params = '{"FunctionName":"' + AnotherFunctionName + '",'
        params += '"TriggerName":"' + TriggerName + '",'
        params += '"Namespace":"' + AnotherNamespace + '",'
        params += '"Type":"timer"}'
        req.from_json_string(params)
        resp = client.DeleteTrigger(req)
        print(resp.to_json_string())
    except TencentCloudSDKException as err:
        print(err)

    # 添加新触发器
    try:
        next_time = time.time()
        next_time += random.randint(random_time_lowerlimit,
                                    random_time_toplimit)

        req = models.CreateTriggerRequest()
        params = '{"FunctionName":"' + AnotherFunctionName + '",'
        params += '"TriggerName":"' + TriggerName + '",'
        params += '"Namespace":"' + AnotherNamespace + '",'
        params += '"Type":"timer",'
        params += '"Enable":"OPEN",'
        params += '"TriggerDesc":"' + \
            to_china_timezone_cron(next_time) + '"}'
        req.from_json_string(params)
        resp = client.CreateTrigger(req)
        print(resp.to_json_string())
    except TencentCloudSDKException as err:
        print(err)
    return


# 用于主从结构下的触发器更新
def MSTrigUpdate_Master(AnotherFunctionName, AnotherRegion, AnotherNamespace, TriggerName, FunctionName, Namespace):
    global SecretId, SecretKey, Region
    try:
        cred = credential.Credential(SecretId, SecretKey)
        client = scf_client.ScfClient(cred, AnotherRegion)
    except TencentCloudSDKException as err:
        print(err)
    # 启动从函数
    pass_params = {
        "FunctionName": FunctionName,
        "Region": Region,
        "Namespace": Namespace,
        "TriggerName": TriggerName,
        "SecretId": SecretId,
        "SecretKey": SecretKey
    }
    pass_params_str = json.dumps(pass_params)
    req = models.InvokeRequest()
    params = '{"FunctionName":"' + AnotherFunctionName + '",'
    params += '"InvocationType":"Event",'
    params += '"ClientContext":"' + pass_params_str + '",'
    params += '"Namespace":"' + AnotherNamespace + '"}'
    req.from_json_string(params)
    return


def MSTrigUpdate_Slave(event, content):
    FunctionName = content["FunctionName"]
    Region = content["Region"]
    Namespace = content["Namespace"]
    TriggerName = content["TriggerName"]
    SecretId = content["SecretId"]
    SecretKey = content["SecretKey"]
    ABTrigUpdate(FunctionName, Region,
                 Namespace, TriggerName)
    return

def to_china_timezone_cron(timestamp): return time.strftime(
    "%S %M %H %d %m * %Y", time.gmtime(timestamp+8*60*60))
