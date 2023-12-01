import os

import yaml
from loguru import logger


class ConfigManager:
    """
    配置文件检查
    """
    CONFIG_FILE_NAME = 'config.yaml'

    @staticmethod
    def get_default_config():
        """
        默认的配置信息，如果配置文件缺失或配置项缺失，则会使用这里定义的默认值
        """
        return {
            'WBUPower': {
                'Corp_id': r'企业微信 Corp_id',
                'Corp_secret': r'企业微信 Corp_secret',
                'Agentid': r'企业微信 Agentid',
                'Building': r'观湖苑X栋',
                'Roomid': r'房间号,例如222',
                'adbinputone': 'adb shell input tap 730 1962',
                'adbinputtwo': 'adb shell input tap 415 555',
                'hostip': '填运行脚本的ip',
                'Cookies': {'JSESSIONID': ''},
                'Url': ''
            }
        }

    @classmethod
    def load_config(cls):
        """
        这里是 Config.yaml 生成以及检测相关
        """
        # 检查配置文件是否存在
        if os.path.exists(cls.CONFIG_FILE_NAME):
            # 如果配置文件存在，尝试加载配置数据
            with open(cls.CONFIG_FILE_NAME, 'r', encoding='utf-8') as config_file:
                config_content = config_file.read()
                # 如果配置文件内容为空，则使用默认配置
                if not config_content.strip():
                    logger.error("配置文件为空，将使用默认配置。")
                    config_data = cls.get_default_config()
                else:
                    try:
                        config_data = yaml.safe_load(config_content)
                        if not isinstance(config_data, dict):
                            # 如果配置文件中只有字典名而没有键值对，则使用默认配置
                            logger.error("配置文件内容不正确，将使用默认配置。")
                            config_data = cls.get_default_config()
                        elif 'WBUPower' not in config_data:
                            # 如果配置文件中没有WBUPower字段，则使用默认配置
                            logger.error("配置文件缺少WBUPower字段，将使用默认配置。")
                            config_data['WBUPower'] = cls.get_default_config()['WBUPower']
                        elif not isinstance(config_data['WBUPower'], dict):
                            # 如果WBUPower字段的值不是一个字典，则使用默认配置
                            logger.error("WBUPower字段内容不正确，将使用默认配置。")
                            config_data['WBUPower'] = cls.get_default_config()['WBUPower']
                    except yaml.YAMLError:
                        # 如果配置文件内容不正确，打印错误信息，使用默认配置
                        logger.error("配置文件内容不正确，将使用默认配置。")
                        config_data = cls.get_default_config()
        else:
            # 如果配置文件不存在，打印信息，使用默认配置
            config_data = cls.get_default_config()
            logger.error("配置文件不存在，将使用默认配置。")

        # 确保配置文件中包含WBUPower字典，并添加缺失的键
        # setdefault函数在config_data字典中查找'WBUPower'键
        typecho_config = config_data.setdefault('WBUPower')
        # 获取默认配置中的WBUPower字典
        default_typecho_config = cls.get_default_config()['WBUPower']
        for key, value in default_typecho_config.items():
            # 对于默认配置中的每个键值对，检查是否在配置文件中，如果不存在，则添加该键值对
            typecho_config.setdefault(key, value)

        # 保存配置数据，以确保缺失的键值对得到添加或更新
        cls.save_config(config_data)

        # 返回配置数据
        return config_data

    @classmethod
    def save_config(cls, config_data):
        """
        将配置数据保存到配置文件
        """
        with open(cls.CONFIG_FILE_NAME, 'w', encoding='utf-8') as config_file:
            # 使用 ensure_ascii=False 以防止Unicode转义序列
            yaml.dump(config_data, config_file, allow_unicode=True, default_flow_style=False, encoding=None,
                      sort_keys=False)
