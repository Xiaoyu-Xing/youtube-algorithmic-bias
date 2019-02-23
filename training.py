from selenium import webdriver
import json
import os
import time
import httplib2
import Settings



class Trainer:

    def __init__(self,
                 directory=Settings.training_directory
                 ):
        self.train_directory = directory
        self.base_path, self.extended_diversity, self.extended_RNG = '', '', ''
        # Notice: summary json file is also stored here, need to be careful when extracting videos
        self.base_lists, self.extended_diversity_lists, self.extended_RNG_lists = {}, {}, {}
        self.one_profile, self.one_list = '', []

    def _read_json(self, path):
        with open(path) as f:
            jfile = json.load(f)
        return jfile, len(jfile), type(jfile)

    def get_all_list(self):
        for (cur_dir, sub_dir, cur_files) in os.walk(self.train_directory):
            # Process base profiles basic version rather than detailed version
            if 'base' in cur_dir and 'detailed' not in cur_dir:
                for file in cur_files:
                    if 'json' in file:
                        v_list, _, _ = self._read_json(os.path.join(cur_dir, file))
                        name = os.path.splitext(file)[0].split('_', 2)[-1]
                        self.base_lists[name] = v_list
            if 'extended' in cur_dir and 'diversity' in cur_dir:
                for file in cur_files:
                    if 'json' in file:
                        v_list, _, _ = self._read_json(os.path.join(cur_dir, file))
                        name = os.path.splitext(file)[0].split('_', 3)[-1]
                        self.extended_diversity_lists[name] = v_list
            if 'extended' in cur_dir and 'RNG' in cur_dir:
                for file in cur_files:
                    if 'json' in file:
                        v_list, _, _ = self._read_json(os.path.join(cur_dir, file))
                        name = os.path.splitext(file)[0].split('_', 3)[-1]
                        self.extended_RNG_lists[name] = v_list

    def get_one_list(self, one_path=Settings.one_path):
        v_list, _, _ = self._read_json(one_path)
        name = os.path.splitext(one_path)[0].split('_', 3)[-1]
        self.one_profile = name
        self.one_list = v_list

    def _exe_js(browser, scripts):
        return 

    # Some notice:
    # 1. when the video is finished, selenium won't see the 10s "play next"
    # it will automatically play the next
    # 2. No idea what is video cued???
    def train_one_batch(self, name, video_list, cookies_path=Settings.seed_cookie_path):
        if len(video_list) == 0:
            raise Exception('Nothing to train, did already you parse the list?')
        print(f'Train for {name} in progress, total length {len(video_list)}')
        # fp = webdriver.FirefoxProfile()
        browser = webdriver.Firefox()
        # Delete initial coockies, if any
        browser.delete_all_cookies()
        # Load page before load cookies !!!
        browser.get(Settings.inital_website)
        cookies_list  = self._read_json(cookies_path)[0]
        good_counter, bad_counter = 0, 0
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
        for video in video_list:
            # Cannot use status == 200 to determin video availability
            # http = httplib2.Http()
            # response = http.request(video, 'HEAD')
            # if int(response[0]['status']) != 200:
            #     print(f'{video} unavailable, skip to next one.')
            #     continue
            # print(int(response[0]['status']))
            try:
                print(f'Now visiting: {video}')
                browser.get(video)
                # YouTube API reference: https://developers.google.com/youtube/iframe_api_reference
                playback_rates = browser.execute_script(
                    'return document.getElementById("movie_player").getAvailablePlaybackRates()'
                    )
                # Check availabel playback speed
                # print(f'playback rate: {playback_rates}')
                # Set to play at the fastest rate
                browser.execute_script(
                    f'document.getElementById("movie_player").setPlaybackRate({list(playback_rates)[-1]})'
                    )
                # getPlayerState code: -1: unstarted, 
                # 0: ended, 1: playing, 2: paused, 3: buffering, 5: video cued
                player_status = browser.execute_script(
                    'return document.getElementById("movie_player").getPlayerState()'
                    )
                # get elapsed_time since playing
                elapsed_time = browser.execute_script(
                    'return document.getElementById("movie_player").getCurrentTime()'
                    )
                while player_status != 0 and elapsed_time < Settings.watch_time:
                    print(f'status: {player_status}, time: {elapsed_time}')
                    time.sleep(2)
                    player_status = browser.execute_script(
                        'return document.getElementById("movie_player").getPlayerState()'
                        )
                    elapsed_time = browser.execute_script(
                        'return document.getElementById("movie_player").getCurrentTime()'
                        )
                good_counter += 1
            except Exception as e:
                print(f'Exception: {e}, skip to next video')
                bad_counter += 1
                continue
        # Write new cookies for next training session.
        with open(Settings.training_coockie_path, 'w') as f:
            json.dump(browser.get_cookies(), f)
        browser.close()
        return good_counter, bad_counter

    def train_all(self, name=Settings.full_training_name, 
                  category=Settings.full_training_category,
                  path=Settings.full_list_path):
        batch_size = Settings.training_batch_size
        if name:
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
        elif path:
            full_list, _, _ = self._read_json(path)
            name = os.path.splitext(path)[0]
        print(f'Full training begins, total: {len(full_list)}')
        full_good_counter, full_bad_counter = 0, 0
        for i in range(0, len(full_list), batch_size):
            print(f'Current traning range: from [{i} to {i+batch_size}).')
            if i == 0:
                good, bad = self.train_one_batch(name, full_list[i:i+batch_size], Settings.seed_cookie_path)
            else:
                self.train_one_batch(name, full_list[i:i+batch_size], Settings.training_coockie_path)
            full_good_counter += good
            full_bad_counter += bad
        print(f'Total training metrics: \
            successful: {full_good_counter}, failed: {full_bad_counter}')
        print(f'Training finished.')


def short_test():
    trainer = Trainer()
    trainer.get_one_list()
    print(trainer.one_list)
    print(trainer.one_profile)
    trainer.train_one_batch('yout317317', trainer.one_list)


def full_test():
    trainer = Trainer()
    trainer.train_all()

if __name__ == '__main__':
    full_test()
