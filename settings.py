import os
from datetime import datetime
from os.path import join


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG = "config"
CRAWLING_CONFIG = join(CONFIG, "crawling_config")
FIREFOX_CONFIG = join(CONFIG, "firefox_config")
GEN_DATA = "generated_data"
PROFILE_DATA = "profile_data_for_training"
INPUT_DATA = "input_data"

# Set your parameters here

# >>>>>>>>>>>>First section: for creating profiles<<<<<<<<<<<<
# Hyper-parameters:
input_path = join(ROOT_DIR,
                  'raw_reddit_data')  # Input data folder, should be the same structure as the example
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

# There are two training mode:
training_method = 2  # Choose between 1 or 2
# 1) given the folder path to all of the json profiles, such as the 'sample_output' folder
# which contains all base, extended profiles (by 2 methods),
# then specify which reddit profile and whether base or extended need to train, set parameters below:

# If you need to parse all json files
# Give the dir to the lowest common folder below
training_directory = join(ROOT_DIR, GEN_DATA, PROFILE_DATA, 'sample_output')
# full training profile name, use the reddit name, check the keys summary.json file
# If not None, make sure training_directory is valid
full_training_name = 'the_donald'
# choose among 'base', 'diversity', 'RNG'
full_training_category = 'base'

# 2) given a specific json file path, and only train by those videos
# If you only need to parse and train one list
# Give the dir to json below
# Secondary choice, set full_training_name to None to use this
full_list_path = join(training_directory, 'base/base_videos_inceltears.json')
# one_path = 'cookies/test.json' # This is for testing purpose, ignore in real cookies


# Other parameters:

# Path to a firefox profile with extension installed or other functionality
firefox_profile_rich_config = join(ROOT_DIR, FIREFOX_CONFIG, 'firefox-profile-rich-config/')
# Path to a blank firefox profile
firefox_profile_blank = join(ROOT_DIR, FIREFOX_CONFIG, 'firefox-profile-blank')

# Path to local firefox binary
firefox_binary_path = join(ROOT_DIR, FIREFOX_CONFIG, 'firefox-66/firefox/firefox')
# Whether to block the ads:
ads_block = True
# Path to the cookies
# Current account: yout317317@gmail.com, pass: al...b... DOB: 19800101, no gender
# starter cookie before training
seed_cookie_path = join(ROOT_DIR, INPUT_DATA, 'cookies/cookiebro-cookies.json')
# where to save cookie after training
training_cookie_saving_path = join(ROOT_DIR, INPUT_DATA, 'cookies/after_training_cookie.json')
# How many seconds to watch for each video:
watch_time = 30  # should be more than 5 seconds, VIDEO TIME
# Initial web to visit before train, DO NOT CHANGE unless for other projects
initial_website = 'https://www.youtube.com/'
# Training batch size to prevent memory overload:
training_batch_size = 100  # Must be more than 2, should be more than 20
screenshot_total_counts = 2  # How many screen-shot needed
# How many seconds between each screenshots, real interval will be roughly equal to this
screenshot_interval = 8  # In seconds, REAL TIME
# Whether to play at the fastest playback speed
fast = True  # Notice: if true, the video time is 2 times faster than real time
# Report time interval, how long between report current status, unit: seconds
report_interval = 10  # should more than 2 seconds, REAL TIME

# >>>>>>>>>>>>Third section: for training in parallel mode<<<<<<<<<<<<
# Set to true if train in parallel
# Turn on master mode will override training setting above, including:
# 1) only method 2 will be used, which means only a list provided will be trained
# 2) seed and training cookies needs be provided here
# 3) log path need to be provided for log and screenshot

# Attention: must set path for Click: export LC_ALL=C.UTF-8, export LANG=C.UTF-8
master_mode = True
log_root_path: str = '/home/xx/data/log/' + datetime.today().strftime('%Y-%m-%d')
training_base_path = join(training_directory, "base")
training_RNG_path = join(training_directory, "extended_RNG")
training_diversity_path = join(training_directory, "extended_diversity")
categories = ['mensrights.json', 'incel.json', 'enoughtrumpspam.json',
              'inceltears.json', 'feminism.json', 'metoo.json', 'the_donald.json']
training_list = [join(training_base_path, "base_videos_" + cat) for cat in categories]
# training_list = [join(training_base_path, "related_videos_RNG_" + cat) for cat in categories]
# training_list = [join(training_base_path, "related_videos_diversity" + cat) for cat in categories]

# For current project, below list length needs to be same with above list length
seed_cookies_list = [seed_cookie_path] * 7
training_cookies_list = [training_cookie_saving_path] * 7

# >>>>>>>>>>>>Forth section: for pilot testing<<<<<<<<<<<<
keyword = "mueller report"
report_results_number = 3
recommend_results_number = 2  # max ~40, limited by fed list from youtube
