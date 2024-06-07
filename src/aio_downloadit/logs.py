"""to config logs of the program"""

import logging

logger = logging.getLogger("aio_downloadit")

s_formater = logging.Formatter(
    "[%(levelname)s]: occured at %(asctime)s in %(name)s => %(message)s"
)

s_handler = logging.StreamHandler()
s_handler.setFormatter(s_formater)
s_handler.setLevel(logging.INFO)

logger.addHandler(s_handler)
logger.setLevel(logging.INFO)
