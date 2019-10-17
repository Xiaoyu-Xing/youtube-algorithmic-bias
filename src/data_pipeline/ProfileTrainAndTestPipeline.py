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


def train_and_test_profile(subreddit: str,
                           tag: str,
                           cookie_path: str,
                           video_json_path: str = "") -> Tuple[str, str]:
    videos = []
    if video_json_path != "":
        with open(video_json_path) as f:
            videos: List[str] = json.load(f)
    batch_size: int = len(videos) if "stateless" in tag and len(videos) > 0  else settings.training_batch_size
    setup_log(f"{subreddit}-{tag}-{os.getpid()}")
    log = logging.getLogger(__name__ + str(os.getpid()))
    if subreddit != "blank" and not os.path.isfile(video_json_path):
        log.error("Video json file {} not exists.".format(video_json_path))
        raise RuntimeError("Invalid file path.")
    log.info("Total training size: {}.".format(len(videos)))
    # Training will be skipped if videos list is empty.
    # with VirtualScreen() as display:
    for i in range(0, len(videos), batch_size):
        sub_video_list: List[str] = videos[i:i + batch_size]
        with FireFoxBrowser(cookie_path) as browser:
            FireFoxSimpleAutoBrowsing.browse_video_list(sub_video_list, browser)
    with FireFoxBrowser(cookie_path) as browser:
        tester = YouTubeQueryTester(browser, tag, subreddit, settings.keyword)
        query_result_path: str = tester.search_by_keyword(settings.report_results_number)
        recommendation_path: str = tester.get_side_column_recommendations_from_youtube_records(
            tester.query_result[-1], settings.recommend_results_number)
    return query_result_path, recommendation_path
