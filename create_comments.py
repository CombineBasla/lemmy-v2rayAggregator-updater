import yaml
from pythorhead import Lemmy
from pythorhead.types import LanguageType

# 从 'config.yaml' 读取配置
with open("config.yaml", "r") as yaml_file:
    config_root = yaml.safe_load(yaml_file)

# 从配置文件获取 Lemmy 参数
config_lemmy = config_root["lemmy"]
lemmy_url = config_lemmy["lemmy_url"]
request_timeout = config_lemmy["request_timeout"]
username = config_lemmy["username"]
community = config_lemmy["community"]
post_id = config_lemmy["post_id"]

# 设置 Lemmy 发贴语言
language_id = LanguageType.ZH  # 中文

# 从环境变量获取 Lemmy 用户密码
password = os.getenv("LEMMY_BOT_PASSWORD")
if not username or not password:
    print("Bot useranem or password not set")
    sys.exit(1)

# 登陆 Lemmy
lemmy = Lemmy(lemmy_url, request_timeout)
lemmy.log_in(username, password)
community_id = lemmy.discover_community(community)

# 循环发 10 个贴
for i in range(10):
    lemmy.comment.create(
        post_id=post_id,
        content=f"Placeholder {i}",
        form_id=None,
        parent_id=None,
        language_id=language_id,
    )
