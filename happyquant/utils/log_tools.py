from loguru import logger

def output(content, log_type='info'):
    if log_type == 'info':
        logger.info(content)
    else:
        print('Log Type not supported')