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
import Settings
import random


class Trainer:

    def __init__(self, directory=Settings.training_directory):
        self.train_directory = directory
        self.base_path, self.extended_diversity, self.extended_RNG = '', '', ''
        # Notice: summary json file is also stored here, need to be careful when extracting videos
        self.base_lists, self.extended_diversity_lists, self.extended_RNG_lists = {}, {}, {}
        self.one_profile, self.one_list = '', []

    def read_json(self, path):
        with open(path) as f:
            jfile = json.load(f)
        return jfile, len(jfile), type(jfile)

    def get_all_list(self):
        for (cur_dir, sub_dir, cur_files) in os.walk(self.train_directory):
            print((cur_dir, sub_dir, cur_files))
            # Process base profiles basic version rather than detailed version
            if 'base' in cur_dir and 'detailed' not in cur_dir:
                for file in cur_files:
                    if 'json' in file:
                        v_list, _, _ = self.read_json(os.path.join(cur_dir, file))
                        name = os.path.splitext(file)[0].split('_', 2)[-1]
                        self.base_lists[name] = v_list
            if 'extended' in cur_dir and 'diversity' in cur_dir:
                for file in cur_files:
                    if 'json' in file:
                        v_list, _, _ = self.read_json(os.path.join(cur_dir, file))
                        name = os.path.splitext(file)[0].split('_', 3)[-1]
                        self.extended_diversity_lists[name] = v_list
            if 'extended' in cur_dir and 'RNG' in cur_dir:
                for file in cur_files:
                    if 'json' in file:
                        v_list, _, _ = self.read_json(os.path.join(cur_dir, file))
                        name = os.path.splitext(file)[0].split('_', 3)[-1]
                        self.extended_RNG_lists[name] = v_list

    def get_one_list(self, one_path):
        v_list, _, _ = self.read_json(one_path)
        name = os.path.splitext(one_path)[0].split('_', 3)[-1]
        self.one_profile = name
        self.one_list = v_list

    def _setup_browser(self, cookies_path):
        if Settings.ads_block:
            fp = FirefoxProfile(Settings.firefox_profile_with_functions)
        else:
            fp = FirefoxProfile(Settings.firefox_profile_blank)
        options = Options()
        options.headless = Settings.headless
        options.binary = Settings.firefox_binary_path
        browser = webdriver.Firefox(firefox_profile=fp, options=options)
        browser.maximize_window()
        browser.delete_all_cookies()
        browser.get(Settings.inital_website)
        time.sleep(3)
        try:
            cookies_list = self.read_json(cookies_path)[0]
        except Exception as e:
            print(f"Loading cookie error: {e}, reload")
            time.sleep(random.randint(2, 15))
            cookies_list = self.read_json(cookies_path)[0]
        for cookie in cookies_list:
            try:
                browser.add_cookie(cookie)
            except Exception as e:
                pass
                # Usually loading cookies failed due to specific page not loaded
                # print(f'Exception for cookie {cookie} due to {e}')
            finally:
                pass
                # print('Load cookies finished. May not successful.')
        # Refresh page
        browser.get(Settings.inital_website)
        time.sleep(3)
        return browser

    def _clean_youtube_link(self, link):
        # Remove timestamp in the url
        if "t=" in link:
            # chop off "&t=", "?t=" or "#t="
            link = link.split('t=')[0][:-1]
        return link

    def _run_js(self, browser, js):
        # Execute javascripts in the browser
        return browser.execute_script(js)

    def _get_playback_rates(self, browser):
        js = 'return document.getElementById("movie_player").getAvailablePlaybackRates()'
        return self._run_js(browser, js)

    def _get_player_status(self, browser):
        # get the play status
        status_check_list = {-1: 'unstarted', 0: 'ended', 1: 'playing',
                             2: 'paused', 3: 'buffering', 5: 'video cued'}
        js = 'return document.getElementById("movie_player").getPlayerState()'
        return status_check_list[self._run_js(browser, js)]

    def _get_elapsed_time(self, browser):
        # get elapsed_time since playing
        js = 'return document.getElementById("movie_player").getCurrentTime()'
        return self._run_js(browser, js)

    def take_screenshot(self, browser, path):
        print('Screenshot Taken')
        browser.save_screenshot(path)
        return

    # Some notice:
    # 1. when the video is finished, selenium won't see the 10s "play next"
    # it will automatically play the next
    def train_one_batch(self, name, video_list, cookies_path, training_cookie):
        if len(video_list) == 0:
            raise Exception('Empty video list')
        today = str(datetime.datetime.now().strftime('%Y-%b-%d-%H-%M'))
        log_path = os.path.join(Settings.log_root_path, name, today)
        if not os.path.exists(log_path):
            os.makedirs(log_path)
        display = Display(visible=0, size=(1920, 1080))
        display.start()
        browser = self._setup_browser(cookies_path)
        local_counter = 0
        good_counter, bad_counter = 0, 0
        print(f'---Inside a new batch, ' +
              f'train for {name} in progress, current batch size {len(video_list)}---')
        for video in video_list:
            video = self._clean_youtube_link(video)
            video_screenshot_path = video.replace('/', '-').replace(':', '-').replace('.', '-')
            report_timer = screenshot_timer = start_time = time.time()
            refresh_flag = 2
            screenshot_count = 0
            screenshot_total = Settings.screenshot_total_counts
            try:
                local_counter += 1
                print(f'\n***Now visiting #{local_counter} video: {video}, now: {time.ctime()}')
                browser.get(video)
                # YouTube API reference: https://developers.google.com/youtube/iframe_api_reference
                if Settings.fast:
                    playback_rates = self._get_playback_rates(browser)
                    # Set to play at the fastest rate
                    fast_js = f'document.getElementById("movie_player").setPlaybackRate({list(playback_rates)[-1]})'
                    self._run_js(browser, fast_js)
                previous_status = player_status = self._get_player_status(
                    browser)
                elapsed_time = self._get_elapsed_time(browser)
                print(f'status: {previous_status}, elapsed time: {elapsed_time:7.2f}s.')
                while player_status != 'ended' and elapsed_time < Settings.watch_time:
                    if int(time.time() - report_timer) > Settings.report_interval:
                        previous_status = self._get_player_status(browser)
                        print(f'status: {previous_status}, elapsed time: {elapsed_time:7.2f}s.')
                        report_timer = time.time()
                    if screenshot_count < screenshot_total and \
                            int(time.time() - screenshot_timer) > Settings.screenshot_interval:
                        save_screenshot_path = (os.path.join(log_path, video_screenshot_path) + '--' +
                                                str(screenshot_count) + '.png')
                        self.take_screenshot(browser, save_screenshot_path)
                        screenshot_count += 1
                        screenshot_timer = time.time()
                    # Slow down the checking process to prevent overload
                    time.sleep(2)
                    player_status = self._get_player_status(browser)
                    elapsed_time = self._get_elapsed_time(browser)
                    # Sometimes the video will stuck at somewhere
                    # if the status didn't change for some time, and status is abnormal and able to refresh
                    if refresh_flag and \
                            player_status == previous_status and \
                            player_status in ['unstarted', 'paused', 'buffering']:
                        # if the real time already passed one/third of watch time, means we already waited some time
                        if refresh_flag == 2 and \
                                (time.time() - start_time) > Settings.watch_time // 3:
                            browser.refresh()
                            print("Browser refreshed.")
                            refresh_flag -= 1
                        # we waited more time
                        elif refresh_flag == 1 and \
                                (time.time() - start_time) > 2 * Settings.watch_time // 3:
                            browser.refresh()
                            print("Browser refreshed.")
                            refresh_flag -= 1
                    if (time.time() - start_time) > 3 * Settings.watch_time:
                        raise Exception('Unknown reason, timeout reached')
                good_counter += 1
            except Exception as e:
                print(f'Exception: {e}, skip to next video')
                bad_counter += 1
                continue
        # Write new cookies for next training session.
        with open(training_cookie, 'w') as f:
            json.dump(browser.get_cookies(), f)
        # Need to close all tabs
        browser.quit()
        display.stop()
        return good_counter, bad_counter

    def train_a_list(self, train_list,
                     reddit_name,
                     seed_cookie=Settings.seed_cookie_path,
                     training_cookie=Settings.training_cookie_path):
        full_list, name = train_list, reddit_name.split('/')[-1]
        batch_size = Settings.training_batch_size
        print(
            f'\n>>>>>Full training begins, total: {len(full_list)}, now: {time.ctime()}<<<<<\n')
        full_good_counter, full_bad_counter = 0, 0
        for i in range(0, len(full_list), batch_size):
            restart_flag = 2
            try:
                print(f'---Current training range: from [{i+1} to {min(i+batch_size, len(full_list))}].---')
                # i % (i - 1) is for select seed_cookit initially, then select training_cookie afterwards
                good, bad = self.train_one_batch(name,
                                                 full_list[i:i + batch_size],
                                                 [seed_cookie, training_cookie][i % (i - 1)],
                                                 training_cookie)
            except Exception as e:
                print(f'Exception: {e}, current restart left: {restart_flag}')
                if restart_flag:
                    good, bad = self.train_one_batch(name,
                                                     full_list[i:i + batch_size],
                                                     [seed_cookie, training_cookie][i % (i - 1)],
                                                     training_cookie)
                    restart_flag -= 1
                else:
                    print('Running out of restart for this batch, move on to next batch.')
                    continue
            full_good_counter += good
            full_bad_counter += bad
            # Give the program sometime to clear the old residue
            time.sleep(10)
        print(f'---Total training metrics: ------successful: {full_good_counter}, failed: {full_bad_counter}---')
        print(f'>>>>>Training finished.<<<<<')

    def train_a_path(self, path):
        full_list, _, _ = self.read_json(path)
        name = os.path.splitext(path)[0]
        self.train_a_list(full_list, name)

    def train_by_reddit_or_list(self, name=Settings.full_training_name,
                                category=Settings.full_training_category,
                                path=Settings.full_list_path):
        if Settings.training_method == 1:
            self.get_all_list()
            if category == 'base':
                full_list = self.base_lists
            elif category == 'diversity':
                full_list = self.extended_diversity_lists
            elif category == 'RNG':
                full_list = self.extended_RNG_lists
            else:
                raise Exception('Not a valid category among base, diversity, RNG.')
            full_list = full_list.get(name, None)
            if not full_list:
                raise Exception('Not a valid reddit name.')
            self.train_a_list(full_list, name)
        elif Settings.training_method == 2:
            self.train_a_path(path)


def full_test():
    trainer = Trainer()
    trainer.train_by_reddit_or_list()


@click.command()
@click.option("--path", "path", default=Settings.training_list[0], help="Json video list to train")
@click.option("--sc", "seed_cookie", default=Settings.seed_cookies_list[0], help="Seed cookie to begin training")
@click.option("--tc", "training_cookie", default=Settings.training_cookies_list[0], help="Training cookie to save after training")
def training_master_mode(path, seed_cookie, training_cookie):
    if not path or not seed_cookie or not training_cookie:
        raise Exception('In master mode, but either cookies lists or training list empty.')
    trainer = Trainer()
    reddit_name = os.path.splitext(path)[0]
    train_list, _, _ = trainer.read_json(path)
    try:
        trainer.train_a_list(train_list, reddit_name, seed_cookie, training_cookie)
    except Exception as e:
        print(f"Restrat the whole training process, due to fatal error: {e}")
        trainer.train_a_list(train_list, reddit_name, seed_cookie, training_cookie)


if __name__ == '__main__':
    if Settings.master_mode:
        training_master_mode()
    else:
        full_test()
