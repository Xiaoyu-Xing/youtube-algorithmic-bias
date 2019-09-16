import datetime
import json
import logging
import os
import time
from collections import OrderedDict
from typing import List, Dict

from selenium import webdriver
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.firefox.options import Options

from src.common_utils.YouTubeVideoRecord import YouTubeVideoRecord


import settings as sts

log = logging.getLogger(__name__)


class YouTubeQueryTester:
    QUERY_WEB: str = "https://www.youtube.com/"
    QUERY_IMPLICIT_WAIT: int = 5  # Waiting in seconds due to asynchronous feature of browsers
    # The limit of scrolling down to find enough query result, 100 window size should be enough for
    # a few hundred search result
    SCROLL_DOWN_COUNT_LIMIT: int = 100
    # 4 scrolls is enough to get all the recommendation list (as of 2019, ~40 for each video) in the
    # right side recommendation column
    SIDE_RECOMMENDATIONS_SCROLL_DOWN: int = 4
    EXPLICIT_SLEEP_TIME: int = 3  # in seconds

    def __init__(self,
                 driver: webdriver.Firefox,
                 subdirectory_to_save_result: str,
                 keyword: str) -> None:
        log.info("Start testing on web: {}".format(YouTubeQueryTester.QUERY_WEB))
        log.info("Class variables: "
                 "QUERY_WEB: {}, QUERY_IMPLICIT_WAIT: {}, SCROLL_DOWN_COUNT_LIMIT: {}, "
                 "SIDE_RECOMMENDATIONS_SCROLL_DOWN: {}, EXPLICIT_SLEEP_TIME: {}."
                 .format(YouTubeQueryTester.QUERY_WEB, YouTubeQueryTester.QUERY_IMPLICIT_WAIT,
                         YouTubeQueryTester.SCROLL_DOWN_COUNT_LIMIT,
                         YouTubeQueryTester.SIDE_RECOMMENDATIONS_SCROLL_DOWN,
                         YouTubeQueryTester.EXPLICIT_SLEEP_TIME))
        self.query_result: List[List[YouTubeVideoRecord]] = []
        self.recommendation_result: List[Dict[str, List[YouTubeVideoRecord]]] = []
        self.subdirectory_to_save_result: str = \
            os.path.join(sts.ROOT_DIR, sts.GEN_DATA,
                         subdirectory_to_save_result
                         + datetime.datetime.now().strftime(" %m-%d-%Y %H-%M-%S"))
        if not os.path.exists(self.subdirectory_to_save_result):
            os.makedirs(self.subdirectory_to_save_result)
        log.info("Tester result saved at: {}".format(self.subdirectory_to_save_result))
        self.keyword: str = keyword
        self.driver: webdriver.Firefox = driver
        self.internal_driver: bool = False
        if not self.driver:
            log.warning("External FireFox driver is not provided, "
                        "blank firefox driver is created on behalf.")
            fp: FirefoxProfile = FirefoxProfile(sts.firefox_profile_blank)
            log.info("\tFireFox profile: {}, profile directory path: {}"
                     .format(fp.path, sts.firefox_profile_blank))
            options: Options = Options()
            options.headless = sts.headless
            log.info("\tFireFox profile headless: {}".format(sts.headless))
            options.binary = sts.firefox_binary_path
            log.info("\tFireFox binary directory path: {}".format(sts.firefox_binary_path))
            self.driver: webdriver.Firefox = webdriver.Firefox(firefox_profile=fp, options=options)
            self.internal_driver = True
        self.driver.implicitly_wait(YouTubeQueryTester.QUERY_IMPLICIT_WAIT)
        log.info("Set implicit wait as {} seconds."
                 .format(YouTubeQueryTester.QUERY_IMPLICIT_WAIT))
        self.driver.get(YouTubeQueryTester.QUERY_WEB)

    @staticmethod
    def convert_to_sec_from_other_unit(number: str, unit: str) -> int:
        if not number.isdigit():
            raise ValueError("Unable to convert non-digit to time in seconds. Argument: {}"
                             .format(number))
        if "second" in unit:
            return int(number)
        elif "minute" in unit:
            return int(number) * 60
        elif "hour" in unit:
            return int(number) * 3600
        elif "day" in unit:
            return int(number) * 86400
        elif "week" in unit:
            return int(number) * 86400 * 7
        elif "month" in unit:
            return int(number) * 86400 * 30
        elif "year" in unit:
            return int(number) * 86400 * 30 * 12
        else:
            raise RuntimeError("Unsupported unit. Argument: {}".format(unit))

    def parse_video(self, video) -> YouTubeVideoRecord:
        title: str = video.get_attribute("title")  # Title
        href: str = video.get_attribute("href")  # Link
        # Video info including title, source, uploaded time, video length, views
        # e.g. : "Trump holds first 'MAGA' rally since Mueller report release by
        # Fox News Streamed 19 hours ago 1 hour, 26 minutes 284,647 views"
        info: str = video.get_attribute("aria-label")
        info = info.replace(title + " by ", "")  # remove title from info
        new_record: YouTubeVideoRecord = self.parse_video_details_info_attribute(info)
        new_record.href = href
        new_record.title = title
        # info_dict["href"] = href
        # info_dict["title"] = title
        log.debug("Got video {} information: {}.".format(repr(video), new_record))
        return new_record

    def parse_video_details_info_attribute(self, info: str) -> YouTubeVideoRecord:
        source: str = "Unknown"
        upload_time: str = "Unknown"
        unit: str = "Unknown"
        video_length: int = 0
        # Everything after title, before " ago "
        source_and_upload_time: str = info.split(" ago ")[0]
        video_length_and_views_count: str = info.split(" ago ")[1]  # Everything after " ago "
        source_uptime: List[str] = source_and_upload_time.split()
        length_views: List[str] = video_length_and_views_count.split()

        unit_list: List[str] = ["second", "minute", "hour", "day", "week", "month", "year"]
        for i, word in enumerate(source_uptime):
            # All the words after "by" until the first digit is Source
            if word.isdigit() and source_uptime[i + 1].rstrip("s") in unit_list:
                upload_time: str = word
                unit: str = source_uptime[i + 1]
                source = " ".join(source_uptime[:i])
                break
        # Approximate the uploaded datetime
        uploaded_time: datetime = datetime.datetime.now() - datetime.timedelta(
            seconds=self.convert_to_sec_from_other_unit(upload_time, unit))
        # Get the number and remove the comma separation and
        views = int("".join(length_views[-2].split(",")))  # Get all the views
        length_views = length_views[:-2]  # remove the views
        for i in range(0, len(length_views),
                       2):  # for all the left words, convert all time to seconds
            video_length += self.convert_to_sec_from_other_unit(
                length_views[i], length_views[i + 1])

        new_record = YouTubeVideoRecord()
        new_record.source = source
        new_record.approximated_uploaded_time = uploaded_time
        new_record.video_length = video_length
        new_record.views = views
        new_record.query_time = datetime.datetime.now()
        # ret = {"source": source,
        #        "approximated upload time": uploaded_time.strftime("%m/%d/%Y %H:%M:%S"),
        #        "video length": f"{video_length} seconds",
        #        "views": views,
        #        "query time": datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")}
        return new_record

    def search_by_keyword(self,
                          num_of_results_needed: int,
                          additional_label: str = "test"):
        driver: webdriver.Firefox = self.driver
        driver.find_element_by_name("search_query").click()
        driver.find_element_by_name("search_query").clear()
        driver.find_element_by_name("search_query").send_keys(self.keyword)
        log.info("Begin search by driver {}, with keyword: {}"
                 .format(repr(driver), self.keyword))
        try:
            driver.find_element_by_id("search-form").submit()
        except Exception as e:
            log.warning("Unable to find element by id 'search-form', use find element"
                        " by name 'search_query' instead. Message: {}".format(e))
            driver.find_element_by_name("search_query").click()
        # Explicit sleep for web to load. (Don't remember whether in addition to implicit wait.)
        time.sleep(YouTubeQueryTester.EXPLICIT_SLEEP_TIME)
        scroll_count: int = 0
        while len(driver.find_elements_by_id("video-title")) < num_of_results_needed:
            log.debug("Scrolling down to show more result, required: {}, found: {}"
                      .format(num_of_results_needed,
                              len(driver.find_elements_by_id("video-title"))))
            driver.execute_script("window.scrollByPages(10)")
            scroll_count += 1
            if scroll_count > YouTubeQueryTester.SCROLL_DOWN_COUNT_LIMIT:
                log.error("Unable to find enough result, required: {}, found: {}, "
                          "scroll down count: {}"
                          .format(num_of_results_needed,
                                  len(driver.find_elements_by_id("video-title")),
                                  scroll_count))
                break
            time.sleep(YouTubeQueryTester.EXPLICIT_SLEEP_TIME)
        # Get all the videos shown on web page
        video_list: List = driver.find_elements_by_id("video-title")
        query_result_list: List = list()  # Maintain the video sequence as shown in web page
        for video in video_list:
            url: str = video.get_attribute("href")  # url
            try:
                query_result_list.append(self.parse_video(video))
                log.debug("Add video {} info {}.".format(url, query_result_list[-1]))
            except Exception as e:
                log.error("Unable to parse video, url: {}, full info: {}, error message {}"
                          .format(url, (video.get_attribute("aria-label")), e), exc_info=True)
                continue
            if len(query_result_list) >= num_of_results_needed:
                break
        log.info("Got {} number of videos after searching for keyword {}."
                 .format(len(query_result_list), self.keyword))
        save_file_path: str = os.path.join(
            self.subdirectory_to_save_result,
            f"query_result_for_{self.keyword}_with_{additional_label}.json")
        try:
            with open(save_file_path, "w") as f:
                json.dump(obj=query_result_list, fp=f, indent=4, default=YouTubeVideoRecord.encoder)
                log.info("Saved search result for {} as json file at {}."
                         .format(self.keyword, save_file_path))
        except TypeError as e:
            log.error("Error during save json file at {}, message {}."
                      .format(save_file_path, e), exc_info=True)
        self.query_result.append(query_result_list)
        return query_result_list

    def click_and_get_right_column_recommendations(
            self, query_result_list: List[YouTubeVideoRecord],
            num_results_required_for_each_video: int,
            additional_label: str = "test") -> Dict[str, List[YouTubeVideoRecord]]:
        driver = self.driver
        recommend_dict = OrderedDict()
        log.info("Getting deep recommendation from right side column recommendation list for "
                 "a list of videos. Number of vidoes to investigate: {}, "
                 "each video need {} recommendations."
                 .format(len(query_result_list), num_results_required_for_each_video))
        for query in query_result_list:
            parent_url = query.href
            if parent_url in recommend_dict:
                continue
            log.info("Getting side recommendation for {}.".format(query))
            recommend_dict[parent_url] = []
            driver.get(parent_url)
            time.sleep(YouTubeQueryTester.EXPLICIT_SLEEP_TIME)
            for _ in range(YouTubeQueryTester.SIDE_RECOMMENDATIONS_SCROLL_DOWN):
                # Cannot do check for number of element, because there are multiple empty element
                driver.execute_script("window.scrollByPages(10)")
                time.sleep(YouTubeQueryTester.EXPLICIT_SLEEP_TIME)
            recs: List = driver.find_elements_by_class_name("ytd-compact-video-renderer")
            # Note: the url and information is not in the same object, so need to get all not-None
            # object and match them together
            temp_href_list = []
            temp_info_list = []
            for rec in recs:
                if rec.get_attribute("href"):
                    temp_href_list.append(rec.get_attribute("href"))
                if rec.get_attribute("aria-label"):
                    temp_info_list.append(rec.get_attribute("aria-label"))
            for href, info in zip(temp_href_list, temp_info_list):
                log.info("\tCurrent parsing recommended video {}.".format(href))
                try:
                    rec_title = info.split(" by ")[0]
                    info = info.replace(rec_title + " by ", "")  # remove title from info
                    new_record: YouTubeVideoRecord = self.parse_video_details_info_attribute(info)
                    # The recommendation video in side column element info is different from
                    # video directly pulled from query page, href is not in "info" element
                    new_record.href = href
                    new_record.title = rec_title
                    # rec_dict["href"] = href
                    # rec_dict["title"] = rec_title
                    recommend_dict[parent_url].append(new_record)
                    if len(recommend_dict[parent_url]) >= num_results_required_for_each_video:
                        break
                except Exception as e:
                    log.error("Exception {} during parsing recommendation video {} for url {}."
                              .format(e, href, parent_url), exc_info=True)
                    continue
        save_file_path = os.path.join(
            self.subdirectory_to_save_result,
            f"Side_column_recommendation_lists_for_{self.keyword}_with_{additional_label}.json")
        try:
            with open(save_file_path, "w") as f:
                json.dump(obj=recommend_dict, fp=f, indent=4, default=YouTubeVideoRecord.encoder)
                log.info("Saved side recommendation result for {} as json file at {}."
                         .format(self.keyword, save_file_path))
        except TypeError as e:
            log.error("Error during save json file at {}, message {}."
                      .format(save_file_path, e), exc_info=True)
        self.recommendation_result.append(recommend_dict)
        return recommend_dict

    def __del__(self):
        if self.internal_driver and self.driver:
            self.driver.quit()
