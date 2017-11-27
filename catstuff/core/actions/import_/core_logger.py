import logging, logging.handlers
import catstuff.tools.common
import os

_dir = os.path.dirname(os.path.realpath(__file__))

log_file = os.path.join(_dir, '../logs/core/plugins.log')
catstuff.tools.common.touch(log_file)
# logging.basicConfig(filename=log_file, level=logging.DEBUG)

log_handler = logging.handlers.RotatingFileHandler(log_file, mode='a', maxBytes=10*1024*1024,
                                                   backupCount=2, encoding=None, delay=0)
log_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s - %(names)s - %(funcName)s(%(lineno)d): %(message)s'
))
log_handler.setLevel(logging.DEBUG)

logger = logging.getLogger('modules')
logger.setLevel(logging.DEBUG)
logger.addHandler(log_handler)  # fix this