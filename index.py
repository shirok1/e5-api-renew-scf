import requests as req
import json
import os
import ScfOperate


# 获取环境变量用的字符串是一大坑点！
# 为什么Python没有nameof方法？？
# （然而如果一开始就规范好变量命名规则就没那么多事了

# 定义关于Azure AD的变量
# 规范：使用全小写，中间用下划线连接

# 读取环境变量中的微软应用api
ms_id = ""
ms_secret = ""

# 读取环境变量中的refresh_token
refresh_token = ""

# 定义关于腾讯云的变量
# 规范：全部单词首字母大写，中间无连接符号
FunctionName = ""
Namespace = ""
# 下面是递归触发相关
TrigUpdateType = ""
AnotherFunctionName = ""
AnotherRegion = ""
AnotherNamespace = ""
TriggerName = ""
TriggerName_Default = "RandomTimer"

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


def get_api(url, headers):
    return req.get(url, headers=headers).status_code == 200


# 拿到最新的access_token
def get_token():
    global refresh_token, ms_id, ms_secret
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
    return access_token


def exe(event, content):
    # 全局变量要手动指定才能修改……
    global FunctionName, Namespace

    global ms_id, ms_secret, refresh_token

    # 读取环境变量中的微软应用api
    ms_id = os.environ.get("ms_id")
    ms_secret = os.environ.get("ms_secret")

    # 读取环境变量中的refresh_token
    refresh_token = os.environ.get("refresh_token")

    ScfOperate.SecretId = os.environ.get("SecretId")
    ScfOperate.SecretKey = os.environ.get("SecretKey")
    ScfOperate.Region = os.environ.get("Region")

    # 从api入参处读取
    FunctionName = content["function_name"]
    Namespace = content["namespace"]

    access_token = get_token()
    headers = {
        "Authorization": access_token,
        "Content-Type": "application/json"
    }
    try:
        for api in api_list:
            get_api(api, headers)
    except:
        print("出现错误，跳过剩余")
    print("API触发结束")
    # 设定下一个触发时间
    # ScfOperate.TrigUpdate(FunctionName, Namespace, TriggerName)

    # 经过确认，运行状态下的云函数的触发器不能被修改
    # 因此在云函数系统更新前，只能使用双函数递归调用实现随机时间
    # 有AB、主从两种方案，干脆都写了
    global TrigUpdateType
    TrigUpdateType = os.environ.get("TrigUpdateType")
    if not TrigUpdateType:
        print("TrigUpdateType为空，将不会尝试设置随机时间")
        ScfOperate.EnvWrite(FunctionName, Namespace, ms_id,
                        ms_secret, refresh_token)
        return
    global AnotherFunctionName, AnotherRegion, AnotherNamespace, TriggerName

    AnotherFunctionName = os.environ.get("AnotherFunctionName")
    if not AnotherFunctionName:
        print("AnotherFunctionName为空，将不会尝试设置随机时间")
        return
    
    AnotherRegion = os.environ.get("AnotherRegion")
    if not AnotherRegion:
        print("AnotherRegion为空，将会默认为相同")
        AnotherRegion = os.environ.get("Region")
    
    AnotherNamespace = os.environ.get("AnotherNamespace")
    if not AnotherNamespace:
        print("AnotherNamespace为空，将会默认为相同")
        AnotherNamespace = Namespace

    TriggerName = os.environ.get("AnotherTriggerName")
    if not TriggerName:
        print("TriggerName为空，将会使用默认值" + TriggerName_Default)
        TriggerName = TriggerName_Default
    
    # 类型判断
    if TrigUpdateType == "AB":
        print("TrigUpdateType为A+B型")
        ScfOperate.ABTrigUpdate(AnotherFunctionName,
                                AnotherRegion, AnotherNamespace, TriggerName)
    elif TrigUpdateType == "MS":
        print("TrigUpdateType为M+S型")
        ScfOperate.MSTrigUpdate_Master(AnotherFunctionName, AnotherRegion,
            AnotherNamespace, TriggerName, FunctionName, Namespace)
    Another = {
        "TrigUpdateType": TrigUpdateType,
        "AnotherFunctionName": AnotherFunctionName,
        "AnotherRegion": os.environ.get("AnotherRegion"),
        "AnotherNamespace": os.environ.get("AnotherNamespace"),
        "TriggerName": os.environ.get("TriggerName"),
    }
    #print(Another)
    ScfOperate.EnvWrite(FunctionName, Namespace, ms_id,
                        ms_secret, refresh_token, Another)
    return
