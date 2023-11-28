import requests
import os
import sys
import yaml
from configmanager import ConfigManager
from wxpush import WeChatPush
from loguru import logger
from datetime import datetime


@logger.catch
def read_power_balance():
    # 如果存在 .power.yaml 文件，则读取其中的电费余额
    if os.path.exists('.power.yaml'):
        with open('.power.yaml', 'r') as file:
            power_data = yaml.safe_load(file)
            return power_data.get('balance', 0)
    else:
        # 如果文件不存在
        logger.info("首次运行,不计算用量")
        return 0


@logger.catch
def write_power_balance(balance):
    # 获取当前时间
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    power_data = {'balance': balance, 'last_updated': now}

    # 写入当次的余额
    with open('.power.yaml', 'a') as file:
        yaml.dump(power_data, file, default_flow_style=False)
        file.write('\n')  # 添加换行，以便下次写入的内容位于新的一行


@logger.catch
def compare_and_print_difference(current_balance, previous_balance):
    if not previous_balance:
        return 0
    else:
        difference = current_balance - previous_balance
        return difference


@logger.catch
def main():
    ver = '1.0'

    logger.info('--------------------')
    logger.info('Copyright (C) 2023 kodesu, Inc. All Rights Reserved ')
    logger.info('Date    : 2023-11')
    logger.info('Author  : kodesu')
    logger.info('Blog    : https://kookoo.top')
    logger.info('Github  : https://github.com/Xingsandesu/wbu_power_message_push')
    logger.info(f"Ver     : {ver}")
    logger.warning("此Api可能随时被封堵，cookies填写不正确或者过期可能会被一卡通服务器暂时拉黑，请谨慎使用此工具！！！")
    logger.warning("仅供学习使用，本人不负任何责任！！！")
    logger.info('--------------------')

    # 获取当前脚本所在的文件夹路径
    if getattr(sys, 'frozen', False):
        current_path = os.path.dirname(sys.executable)
    else:
        current_path = os.path.dirname(os.path.abspath(__file__))

    os.chdir(current_path)
    current_dir = os.getcwd()
    logger.info(f"当前工作目录:{current_dir}")

    config_file_path = os.path.join(current_dir, ConfigManager.CONFIG_FILE_NAME)
    logger.info(f"配置文件工作目录:{config_file_path}")

    try:
        config = ConfigManager.load_config()
        building = config['WBUPower']['Building']
        roomid = config['WBUPower']['Roomid']
        cookies = config['WBUPower']['Cookies']
        corpid = config['WBUPower']['Corp_id']
        agentid = config['WBUPower']['Agentid']
        corpsecret = config['WBUPower']['Corp_secret']
    except NameError:
        logger.error("请检查配置文件，确认相关信息是否正确，服务器是否能够正常访问，XML-PRC接口是否开启")

    try:
        logger.info(f"楼栋号:{building}")
        logger.info(f"房间号:{roomid}")
        logger.info(f"Cookies:{cookies}")
        logger.info(f"企业微信企业id值:{corpid}")
        logger.info(f"企业微信应用secret值:{corpsecret}")
        logger.info(f"企业微信应用Agentid值:{agentid}")
    except NameError:
        logger.error("无法加载配置文件")

    try:
        wechat_push = WeChatPush(corpid, corpsecret, agentid)
    except KeyError:
        logger.error("企业微信配置错误，请检查企业微信相关配置")
    except NameError:
        logger.error("企业微信配置错误，请检查企业微信相关配置")

    api_url = (
        f'http://yktyd.wbu.edu.cn/wechat/basicQuery/queryElecRoomInfo.html'
        f'?'
        f'aid=0030000000001401'
        f'&'
        f'area={{"area":"","areaname":""}}'
        f'&'
        f'building={{"building":"{building}","buildingid":"42"}}'
        f'&'
        f'floor={{"floorid":"","floor":""}}'
        f'&'
        f'room={{"room":"","roomid":"{roomid}"}}'
    )

    headers = {'Cookie': '; '.join([f'{key}={value}' for key, value in cookies.items()])}
    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        balance_str = data['errmsg'].split('账户余额:')[1].split(' 元！')[0]
        building_number = data['building']['building']
        room_number = data['room']['roomid']
        balance = float(balance_str)
        # 读取之前保存的电费余额
        previous_balance = read_power_balance()
        # 将当前电费余额和时间写入文件
        write_power_balance(balance)
        # 比较两个电费余额并打印差值
        difference_value = compare_and_print_difference(balance, previous_balance)
        logger.info(f'距离上次查询，您已用电费{difference_value:.2f} 元')
        wechat_push.send_text_message(f'距离上次查询，您已用电费{difference_value:.2f} 元')
        if balance < 3:
            logger.warning(
                f"{building_number}-{room_number}:账户余额: {balance} 元,警告：账户余额低于3元！请尽快充值以免断电！")
            wechat_push.send_text_message(
                f"{building_number}-{room_number}:账户余额: {balance} 元,警告：账户余额低于3元！请尽快充值以免断电！")
        else:
            logger.info(f"{building_number}-{room_number}:账户余额: {balance} 元")
            wechat_push.send_text_message(f"{building_number}-{room_number}:账户余额: {balance} 元")
    else:
        logger.error("API 请求失败，状态码:", response.status_code)
        wechat_push.send_text_message(f"API 请求失败，状态码: {response.status_code}")
        logger.error("错误信息:", response.text)
        wechat_push.send_text_message(f"错误信息: {response.text}")


if __name__ == '__main__':
    log_folder = "logs"
    os.makedirs(log_folder, exist_ok=True)
    logger.add(os.path.join(log_folder, "{time}.log"), enqueue=True)
    main()
