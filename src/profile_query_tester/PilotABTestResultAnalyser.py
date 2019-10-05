import copy
import itertools
import json
import os
import random
from collections import OrderedDict
from typing import List, Dict, Tuple

import settings
from src.common_utils.YouTubeVideoRecord import YouTubeVideoRecord


class PilotAnalyzer:
    STATEFUL: str = "stateful"
    STATELESS: str = "stateless"
    QUERY: str = "query_result.json"
    REC: str = "recommendation.json"

    def __init__(self, subreddit_path):
        self.subreddit_path: str = subreddit_path
        self.stateful: str = os.path.join(subreddit_path, PilotAnalyzer.STATEFUL)
        self.stateless: str = os.path.join(subreddit_path, PilotAnalyzer.STATELESS)

    def read_and_parse_files(self):
        summary = {"profile": self.subreddit_path}
        query_result_stateful: List[YouTubeVideoRecord] = PilotAnalyzer \
            .decode_video_query_records(os.path.join(self.stateful, PilotAnalyzer.QUERY))
        query_result_stateless: List[YouTubeVideoRecord] = PilotAnalyzer \
            .decode_video_query_records(os.path.join(self.stateless, PilotAnalyzer.QUERY))
        query_stateful_extra, query_stateless_extra, query_common = \
            self.query_result_comparison(query_result_stateful, query_result_stateless)
        query_common_similarity = PilotAnalyzer.calculate_spearman_rho(query_common)
        summary["query_result"] = {"stateful extra": len(query_stateful_extra),
                                   "stateless extra": len(query_stateless_extra),
                                   "common": len(query_common),
                                   "similarity coefficient (closer to 1, higher similarity)":
                                       query_common_similarity}
        rec_result_stateful = PilotAnalyzer.decode_video_rec_records(
            os.path.join(self.stateful, PilotAnalyzer.REC))
        rec_result_stateless = PilotAnalyzer.decode_video_rec_records(
            os.path.join(self.stateless, PilotAnalyzer.REC))
        rec_result_stateful_combined: List[YouTubeVideoRecord] = \
            [each for each_rec_list in rec_result_stateful.values()
             for each in each_rec_list.keys()]
        rec_result_stateless_combined: List[YouTubeVideoRecord] = \
            [each for each_rec_list in rec_result_stateless.values()
             for each in each_rec_list.keys()]
        rec_ful_diff, rec_less_diff, rec_common = \
            self.query_result_comparison(rec_result_stateful_combined,
                                         rec_result_stateless_combined)
        rec_common_similarity = PilotAnalyzer.calculate_spearman_rho(rec_common)
        summary["recommendation_results"] = {"stateful extra": len(rec_ful_diff),
                                             "stateless extra": len(rec_less_diff),
                                             "common": len(rec_common),
                                             "similarity coefficient (closer to 1, higher "
                                             "similarity):": rec_common_similarity}

        with open(os.path.join(self.subreddit_path, "summary.txt"), "w") as report:
            json.dump(obj=summary, fp=report, indent=4)

        return query_result_stateful, query_result_stateless, rec_result_stateful_combined, \
            rec_result_stateless_combined

    @staticmethod
    def calculate_spearman_rho(common_videos_with_index: Dict[str, Tuple[int, int]]) -> int:
        n = 0
        diff_sum = 0
        for index_pair in common_videos_with_index.values():
            diff_sum += (index_pair[0] - index_pair[1]) ** 2
            n = max(n, index_pair[0], index_pair[1])
        return 1 - 6 * diff_sum / (n * (n ** 2 - 1))

    @staticmethod
    def query_result_comparison(videos_list_first: List[YouTubeVideoRecord],
                                videos_list_second: List[YouTubeVideoRecord]) \
            -> Tuple[set, set, Dict[str, Tuple]]:
        videos_dict_first: Dict = OrderedDict()
        for first_index, record in enumerate(videos_list_first):
            if record not in videos_dict_first:
                videos_dict_first[record] = first_index
        videos_dict_second: Dict = OrderedDict()
        for first_index, record in enumerate(videos_list_second):
            if record not in videos_dict_second:
                videos_dict_second[record] = first_index
        extra_in_first: set = set(videos_dict_first.keys() - videos_dict_second.keys())
        extra_in_second: set = set(videos_dict_second.keys() - videos_dict_first.keys())
        common_videos = videos_dict_first.keys() & videos_dict_second.keys()  # intersection of set
        common_videos_with_index: Dict[str, Tuple[int, int]] = \
            {record: (videos_dict_first[record], videos_dict_second[record])
             for record in common_videos}
        return extra_in_first, extra_in_second, common_videos_with_index

    @staticmethod
    def decode_video_query_records(file: str) -> List[YouTubeVideoRecord]:
        if not os.path.exists(file) or not os.path.isfile(file):
            raise RuntimeError("Invalid file input.")
        with open(file, "r") as query_file:
            return json.load(query_file, object_hook=YouTubeVideoRecord.decoder)

    @staticmethod
    def decode_video_rec_records(file: str) -> Dict[str, Dict[YouTubeVideoRecord, int]]:
        if not os.path.exists(file) or not os.path.isfile(file):
            raise RuntimeError("Invalid file input.")
        with open(file, "r") as rec_file:
            content: Dict[str: List[Dict]] = json.load(rec_file)
        for parent_video, recommendation_video_list in content.items():
            content[parent_video] = {YouTubeVideoRecord.decoder(record): index
                                     for index, record in enumerate(recommendation_video_list)}
        return content


def cross_comparison(profile1_list, profile2_list, profile1_name, profile2_name, state):
    summary = {"name": "profile 1: {} vs profile 2: {} on {}.".format(
        profile1_name, profile2_name, state)}
    profile1_extra, profile2_extra, profile_common = \
        PilotAnalyzer.query_result_comparison(profile1_list, profile2_list)
    summary["profile 1 extra"] = len(profile1_extra)
    summary["profile 2 extra"] = len(profile2_extra)
    summary["common"] = len(profile_common)
    summary["similarity of common"] = PilotAnalyzer.calculate_spearman_rho(profile_common)
    return summary


if __name__ == '__main__':
    pilot_data_path = "input_data/pilot_test_result"
    names = ["enoughtrumpspam", "the_donald", "blank"]
    results = {}
    for name in names:
        pilot_data_full_path = os.path.join(settings.ROOT_DIR, pilot_data_path, name)
        results[name] = PilotAnalyzer(pilot_data_full_path).read_and_parse_files()
    four_result_name = ["query stateful", "query stateless",
                        "recommendation stateful", "recommendation stateless"]

    with open("inter-subreddits summary.txt", "w") as f:
        for i in range(len(names)):
            profile1 = names[i]
            profile2 = names[(i + 1) % len(names)]
            for argument in zip(results[profile1], results[profile2],
                                itertools.repeat(profile1), itertools.repeat(profile2),
                                four_result_name):
                comparison_result = cross_comparison(*argument)
                json.dump(obj=comparison_result, fp=f, indent=4)

    test = results["enoughtrumpspam"][-1]
    test_shuffle = copy.deepcopy(test)
    random.shuffle(test_shuffle)
    print(cross_comparison(test, test_shuffle, "ets", "ets_shuffle", "shuffled"))

    test2 = results["enoughtrumpspam"][0]
    test2_shuffle = copy.deepcopy(test2)
    random.shuffle(test2_shuffle)
    print(cross_comparison(test2, test2_shuffle, "ets", "ets_shuffle", "shuffled"))
