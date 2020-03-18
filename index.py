import requests as req
import json
import os
from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.scf.v20180416 import scf_client, models

# 定义关于Azure AD的变量
# 规范：使用全小写，中间用下划线连接
ms_id = ""
ms_secret = ""
refresh_token = ""

# 定义关于腾讯云的变量
# 规范：全部单词首字母大写，中间无连接符号
SecretId = ""
SecretKey = ""

FunctionName = ""
Namespace = ""
Region = ""


# 微软api列表，直接复制粘贴自原脚本
api_list = [
    r"https://graph.microsoft.com/v1.0/me/drive/root",
    r"https://graph.microsoft.com/v1.0/me/drive",
    r"https://graph.microsoft.com/v1.0/users",
    r"https://graph.microsoft.com/v1.0/me/messages",
    r"https://graph.microsoft.com/v1.0/me/mailFolders/inbox/messageRules",
    r"https://graph.microsoft.com/v1.0/me/mailFolders/inbox/messageRules",
    r"https://graph.microsoft.com/v1.0/me/drive/root/children",
    r"https://api.powerbi.com/v1.0/myorg/apps",
    r"https://graph.microsoft.com/v1.0/me/mailFolders",
    r"https://graph.microsoft.com/v1.0/me/outlook/masterCategories"
]


# 写入环境变量（主要是为了更新refresh_token供下次使用）
def envwrite():
    req = models.UpdateFunctionConfigurationRequest()
    params = '{"FunctionName":"' + FunctionName + '",'
    params += '"Environment":{"Variables":['
    params += '{"Key":"Region","Value":"' + Region + '"},'
    params += '{"Key":"refresh_token","Value":"' + refresh_token + '"},'
    params += '{"Key":"ms_id","Value":"' + ms_id + '"},'
    params += '{"Key":"ms_secret","Value":"' + ms_secret + '"},'
    params += '{"Key":"SecretId","Value":"' + SecretId + '"},'
    params += '{"Key":"SecretKey","Value":"' + SecretKey + '"}]}}'
    req.from_json_string(params)
    print(req)
    try:
        # 以下照抄腾讯云sdk例程
        cred = credential.Credential(SecretId, SecretKey)
        client = scf_client.ScfClient(cred, Region)
        resp = client.UpdateFunctionConfiguration(req)

        print(resp.to_json_string())

    except TencentCloudSDKException as err:
        print(err)
    pass


def getapi(url, headers):
    if req.get(url, headers=headers).status_code == 200:
        print("调用"+url+"成功")


# 拿到最新的access_token，顺便更新环境变量里的refresh_token
def gettoken():
    global refresh_token
    headers = {"Content-Type": "application/x-www-form-urlencoded"
               }
    data = {"grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": ms_id,
            "client_secret": ms_secret,
            "redirect_uri": "http://localhost:53682/"
            }
    html = req.post(
        "https://login.microsoftonline.com/common/oauth2/v2.0/token", data=data, headers=headers)
    jsontxt = json.loads(html.text)
    refresh_token = jsontxt["refresh_token"]
    access_token = jsontxt["access_token"]
    envwrite()
    return access_token


def exe(event, content):
    # 全局变量要手动指定才能修改……
    global FunctionName, Namespace, ms_id, ms_secret, SecretId, SecretKey, Region, refresh_token

    # 从api入参处读取
    FunctionName = content["function_name"]
    Namespace = content["namespace"]

    # 获取环境变量用的字符串是一大坑点！
    # 为什么Python没有nameof方法？？
    # （然而如果一开始就规范好变量命名规则就没那么多事了

    # 读取环境变量中的微软应用api
    ms_id = os.environ.get("ms_id")
    ms_secret = os.environ.get("ms_secret")

    # 读取环境变量中的腾讯云api
    SecretId = os.environ.get("SecretId")
    SecretKey = os.environ.get("SecretKey")

    # 读取环境变量中的腾讯云地域
    Region = os.environ.get("Region")

    # 读取环境变量中的refresh_token
    refresh_token = os.environ.get("refresh_token")

    access_token = gettoken()
    headers = {
        "Authorization": access_token,
        "Content-Type": "application/json"
    }
    try:
        for api in api_list:
            getapi(api, headers)
    except:
        print("pass")
        pass
