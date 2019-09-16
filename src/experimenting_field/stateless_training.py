import logging
import os

import settings
from src.common_utils.FireFoxBrowser import FireFoxBrowser
from src.common_utils.VirtualScreen import VirtualScreen
from src.profile_query_tester.YouTubeQueryTester import YouTubeQueryTester
from src.profile_trainer.FireFoxSimpleAutoBrowsing import FireFoxSimpleAutoBrowsing


def setup_log():
    if not os.path.exists(settings.log_root_path):
        os.makedirs(settings.log_root_path)
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s::: %(message)s",
        filename=os.path.join(settings.log_root_path, "stateless_training.log"),
        filemode="a",
        level=logging.INFO
    )


def main():
    setup_log()
    videos: list = ["https://www.youtube.com/watch?v=sKDHedsVA94",
                    "https://www.youtube.com/watch?v=5krV47BLyoQ",
                    "https://www.youtube.com/watch?v=xn4ZeV87BWM"]
    with VirtualScreen() as display, FireFoxBrowser() as browser:
        FireFoxSimpleAutoBrowsing.browsing_list_videos(videos, browser)
        tester = YouTubeQueryTester(browser, "stateless_training", settings.keyword)
        tester.search_by_keyword(settings.report_results_number)
        tester.click_and_get_right_column_recommendations(
            tester.query_result[-1], settings.recommend_results_number)


if __name__ == "__main__":
    main()
