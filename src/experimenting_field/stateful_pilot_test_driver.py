import os
import multiprocessing as mp
from typing import List

import settings
from src.experimenting_field.StatefulTrainAndTest import stateful_train_and_test


def start_stateful():
    input_video_parent_path: str = \
        os.path.join(settings.ROOT_DIR, settings.INPUT_DATA, "stateful_videos")
    donald_path: str = os.path.join(input_video_parent_path, "base_videos_the_donald.json")
    enoughtrumpspam_path: str = os.path.join(input_video_parent_path,
                                             "base_videos_enoughtrumpspam.json")
    video_list: List[str] = [donald_path, enoughtrumpspam_path, ""]
    cookie_base_path: str = os.path.join(settings.ROOT_DIR, settings.INPUT_DATA, "cookies")
    cookie_path: List[str] = [os.path.join(cookie_base_path, file_name) for file_name in
                              ["the_donald.json", "enoughtrumpspam.json", "blank.json"]]
    print("Videos to be visited: {}".format(video_list))
    print("Cookies to be loaded: {}.".format(cookie_path))
    with mp.Pool() as pool:
        pool.map(stateful_train_and_test, zip(video_list, cookie_path))


if __name__ == "__main__":
    mp.set_start_method("spawn")
    start_stateful()
