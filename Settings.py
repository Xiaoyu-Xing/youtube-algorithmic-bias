# Fix: 1. time stamp on youtube link '?t='' 
# 2. document: settings details here, research method on onenote, how to run in readme
# 3. disgard window handle method, use firefox profiles to load pre-installed extention and start firefox binary from local

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


# For generating extended files (two methods)

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
# e.g. ratio = 0.003, then this value should be 3
subreddit_ratio_decimal = 3  # the precision of ratio
# How many percent of top videos in each subreddit will be chosen
# Default 0.1, i.e. 10%
sampling_percent_index = 0.1
# Shuffle the output for this method?
extended_shuffle_by_random_number = True


# >>>>>>>>>>>>Second section: for training profiles<<<<<<<<<<<<
headless = False  # running in linux server need to run without GUI, then set to True
# If you need to parse all json files
# Give the dir to the lowest common folder below
training_directory = 'sample_output'
# If you only need to parse and train one list
# Give the dir to json below
one_path = 'training/test.json'
# Path to a firefox profile
firefox_profile_path = ''
# Path to the cookies
seed_cookie_path = 'training/cookiebro-cookies.json'  # DO NOT OVERRIDE
training_coockie_path = 'training/after_training_cookie.json'
# How many seconds to watch for each video:
watch_time = 30
# Initial web to visit before train, DO NOT CHANGE
inital_website = 'https://www.youtube.com/'
# Current account: yout317317, pass: al...b... 19800101, no gender
# Training batch size to prevent memory overload:
training_batch_size = 20
# full training process:
# full traning profile name, use the reddit name, check the keys summary.json file
# If not None, make sure training_directory is valid
full_training_name = 'the_donald'
# choose among 'base', 'diversity', 'RNG'
full_training_category = 'base'
# Or use the path to the full list you need to train
full_list_path = ''  # Secondary choice, set full_training_name to None to use this
# path to ad block extension for firefox
# adblock pro is the only one found so far not pop up new page after installation!
ad_block_path = 'adblock_for_firefox-3.25.0-an+fx.xpi'
# Whether to play at the fastest playback speed
fast = True
# Report time interval, how long between report current status, unit: seconds
report_interval = 5 # should more than 2 seconds
