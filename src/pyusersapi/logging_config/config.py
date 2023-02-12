import logging.config
import yaml


def init():
    with open('../pyusersapi/config/logging.yaml', 'r') as stream:
        config = yaml.load(stream, Loader=yaml.FullLoader)
        logging.config.dictConfig(config)
