import logging
import os

import settings


def setup_log(log_label: str):
    if not os.path.exists(settings.log_root_path):
        os.makedirs(settings.log_root_path)
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s::: %(message)s",
        filename=os.path.join(settings.log_root_path, log_label + ".log"),
        filemode="a",
        level=logging.INFO
    )