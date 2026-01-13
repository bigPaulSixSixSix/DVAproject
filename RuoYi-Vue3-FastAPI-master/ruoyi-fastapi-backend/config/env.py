import argparse
import configparser
import os
import sys
from dotenv import load_dotenv
from functools import lru_cache
from pydantic import Field, computed_field
from pydantic_settings import BaseSettings
from typing import Literal


class AppSettings(BaseSettings):
    """
    应用配置
    所有配置必须从环境变量读取，不使用代码默认值
    """

    app_env: str = Field(..., description="应用运行环境")
    app_name: str = Field(..., description="应用名称")
    app_root_path: str = Field(..., description="应用代理路径")
    app_host: str = Field(..., description="应用主机")
    app_port: int = Field(..., description="应用端口")
    app_version: str = Field(..., description="应用版本")
    app_reload: bool = Field(..., description="应用是否开启热重载")
    app_ip_location_query: bool = Field(..., description="应用是否开启IP归属区域查询")
    app_same_time_login: bool = Field(..., description="应用是否允许账号同时登录")


class JwtSettings(BaseSettings):
    """
    Jwt配置
    所有配置必须从环境变量读取，不使用代码默认值
    """

    jwt_secret_key: str = Field(..., description="Jwt秘钥")
    jwt_algorithm: str = Field(..., description="Jwt算法")
    jwt_expire_minutes: int = Field(..., description="令牌过期时间（分钟）")
    jwt_redis_expire_minutes: int = Field(..., description="redis中令牌过期时间（分钟）")


class DataBaseSettings(BaseSettings):
    """
    数据库配置
    所有配置必须从环境变量读取，不使用代码默认值
    """

    db_type: Literal["mysql", "postgresql"] = Field(..., description="数据库类型")
    db_host: str = Field(..., description="数据库主机")
    db_port: int = Field(..., description="数据库端口")
    db_username: str = Field(..., description="数据库用户名")
    db_password: str = Field(..., description="数据库密码")
    db_database: str = Field(..., description="数据库名称")
    db_echo: bool = Field(..., description="是否开启sqlalchemy日志")
    db_max_overflow: int = Field(..., description="允许溢出连接池大小的最大连接数")
    db_pool_size: int = Field(..., description="连接池大小")
    db_pool_recycle: int = Field(..., description="连接回收时间（秒）")
    db_pool_timeout: int = Field(..., description="连接池等待超时时间（秒）")

    @computed_field
    @property
    def sqlglot_parse_dialect(self) -> str:
        if self.db_type == "postgresql":
            return "postgres"
        return self.db_type


class RedisSettings(BaseSettings):
    """
    Redis配置
    所有配置必须从环境变量读取，不使用代码默认值
    """

    redis_host: str = Field(..., description="Redis主机")
    redis_port: int = Field(..., description="Redis端口")
    redis_username: str = Field(default="", description="Redis用户名")
    redis_password: str = Field(default="", description="Redis密码")
    redis_database: int = Field(..., description="Redis数据库编号")


class GenSettings:
    """
    代码生成配置
    """

    author = "insistence"
    package_name = "module_admin.system"
    auto_remove_pre = False
    table_prefix = "sys_"
    allow_overwrite = False

    GEN_PATH = "vf_admin/gen_path"

    def __init__(self):
        if not os.path.exists(self.GEN_PATH):
            os.makedirs(self.GEN_PATH)


class UploadSettings:
    """
    上传配置
    """

    UPLOAD_PREFIX = "/profile"
    UPLOAD_PATH = "vf_admin/upload_path"
    UPLOAD_MACHINE = "A"
    DEFAULT_ALLOWED_EXTENSION = [
        # 图片
        "bmp",
        "gif",
        "jpg",
        "jpeg",
        "png",
        # word excel powerpoint
        "doc",
        "docx",
        "xls",
        "xlsx",
        "ppt",
        "pptx",
        "html",
        "htm",
        "txt",
        # 压缩文件
        "rar",
        "zip",
        "gz",
        "bz2",
        # 视频格式
        "mp4",
        "avi",
        "rmvb",
        # pdf
        "pdf",
    ]
    DOWNLOAD_PATH = "vf_admin/download_path"

    def __init__(self):
        if not os.path.exists(self.UPLOAD_PATH):
            os.makedirs(self.UPLOAD_PATH)
        if not os.path.exists(self.DOWNLOAD_PATH):
            os.makedirs(self.DOWNLOAD_PATH)


class CachePathConfig:
    """
    缓存目录配置
    """

    PATH = os.path.join(os.path.abspath(os.getcwd()), "caches")
    PATHSTR = "caches"


class GetConfig:
    """
    获取配置
    """

    def __init__(self):
        self.parse_cli_args()

    @lru_cache()
    def get_app_config(self):
        """
        获取应用配置
        """
        # 实例化应用配置模型
        return AppSettings()

    @lru_cache()
    def get_jwt_config(self):
        """
        获取Jwt配置
        """
        # 实例化Jwt配置模型
        return JwtSettings()

    @lru_cache()
    def get_database_config(self):
        """
        获取数据库配置
        """
        # 实例化数据库配置模型
        return DataBaseSettings()

    @lru_cache()
    def get_redis_config(self):
        """
        获取Redis配置
        """
        # 实例化Redis配置模型
        return RedisSettings()

    @lru_cache()
    def get_gen_config(self):
        """
        获取代码生成配置
        """
        # 实例化代码生成配置
        return GenSettings()

    @lru_cache()
    def get_upload_config(self):
        """
        获取数据库配置
        """
        # 实例上传配置
        return UploadSettings()

    @staticmethod
    def parse_cli_args():
        """
        解析命令行参数
        """
        # 检查是否在alembic环境中运行，如果是则跳过参数解析
        if "alembic" in sys.argv[0] or any("alembic" in arg for arg in sys.argv):
            ini_config = configparser.ConfigParser()
            ini_config.read("alembic.ini", encoding="utf-8")
            if "settings" in ini_config:
                # 获取env选项
                env_value = ini_config["settings"].get("env")
                # 如果alembic.ini中未设置env，不设置APP_ENV（默认加载.env.prod）
                if env_value:
                    os.environ["APP_ENV"] = env_value
        elif "uvicorn" in sys.argv[0]:
            # 使用uvicorn启动时，命令行参数需要按照uvicorn的文档进行配置，无法自定义参数
            pass
        else:
            # 使用argparse定义命令行参数
            parser = argparse.ArgumentParser(description="命令行参数")
            parser.add_argument("--env", type=str, default="", help="运行环境")
            # 解析命令行参数
            args = parser.parse_args()
            # 设置环境变量，如果未设置命令行参数，不设置APP_ENV（默认加载.env.prod）
            if args.env:
                os.environ["APP_ENV"] = args.env
        # 读取运行环境
        run_env = os.environ.get("APP_ENV", "")
        # 运行环境未指定时默认加载.env.prod（生产环境配置）
        env_file = ".env.prod"
        # 运行环境不为空时按命令行参数加载对应.env文件
        if run_env != "":
            env_file = f".env.{run_env}"
        # 加载配置
        load_dotenv(env_file)


# 实例化获取配置类
get_config = GetConfig()
# 应用配置
AppConfig = get_config.get_app_config()
# Jwt配置
JwtConfig = get_config.get_jwt_config()
# 数据库配置
DataBaseConfig = get_config.get_database_config()
# Redis配置
RedisConfig = get_config.get_redis_config()
# 代码生成配置
GenConfig = get_config.get_gen_config()
# 上传配置
UploadConfig = get_config.get_upload_config()
