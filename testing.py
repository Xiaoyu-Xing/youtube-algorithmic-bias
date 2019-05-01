from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from pyvirtualdisplay import Display
import json
import os
import time
import datetime
import click
import Settings as sts
import random
from collections import OrderedDict


class Testing:
    def __init__(self, start="https://www.youtube.com/", driver=None):
        self.driver = driver
        if not self.driver:
            fp = FirefoxProfile(sts.firefox_profile_blank)
            options = Options()
            options.binary = sts.firefox_binary_path
            self.driver = webdriver.Firefox(firefox_profile=fp, options=options)
        if not os.path.exists(sts.testing_output):
            os.makedirs(sts.testing_output)
        self.driver.implicitly_wait(5)
        self.driver.get(start)

    def get_seconds(self, number, unit):
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
            print(number, unit)
            raise Exception("Unsupported unit.")

    def parse_video(self, video):
        title = video.get_attribute("title")  # Title
        href = video.get_attribute("href")  # Link
        info = video.get_attribute("aria-label")
        # All info including title, source, uploaded time, video length, views
        # e.g. : "Trump holds first 'MAGA' rally since Mueller report release by Fox News Streamed 19 hours ago 1 hour, 26 minutes 284,647 views"
        source, uploaded_time, video_length, views, up_time = self.parse_info(title, info)
        ret = {"href": href,
               "source": source,
               "uploaded on": f"{up_time} seconds ago from query time",
               "upload time": "Approximate: " + uploaded_time.strftime("%m/%d/%Y %H:%M:%S"),
               "video length": f"{video_length} seconds",
               "views": views,
               "query time": datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")}
        return ret

    def parse_info(self, title, info):
        # print(info)
        info = info.replace(title + " by ", "")  # remove title from info
        source = []
        up_time = 0
        video_length = 0
        views = 0
        source_uptime, length_views = info.split(" ago ")
        source_uptime = source_uptime.split()
        length_views = length_views.split()
        unit_list = ["second", "minute", "hour", "day", "week", "month", "year"]
        for i in range(len(source_uptime)):
            # All the words after "by" until the first digit is Source
            if source_uptime[i].isdigit() and source_uptime[i + 1].rstrip("s") in unit_list:
                source_uptime = source_uptime[i:]
                break
            else:
                source.append(source_uptime[i])
        source = " ".join(source)
        up_time = self.get_seconds(source_uptime[0], source_uptime[1])  # Get the total seconds from uploaded
        uploaded_time = datetime.datetime.now() - datetime.timedelta(seconds=up_time)  # Calculate the uploaded datetime
        views = int("".join(length_views[-2].split(",")))  # Get all the views
        length_views = length_views[:-2]  # remove the views
        for i in range(0, len(length_views), 2):  # for all the left words, convert all time to seconds
            video_length += self.get_seconds(length_views[i], length_views[i + 1])
        return source, uploaded_time, video_length, views, up_time

    def search(self, keyword=sts.keyword, results=sts.report_results_number):
        driver = self.driver
        driver.find_element_by_name("search_query").click()
        driver.find_element_by_name("search_query").clear()
        driver.find_element_by_name("search_query").send_keys(keyword)
        try:
            driver.find_element_by_id("search-form").submit()
        except:
            driver.find_element_by_name("search_query").click()
        time.sleep(3)
        while len(driver.find_elements_by_id("video-title")) < results:
            driver.execute_script("window.scrollByPages(10)")
            time.sleep(3)
        video_list = driver.find_elements_by_id("video-title")
        video_dict = OrderedDict()
        for video in video_list:
            title = video.get_attribute("title")  # Title
            if title in video_dict:
                continue
            try:
                video_dict[title] = self.parse_video(video)
            except Exception as e:
                print(e)
                print(video.get_attribute("aria-label"))
                continue
            if len(video_dict.keys()) >= results:  # Get the targeted number of results
                break
        with open(os.path.join(sts.testing_output, f"{keyword}_search_result_{sts.additional_label}.json"), "w") as f:
            json.dump(video_dict, f, indent=4)
        # driver.quit()
        return video_dict

    def click_getrecommend(self, video_dict, results=sts.recommend_results_number):
        # video_dict is ordereddict
        # but after python 3.7, the dictionary is by default maintains the order of elements
        driver = self.driver
        recommend_dict = OrderedDict()
        for title in video_dict.keys():
            if title in recommend_dict:
                continue
            recommend_dict[title] = []
            driver.get(video_dict[title]["href"])
            time.sleep(3)
            for _ in range(4):
                driver.execute_script("window.scrollByPages(10)")
                time.sleep(3)
            recs = driver.find_elements_by_class_name("ytd-compact-video-renderer")
            temp_href_list = []
            temp_info_list = []
            for rec in recs:
                if rec.get_attribute("href"):
                    temp_href_list.append(rec.get_attribute("href"))
                if rec.get_attribute("aria-label"):
                    temp_info_list.append(rec.get_attribute("aria-label"))
            if len(temp_href_list) != len(temp_info_list):
                raise Exception("href links and titles length not match.")
            for href, info in zip(temp_href_list, temp_info_list):
                try:
                    rec_title = info.split(" by ")[0]
                    source, uploaded_time, video_length, views, up_time = self.parse_info(rec_title, info)
                    ret = {"href": href,
                           "source": source,
                           "uploaded on": f"{up_time} seconds ago from query time",
                           "upload time": "Approximate: " + uploaded_time.strftime("%m/%d/%Y %H:%M:%S"),
                           "video length": f"{video_length} seconds",
                           "views": views,
                           "query time": datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")}
                    recommend_dict[title].append(ret)
                    if len(recommend_dict[title]) >= results:
                        break
                except Exception as e:
                    print(e)
                    print(info)
                    continue
            print(f"for each recommend list: {len(recommend_dict[title])}")
        with open(os.path.join(sts.testing_output, f"{sts.keyword}_recommendation_lists_{sts.additional_label}.json"), "w") as f:
            json.dump(recommend_dict, f, indent=4)
        return recommend_dict


def main():
    tester = Testing()
    video_dict = tester.search()
    tester.click_getrecommend(video_dict)
    tester.driver.quit()


if __name__ == '__main__':
    main()
