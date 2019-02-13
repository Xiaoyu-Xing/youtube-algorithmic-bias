# youtube-algorithmic-bias

## Generic Research Method:

### 1. Generate base profiles: 
Based on 7 profile data from reddit, a number of videos **X** for each profile can be specified, for example: 50. 
Then top 50 videos for each profile (based on upvotes) will be selected as the base profile, 
if any profile total videos are less than specified number, then all of them will be chosen. Videos can be shuffled to ensure randomness.

### 2. Generate extended profiles: 
Based on 7 extended profiles, a diversity number **N** can be choosen, for example: 1.2. 
It means: top **X\*N** (50\*1.2) subreddits that have cross population with those base profiles will be chosen, 
then for each profile, these top subreddits ratio **R** will be normalized. 
The videos for each subreddits will be caculated by **K** = **R**\***X\*N**, round to nearest integer. 
Top upvotes videos for each subreddit will be chosen based on the calculated number **K**. Videos can be shuffled to ensure randomness.

### 3. Training:
Using multiple machine, potentially cloud service, such as AWS, set up watching process for profiles 
at the same time (same clock time, and same day, and same server). 
Either watch for a certain time or the whole video before next one on the list (txt or json). 

### 4. Testing:
for those trained profiles, either: 1) use one same seed videos, check the recommendation list or 2) ...
