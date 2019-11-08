import os
import time
from datetime import datetime
from pprint import pprint
import multiprocessing as mp

import schedule

import settings
from src.data_pipeline.ProfileTrainAndTestPipeline import train_and_test_profile
from src.profile_query_tester.PilotABTestResultAnalyser import AnalyzerByLevenshtein
from src.common_utils.VirtualScreen import VirtualScreen


class ScheduledJobController:
    def __init__(self, start_sequence, end_sequence):
        self.start = start_sequence
        self.end = end_sequence

    def get_and_update_sequence(self):
        print(f"Current job sequence {self.start}, current time {datetime.now()}, "
              f"sequence end {self.end}.")
        ret = self.start
        self.start += 1
        return ret

    def job_not_finish(self):
        return self.start <= self.end


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
            arguments.append((subreddit, tag, cookie_path, video_path, sequence_number))
    pprint(arguments)
    with VirtualScreen():
        with mp.Pool(processes=len(arguments), maxtasksperchild=1) as pool:
            ret = pool.starmap(train_and_test_profile, arguments)
            pprint("Query result and recommendation saved at {}".format(ret))

    analyzer = AnalyzerByLevenshtein()
    analyzer.run_analysis()


if __name__ == '__main__':
    controller = ScheduledJobController(11, 60)
    mp.set_start_method("spawn")
    schedule.every().day.at("08:00").do(query_multiprocessing_job, controller)
    schedule.run_all()
    while controller.job_not_finish():
        schedule.run_pending()
        time.sleep(1)
