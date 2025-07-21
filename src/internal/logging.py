import yaml
import logging.config

# 配置日志


def setup_logging(config_path: str):
    logging.config.dictConfig(yaml.safe_load(open(config_path)))
