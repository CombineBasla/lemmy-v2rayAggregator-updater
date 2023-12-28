import os
import sys
import argparse
import logging
import requests
import yaml
from pythorhead import Lemmy
from pythorhead.types import LanguageType

# 创建解析器并添加日志级别参数
parser = argparse.ArgumentParser()
parser.add_argument(
    "-l",
    "--log",
    help="Set the log level",
    choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
    default="INFO",
)

# 解析命令行参数
args = parser.parse_args()

# 获取传入的日志级别并设置日志配置
level = getattr(logging, args.log)
logging.basicConfig(
    level=level,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S%z",
)

# 从 'config.yaml' 读取配置
with open("config.yaml", "r") as yaml_file:
    config_root = yaml.safe_load(yaml_file)

# 从配置文件获取 Lemmy 参数
config_lemmy = config_root["lemmy"]
lemmy_url = config_lemmy["lemmy_url"]
request_timeout = config_lemmy["request_timeout"]
comment_id_list = config_lemmy["comment_id_list"]
username = config_lemmy["username"]

# 设置 Lemmy 发贴语言
language_id = LanguageType.ZH  # 中文

# 从环境变量获取 Lemmy 用户密码
password = os.getenv("LEMMY_BOT_PASSWORD")
if not username or not password:
    print("Bot useranem or password not set")
    sys.exit(1)

# 从配置文件获取 v2rayAggregator 参数
links_url = config_root["v2rayAggregator"]["links_url"]

# 尝试登录 Lemmy ，最多重试三次
lemmy = Lemmy(lemmy_url, request_timeout=5)
max_attempts = 3
attempts = 0

while attempts < max_attempts:
    success = lemmy.log_in(username, password)
    if success:
        logging.info("Login successful!")
        break  # 退出循环
    else:
        attempts += 1
        logging.info(f"Login failed, retrying... ({attempts}/{max_attempts})")
        time.sleep(5)  # 等待 5 秒后再重试

if attempts == max_attempts:
    logging.error(
        "Too many failed login attempts, please check your credentials or try again later."
    )

# Comment 模板
template = """
# Part {index}

```
{links}
```
"""

# 获取 200 行链接，每行一条，转为列表
response = requests.get(links_url)
link_list = response.text.split("\n")

# 遍历 Comments
for i, comment_id in enumerate(comment_id_list):
    index = i + 1

    # 每 20 条组成一部分
    parted_link_list = link_list[i * 20 : (i + 1) * 20]
    links = "\n".join(parted_link_list)

    # 更新所有 Comments
    lemmy.comment.edit(
        comment_id=comment_id,
        content=template.format(index=index, links=links),
        form_id=None,
        language_id=language_id,
    )
    logging.info(f"Comment (Part {index}) is updated.")
