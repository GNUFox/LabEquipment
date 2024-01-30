import logging
from labequipment.framework.globals import GlobalDefaults


def setup_custom_logger(name, stdout_level=logging.DEBUG, file_level=logging.DEBUG):
    logger = logging.getLogger(name)
    formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - [%(module)s] %(message)s')
    logger.setLevel(logging.DEBUG)

    stdout_handler = logging.StreamHandler()
    stdout_handler.setLevel(stdout_level)
    stdout_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(GlobalDefaults.debug_log_path)
    file_handler.setLevel(file_level)
    file_handler.setFormatter(formatter)

    # logger.setLevel(stdout_level)
    logger.addHandler(stdout_handler)
    logger.addHandler(file_handler)
    return logger


setup_custom_logger('root', stdout_level=logging.DEBUG, file_level=logging.DEBUG)
