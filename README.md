# youtube-algorithmic-bias

## Generic Research Method:

### 1. Generate base profiles: 
Based on 7 profile data from reddit, a number of videos **X** for each profile can be specified, for example: 50. 
Then top 50 videos for each profile (based on upvotes) will be selected as the base profile, 
if any profile total videos are less than specified number, then all of them will be chosen. Videos can be shuffled to ensure randomness.

### 2. Generate extended profiles (two method):
1) By random number generator:
Let D be the digits after decimal points of ratio in the profiles, R be the ratio, C be a random number generated in the range of [0, 10^D). If C <= R\*10^D, the top P% videos in this subreddit would be chosen into the extended list. Default P is 10 (so 10% of the top videos will be sampled if this subreddit is chosen). For each subreddit in each profile, above random choosing process is perfomed, total videos chosen will be sampled together with base videos as one extended profile. Videos can be shuffled to ensure randomness.
2) By diversity index: 
Based on the profiles, a diversity number **N** can be choosen, for example: 1.2. 
Then top (ranked by overlaping ratio) **X\*N** (here 50\*1.2=60) subreddits that have cross population with those base profiles will be chosen, 
then for each profile, those top (60) subreddits will be normalized on their overlap ratio. The normalized ratio is denoted as **R**. 
The number of videos for each subreddits will be caculated by **K** = **R**\***X\*N**, round to nearest integer. 
Top upvotes videos for each subreddit will be chosen based on the calculated number **K**. Those chosen videos will be sampled together with base videos as one extended profile. Videos can be shuffled to ensure randomness.

### 3. Training:
Using multiple machine, potentially cloud service, such as AWS, set up watching process for profiles 
at the same time (same clock time, and same day, and same server). 
Either watch for a certain time or the whole video before next one on the list (txt or json). 

### 4. Testing:
for those trained profiles, either: 1) use one same seed videos, check the recommendation list or 2) ...
