# Set your parameters here


# Hyperparameters:
input_path = 'data'  # Input data folder
output_path = 'output'  # Output data folder


# For generating base files
base = True  # Generate base files?
base_video_number = 50  # Each profile contains # of videos
base_shuffle = True  # Shuffle the output list?
base_detailed = True  # Generate a detailed version?


# For generating extended files (two methods)

# 1)
by_diversity = True  # Generate by diversity_index method?
# Choose X = (base_video_number * diversity_index number) top subreddits
# normalize the ratios of these top X subreddits
# choose top videos in each subreddits to
# make up to total X extended videos
diversity_index = 1.0
# Shuffle the output for this method?
extended_shuffle_by_diversity = True

# 2)
by_random_number_generator = True  # Generate by random number method?
# How many digits after decimal points for subreddits ratio:
# e.g. ratio = 0.003, then this value should be 3
subreddit_ratio_decimal = 3
# How many percent of top videos in each subreddit will be chosen
# Default 0.1, i.e. 10%
sampling_percent_index = 0.1
# Shuffle the method for this method?
extended_shuffle_by_random_number = True
