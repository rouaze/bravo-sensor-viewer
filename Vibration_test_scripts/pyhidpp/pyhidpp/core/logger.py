import logging


def get_pyhidpp_logger(log_level=logging.INFO, log_to_file=False, log_to_console=True):
    logger = logging.getLogger("hidpp")
    if not logger.hasHandlers():
        logger.propagate = False
        formatter = logging.Formatter(
            "%(asctime)s :: %(name)s :: %(levelname)-8s :: %(message)s"
        )
        logger.setLevel(log_level)
        logger.disabled = not log_to_file and not log_to_console
        if log_to_file:
            file_handler = logging.FileHandler("hidpp.log", mode="a")
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        if log_to_console:
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(formatter)
            logger.addHandler(stream_handler)
    return logger
