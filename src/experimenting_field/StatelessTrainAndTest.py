import json
import logging
import os
from typing import List

import settings
from src.common_utils.FireFoxBrowser import FireFoxBrowser
from src.common_utils.LogSetup import setup_log
from src.common_utils.VirtualScreen import VirtualScreen
from src.profile_query_tester.YouTubeQueryTester import YouTubeQueryTester
from src.profile_trainer.FireFoxSimpleAutoBrowsing import FireFoxSimpleAutoBrowsing


def stateless_train_and_test(video_json_path: str) -> None:
    if video_json_path:
        label: str = os.path.basename(video_json_path).strip(".json")
    else:
        label: str = "blank_control"
    setup_log(label + "_stateless_" + str(os.getpid()))
    log = logging.getLogger(__name__ + str(os.getpid()))
    if video_json_path == "":
        log.info("Start stateless control experiment, i.e. no training.")
        with VirtualScreen() as display, FireFoxBrowser() as browser:
            # Notice, no training part here.
            tester = YouTubeQueryTester(browser, "stateless-test", "blank", settings.keyword)
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
        log.info("State stateless experiment.")
        with VirtualScreen() as display, FireFoxBrowser() as browser:
            FireFoxSimpleAutoBrowsing.browse_video_list(videos, browser)
            tester = YouTubeQueryTester(browser, "stateless-test", label, settings.keyword)
            tester.search_by_keyword(settings.report_results_number)
            tester.get_side_column_recommendations_from_youtube_records(
                tester.query_result[-1], settings.recommend_results_number)


if __name__ == "__main__":
    stateless_videos: str = "stateless_videos"
    input_video_parent_path: str = \
        os.path.join(settings.ROOT_DIR, settings.INPUT_DATA, stateless_videos)
    donald_path: str = os.path.join(input_video_parent_path, "related_videos_RNG_the_donald.json")
    enoughtrumpspam_path: str = os.path.join(input_video_parent_path,
                                             "base_videos_enoughtrumpspam.json")
    stateless_train_and_test(enoughtrumpspam_path)
