import logging
import os

import settings


def setup_log(log_label: str):
    if not os.path.exists(settings.LOG_ROOT):
        os.makedirs(settings.LOG_ROOT)
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s::: %(message)s",
        filename=os.path.join(settings.LOG_ROOT, log_label + ".log"),
        filemode="a",
        level=logging.INFO
    )