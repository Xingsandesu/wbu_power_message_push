import re

from loguru import logger
from mitmproxy import http

import configmanager

# 目标网站
target_url = "yktyd.wbu.edu.cn"
# 目标URL特征
target_url_pattern = re.compile(r'http://yktyd\.wbu\.edu\.cn/wechat/home/index\.html\?.*')


@logger.catch
def update_jsessionid_in_config(jsessionid_value):
    try:
        config = configmanager.ConfigManager.load_config()

        # 更新 JSESSIONID 值
        config['WBUPower']['Cookies']['JSESSIONID'] = jsessionid_value

        # 写回配置文件
        configmanager.ConfigManager.save_config(config)
    except NameError:
        logger.error("请检查配置文件，确认相关信息是否正确")


@logger.catch
def request(flow: http.HTTPFlow) -> None:
    # 检查是否为目标网站
    if target_url in flow.request.pretty_host:
        # 获取请求的URL
        request_url = flow.request.url

        # 检查请求的URL是否符合特定特征
        if target_url_pattern.search(request_url):
            # 提取并打印符合条件的URL
            logger.info(f"请求的原始URL: {request_url}")

            if 'token=' in flow.request.url:
                # new_token = "newToken"
                # new_json = "newJson"

                # 找到 token json 的起始位置
                start_index_token = flow.request.url.find('token=') + len('token=')
                start_index_json = flow.request.url.find('json=') + len('json=')

                # 找到 token json 值的结束位置
                end_index_token = flow.request.url.find('&', start_index_token) if '&' in flow.request.url[
                                                                                          start_index_token:] else None
                end_index_json = flow.request.url.find('&', start_index_json) if '&' in flow.request.url[
                                                                                        start_index_json:] else None

                # 提取原始 token 的值
                old_token = flow.request.url[start_index_token:end_index_token]
                logger.info(f"提取的token: {old_token}")

                # 提取原始 json 的值
                old_json = flow.request.url[start_index_json:end_index_json]
                logger.info(f"提取的json: {old_json}")

                # 使用新的 token 替换原始 token
                # modified_url_token = flow.request.url.replace(old_token, new_token)
                # 使用新的 json 替换原始 json
                # modified_url_json = modified_url_token.replace(old_json, new_json)

                # 伪造请求
                # flow.request.url = modified_url_json
                # logger.info(f"劫持后的URL: {flow.request.url}")
            else:
                # 如果 URL 中不存在 token，返回原始 URL
                logger.error("没有找到token")

            # 获取 Cookies
            cookies = flow.request.headers.get("Cookie", "")

            # 在 Cookies 中查找 JSESSIONID 的值
            jsessionid_match = re.search(r'JSESSIONID=(\w+)', cookies)
            if jsessionid_match:
                jsessionid_value = jsessionid_match.group(1)

                # 输出到控制台
                logger.info(f"获取到的 JSESSIONID: {jsessionid_value}")

                # 更新配置文件中的 JSESSIONID 值
                update_jsessionid_in_config(jsessionid_value)


# 启动 mitmproxy
if __name__ == "__main__":
    from mitmproxy.tools.main import mitmdump

    logger.info("代理已开启，端口8080")

    mitmdump(["-s", __file__])
