import json
import logging
import os
from typing import List, Tuple

import settings
from src.common_utils.FireFoxBrowser import FireFoxBrowser
from src.common_utils.LogSetup import setup_log
from src.common_utils.VirtualScreen import VirtualScreen
from src.profile_query_tester.YouTubeQueryTester import YouTubeQueryTester
from src.profile_trainer.FireFoxSimpleAutoBrowsing import FireFoxSimpleAutoBrowsing


def stateful_train_and_test(json_and_cookie: Tuple[str, str]) -> None:
    video_json_path: str = json_and_cookie[0]
    cookie_path: str = json_and_cookie[1]
    if video_json_path:
        label: str = os.path.basename(video_json_path).strip(".json")
    else:
        label: str = "blank_control"
    setup_log(label + "_stateful_" + str(os.getpid()))
    log = logging.getLogger(__name__ + str(os.getpid()))
    if video_json_path == "":
        log.info("Start stateful control experiment, i.e. no training.")
        with VirtualScreen() as display, FireFoxBrowser(cookie_path) as browser:
            # Notice, no training part here.
            tester = YouTubeQueryTester(browser, "stateful-test", "blank", settings.keyword)
            tester.search_by_keyword(settings.report_results_number)
            tester.get_side_column_recommendations_from_youtube_records(
                tester.query_result[-1], settings.recommend_results_number)
    else:
        if not os.path.isfile(video_json_path):
            log.error("Video json file {} not exists.".format(video_json_path))
            raise RuntimeError("Invalid file path.")
        with open(video_json_path) as f:
            videos: List[str] = json.load(f)
        if not videos:
            log.error("No videos read from json file {}.".format(video_json_path))
        log.info("State stateful experiment. Total training size: {}.".format(len(videos)))
        for i in range(0, len(videos), settings.training_batch_size):
            sub_video_list: List[str] = videos[i:i + settings.training_batch_size]
            with VirtualScreen() as display, FireFoxBrowser(cookie_path) as browser:
                FireFoxSimpleAutoBrowsing.browse_video_list(sub_video_list, browser)
        with VirtualScreen() as display, FireFoxBrowser(cookie_path) as browser:
            tester = YouTubeQueryTester(browser, "stateful-test", label, settings.keyword)
            tester.search_by_keyword(settings.report_results_number)
            tester.get_side_column_recommendations_from_youtube_records(
                tester.query_result[-1], settings.recommend_results_number)


if __name__ == "__main__":
    stateful_videos: str = "stateful_videos"
    input_video_parent_path: str = \
        os.path.join(settings.ROOT_DIR, settings.INPUT_DATA, stateful_videos)
    donald_path: str = os.path.join(input_video_parent_path, "base_videos_the_donald.json")
    enoughtrumpspam_path: str = os.path.join(input_video_parent_path,
                                             "base_videos_enoughtrumpspam.json")
    cookie_base_path: str = os.path.join(settings.ROOT_DIR, settings.INPUT_DATA, "cookies")
    cookie_path_trump: str = os.path.join(cookie_base_path, "enoughtrumpspam.json")
    stateful_train_and_test((enoughtrumpspam_path, cookie_path_trump))
