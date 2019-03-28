# Fix: document: settings details here, research method on onenote, how to run in readme

# Set your parameters here

# >>>>>>>>>>>>First section: for creating profiles<<<<<<<<<<<<
# Hyperparameters:
input_path = 'data'  # Input data folder, should be the same structrue as the example
output_path = 'output'  # Output data folder

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

# 2)
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
training_directory = 'sample_output'
# full traning profile name, use the reddit name, check the keys summary.json file
# If not None, make sure training_directory is valid
full_training_name = 'the_donald'
# choose among 'base', 'diversity', 'RNG'
full_training_category = 'base'

# 2) given a specific json file path, and only train by those videos
# If you only need to parse and train one list
# Give the dir to json below
# Secondary choice, set full_training_name to None to use this
full_list_path = 'sample_output/base/base_videos_inceltears.json'
# one_path = 'training/test.json' # This is for testing purpose, ignore in real training


# Other parameters:

# Path to a firefox profile with extension installed or other functionality
firefox_profile_with_functions = 'training/firefox-profile/'
# Path to a blank firefox profile
firefox_profile_blank = 'training/firefox-profile-blank'

# Path to local firefox binary
firefox_binary_path = 'firefox-66/firefox/firefox'
# Whether to block the ads:
ads_block = True
# Path to the cookies
# Current account: yout317317@gmail.com, pass: al...b... DOB: 19800101, no gender
# starter cookie before training
seed_cookie_path = 'training/cookiebro-cookies.json'
# where to save cookie after training
training_cookie_path = 'training/after_training_cookie.json'
# How many seconds to watch for each video:
watch_time = 150  # should be more than 5 seconds
# Initial web to visit before train, DO NOT CHANGE unless for other projects
inital_website = 'https://www.youtube.com/'
# Training batch size to prevent memory overload:
training_batch_size = 100  # Must be more than 2, should be more than 20
screenshot_total_counts = 2  # How many screenshot needed
# How many seconds between each screenshots, real intervel will be rougly equal to this
screenshot_interval = 8  # In seconds
# Whether to play at the fastest playback speed
fast = True
# Report time interval, how long between report current status, unit: seconds
report_interval = 10  # should more than 2 seconds


# >>>>>>>>>>>>Third section: for training in parallel mode<<<<<<<<<<<<
# Set to true if train in parallel
# Turn on master mode will override training setting above, including:
# 1) only method 2 will be used, which means only a list provided will be trained
# 2) seed and traning cookies needs be provided here
# 3) log path need to be provided for log and screenshot

# Attention: must set path for Click: export LC_ALL=C.UTF-8, export LANG=C.UTF-8
master_mode = True
log_root_path = '/home/data/xiaoyu/testing3'

# training_list = ['sample_output/base/base_videos_feminism.json',
#                  'sample_output/base/base_videos_inceltears.json',
#                  'sample_output/base/base_videos_metoo.json',
#                  'sample_output/base/base_videos_incel.json',
#                  'sample_output/base/base_videos_enoughtrumpspam.json',
#                  'sample_output/base/base_videos_the_donald.json',
#                  'sample_output/base/base_videos_mensrights.json']

training_list = ['sample_output/extended_RNG/related_videos_RNG_mensrights.json',
                 'sample_output/extended_RNG/related_videos_RNG_incel.json',
                 'sample_output/extended_RNG/related_videos_RNG_enoughtrumpspam.json',
                 'sample_output/extended_RNG/related_videos_RNG_inceltears.json',
                 'sample_output/extended_RNG/related_videos_RNG_feminism.json',
                 'sample_output/extended_RNG/related_videos_RNG_metoo.json',
                 'sample_output/extended_RNG/related_videos_RNG_the_donald.json']

# training_list = ['sample_output/extended_diversity/related_videos_diversity_inceltears.json',
#                  'sample_output/extended_diversity/related_videos_diversity_enoughtrumpspam.json',
#                  'sample_output/extended_diversity/related_videos_diversity_the_donald.json',
#                  'sample_output/extended_diversity/related_videos_diversity_mensrights.json',
#                  'sample_output/extended_diversity/related_videos_diversity_feminism.json',
#                  'sample_output/extended_diversity/related_videos_diversity_incel.json',
#                  'sample_output/extended_diversity/related_videos_diversity_metoo.json']
# For current project, below list length needs to be same with above list length
seed_cookies_list = ['training/cookiebro-cookies.json'] * 7
training_cookies_list = ['training/after_training_cookie.json'] * 7
