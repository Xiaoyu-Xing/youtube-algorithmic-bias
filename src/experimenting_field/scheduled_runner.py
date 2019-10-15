import os
import time
from pprint import pprint
import multiprocessing as mp

import schedule

import settings
from src.data_pipeline.ProfileTrainAndTestPipeline import train_and_test_profile
from src.profile_query_tester.PilotABTestResultAnalyser import AnalyzerByLevenshtein


def query_multiprocessing_job(sequence_number):
    subreddits = ["enoughtrumpspam", "blank", "the_donald"]
    tags = ["stateful", "stateless"]
    arguments = []
    for tag in tags:
        for subreddit in subreddits:
            cookie_path = os.path.join(settings.ROOT_DIR, settings.INPUT_DATA,
                                       f"{tag}_cookies", f"{subreddit}.json")
            video_path = os.path.join(settings.ROOT_DIR, settings.INPUT_DATA,
                                      f"{tag}_videos", f"base_videos_{subreddit}.json") \
                if sequence_number == 0 and subreddit != "blank" else ""

            arguments.append((subreddit, tag, cookie_path, video_path))
    pprint(arguments)
    mp.set_start_method("spawn")
    with mp.Pool(processes=len(arguments), maxtasksperchild=1) as pool:
        pool.starmap(train_and_test_profile, arguments)

    analyzer = AnalyzerByLevenshtein()
    analyzer.run_analysis()


if __name__ == '__main__':
    sequence = 0
    schedule.every(3).hours.do(query_multiprocessing_job, sequence)
    while sequence < 5:
        schedule.run_pending()
        sequence += 1
        time.sleep(5)