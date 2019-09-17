import logging
import os
from typing import List

import settings
from src.common_utils.LogSetup import setup_log
from multiprocessing import Pool

from src.experimenting_field.StatelessTrainAndTest import stateless_train_and_test


def start_stateful():
    setup_log(__name__ + __file__)
    log = logging.getLogger(__name__)
    stateful_videos: str = "stateful_videos"
    input_video_parent_path: str = \
        os.path.join(settings.ROOT_DIR, settings.INPUT_DATA, stateful_videos)
    donald_path: str = os.path.join(input_video_parent_path, "related_videos_RNG_the_donald.json")
    enoughtrumpspam: str = os.path.join(input_video_parent_path,
                                        "related_videos_RNG_enoughtrumpspam.json")
    video_list: List[str] = [donald_path, enoughtrumpspam, ""]
    log.info("Videos to be visited: {}".format(video_list))
    with Pool(processes=len(video_list)) as pool:
        pool.map(stateless_train_and_test, video_list)


if __name__ == "__main__":
    start_stateful()