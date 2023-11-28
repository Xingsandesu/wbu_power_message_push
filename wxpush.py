import requests
import json


class WeChatPush:
    def __init__(self, corpid, corpsecret, agentid):
        self.corpid = corpid
        self.corpsecret = corpsecret
        self.agentid = agentid
        self.access_token = self.get_access_token()

    def send_text_message(self, message):
        send_text_url = "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={}".format(self.access_token)
        data = {
            "touser": "@all",
            "msgtype": "text",
            "agentid": self.agentid,
            "text": {
                "content": message
            },
            "safe": 0,
        }
        text_message_res = requests.post(url=send_text_url, data=json.dumps(data)).json()
        return text_message_res

    def get_media_id(self, filetype, path):
        upload_file_url = "https://qyapi.weixin.qq.com/cgi-bin/media/upload?access_token={}&type={}".format(
            self.access_token, filetype)
        files = {filetype: open(path, 'rb')}
        file_upload_result = requests.post(upload_file_url, files=files).json()
        return file_upload_result["media_id"]

    def send_picture_message(self, media_id):
        send_picture_url = "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={}".format(self.access_token)
        data = {
            "touser": "@all",
            "msgtype": "image",
            "agentid": self.agentid,
            "image": {
                "media_id": media_id
            },
            "safe": 0,
        }
        picture_message_res = requests.post(url=send_picture_url, data=json.dumps(data)).json()
        return picture_message_res

    def get_access_token(self):
        get_act_url = "https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={}&corpsecret={}".format(
            self.corpid, self.corpsecret)
        act_res = requests.get(url=get_act_url).json()
        access_token = act_res["access_token"]
        return access_token
