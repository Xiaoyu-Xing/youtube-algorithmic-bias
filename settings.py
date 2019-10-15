import os
from datetime import datetime
from os.path import join
import platform

# CONSTANTS
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG = "config"
CRAWLING_CONFIG = join(CONFIG, "crawling_config")
FIREFOX_CONFIG = join(CONFIG, "firefox_config")
GEN_DATA = "generated_data"
PROFILE_DATA = "profile_data_for_training"
INPUT_DATA = "input_data"
time_format_short = '%Y:%m:%d'
time_format_long = "%Y:%m:%d %H:%M:%S"
if platform.uname().node != "xx-VirtualBox":
    LOG_ROOT: str = '/home/data/xiaoyu/log/' + datetime.today().strftime(time_format_short)
    DATA_ROOT: str = '/home/data/xiaoyu/data/'
else:
    LOG_ROOT: str = '/home/xx/data/log/' + datetime.today().strftime(time_format_short)
    DATA_ROOT: str = '/home/xx/data/data/'

# Set your parameters here

# >>>>>>>>>>>>First section: for creating profiles<<<<<<<<<<<<
# Hyper-parameters:
# Input data folder, should be the same structure as the example
input_path = join(ROOT_DIR, 'raw_reddit_data')
output_path = join(ROOT_DIR, 'generated_profiles_output')  # Output data folder

# For generating base files
base = True  # Generate base files?
base_video_number = 50  # Each profile contains # of videos
base_shuffle = True  # Shuffle the output list?
base_detailed = False  # Generate a detailed version?

# Two methods to generate extended files

# 1)
by_diversity = True  # Generate by diversity_index method?
# Choose X = (base_video_number * diversity_index number) top subreddits
# normalize the overlap ratios of these top X subreddits
# do weighted sampling using normalized overlap ratios to
# make up to total X extended videos
diversity_index = 1.0
# Shuffle the output for this method?
extended_shuffle_by_diversity = True

# 2) Preferred
by_random_number_generator = True  # Generate by random number method?
# How many digits after decimal points for subreddits ratio:
# e.g. ratio = 0.001, then this value should be 3
subreddit_ratio_decimal = 3  # the precision of ratio
# How many percent of top videos in each subreddit will be chosen
# Default 0.1, i.e. 10%
sampling_percent_index = 0.1
# Shuffle the output for this method?
extended_shuffle_by_random_number = True

# >>>>>>>>>>>>Second section: for individual training profiles<<<<<<<<<<<<
headless = False  # Using PyVirtualDisplay, keep this to false
# Path to a firefox profile with extension installed or other functionality
firefox_profile_rich_config = join(ROOT_DIR, FIREFOX_CONFIG, 'firefox-profile-rich-config/')
# Path to a blank firefox profile
firefox_profile_blank = join(ROOT_DIR, FIREFOX_CONFIG, 'firefox-profile-blank')
# Path to local firefox binary
firefox_binary_path = join(ROOT_DIR, FIREFOX_CONFIG, 'firefox-66/firefox/firefox')
# Whether to block the ads:
ads_block = True

# Test account: yout317317@gmail.com, pass: al...b... DOB: 19800101, no gender

# How many seconds to watch for each video:
watch_time = 300  # should be more than 5 seconds, VIDEO TIME
# Initial web to visit before train, DO NOT CHANGE unless for other projects
initial_website = 'https://www.youtube.com/'
# Training batch size to prevent memory overload:
training_batch_size = 100  # Must be more than 2, should be more than 20
# Whether to play at the fastest playback speed
fast = True  # Notice: if true, the video time is 2 times faster than real time

# >>>>>>>>>>>>Forth section: for pilot testing<<<<<<<<<<<<
keyword = "mueller report"
report_results_number = 50
recommend_results_number = 40  # max ~40, limited by fed list from youtube
