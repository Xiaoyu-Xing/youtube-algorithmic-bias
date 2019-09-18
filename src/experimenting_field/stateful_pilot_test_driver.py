import logging
import os
from multiprocessing import Pool
from typing import List

import settings
from src.common_utils.LogSetup import setup_log
from src.experimenting_field.StatefulTrainAndTest import stateful_train_and_test


def start_stateful():
    setup_log(os.path.basename(__file__ + str(os.getpid())).strip(".py"))
    log = logging.getLogger(__name__ + str(os.getpid()))
    input_video_parent_path: str = \
        os.path.join(settings.ROOT_DIR, settings.INPUT_DATA, "stateful_videos")
    donald_path: str = os.path.join(input_video_parent_path, "related_videos_RNG_the_donald.json")
    enoughtrumpspam_path: str = os.path.join(input_video_parent_path,
                                             "related_videos_RNG_enoughtrumpspam.json")
    video_list: List[str] = [donald_path, enoughtrumpspam_path, ""]
    cookie_base_path: str = os.path.join(settings.ROOT_DIR, settings.INPUT_DATA,
                                         "cookies", "standard")
    cookie_path: List[str] = [os.path.join(cookie_base_path, file_name) for file_name in
                              ["the_donald.json", "enoughtrumpspam.json", "blank.json"]]
    log.info("Videos to be visited: {}".format(video_list))
    log.info("Cookies to be loaded: {}.".format(cookie_path))
    with Pool(processes=len(video_list)) as pool:
        pool.starmap(stateful_train_and_test, zip(video_list, cookie_path))


if __name__ == "__main__":
    start_stateful()