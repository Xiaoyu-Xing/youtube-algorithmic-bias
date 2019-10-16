import os
import time
from datetime import datetime
from pprint import pprint
import multiprocessing as mp

import schedule

import settings
from src.data_pipeline.ProfileTrainAndTestPipeline import train_and_test_profile
from src.profile_query_tester.PilotABTestResultAnalyser import AnalyzerByLevenshtein


class ScheduledJobController:
    def __init__(self):
        self.sequence = 0

    def get_and_update_sequence(self):
        print(f"Current job sequence {self.sequence}, time {datetime.now()}")
        ret = self.sequence
        self.sequence += 1
        return ret


def query_multiprocessing_job(sequence):
    sequence_number = sequence.get_and_update_sequence()
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
    controller = ScheduledJobController()
    schedule.every(3).hours.do(query_multiprocessing_job, controller)
    schedule.run_all()
    while controller.sequence <= 2:
        schedule.run_pending()
        time.sleep(1)
