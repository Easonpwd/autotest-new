from dataclasses import dataclass


@dataclass
class Research:
    URL: str = "URLxxxx"


@dataclass
class BaseConfig:
    """
    基础配置类
    """
    update_image: bool = False  # 是否更新脑图
    auto_fill: bool = False  # 是否自动填充图片


User = ['User']
