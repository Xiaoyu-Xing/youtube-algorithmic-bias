import itertools
import json
import os
from collections import OrderedDict, namedtuple, defaultdict
from datetime import datetime
from typing import List, Dict, Tuple

import pandas as pd
from deprecated import deprecated

import settings
from src.common_utils.YouTubeVideoRecord import YouTubeVideoRecord


@deprecated
class AnalyzerBySpearman:
    STATEFUL: str = "stateful"
    STATELESS: str = "stateless"
    QUERY: str = "query_result.json"
    REC: str = "recommendation.json"

    def __init__(self, subreddit_path):
        self.subreddit_path: str = subreddit_path
        self.stateful: str = os.path.join(subreddit_path,
                                          AnalyzerBySpearman.STATEFUL)
        self.stateless: str = os.path.join(subreddit_path,
                                           AnalyzerBySpearman.STATELESS)

    def read_and_parse_files(self):
        summary = {"profile": self.subreddit_path}
        query_result_stateful: List[YouTubeVideoRecord] = \
            decode_query_result_json(os.path.join(self.stateful,
                                                  AnalyzerBySpearman.QUERY))
        query_result_stateless: List[YouTubeVideoRecord] = \
            decode_query_result_json(os.path.join(self.stateless,
                                                  AnalyzerBySpearman.QUERY))
        query_stateful_extra, query_stateless_extra, query_common = \
            self.query_result_comparison(query_result_stateful, query_result_stateless)
        query_common_similarity = calculate_spearman_rho(query_common)
        summary["query_result"] = {"stateful extra": len(query_stateful_extra),
                                   "stateless extra": len(query_stateless_extra),
                                   "common": len(query_common),
                                   "similarity coefficient (closer to 1, higher similarity)":
                                       query_common_similarity}
        rec_result_stateful = AnalyzerBySpearman.decode_recommendation_json_with_index(
            os.path.join(self.stateful, AnalyzerBySpearman.REC))
        rec_result_stateless = AnalyzerBySpearman.decode_recommendation_json_with_index(
            os.path.join(self.stateless, AnalyzerBySpearman.REC))
        rec_result_stateful_combined: List[YouTubeVideoRecord] = \
            [each for each_rec_list in rec_result_stateful.values()
             for each in each_rec_list.keys()]
        rec_result_stateless_combined: List[YouTubeVideoRecord] = \
            [each for each_rec_list in rec_result_stateless.values()
             for each in each_rec_list.keys()]
        rec_ful_diff, rec_less_diff, rec_common = \
            self.query_result_comparison(rec_result_stateful_combined,
                                         rec_result_stateless_combined)
        rec_common_similarity = calculate_spearman_rho(rec_common)
        summary["recommendation_results"] = {"stateful extra": len(rec_ful_diff),
                                             "stateless extra": len(rec_less_diff),
                                             "common": len(rec_common),
                                             "similarity coefficient (closer to 1, higher "
                                             "similarity):": rec_common_similarity}
        file_name: str = "summary-" + datetime.now().strftime(settings.time_format_long) + ".txt"
        with open(os.path.join(self.subreddit_path, file_name), "w") as report:
            json.dump(obj=summary, fp=report, indent=4)

        return query_result_stateful, query_result_stateless, rec_result_stateful_combined, \
            rec_result_stateless_combined

    @staticmethod
    def decode_recommendation_json_with_index(file: str) -> Dict[
            str, Dict[YouTubeVideoRecord, int]]:
        if not os.path.exists(file) or not os.path.isfile(file):
            raise RuntimeError("Invalid file input.")
        with open(file, "r") as rec_file:
            content: Dict[str: List[Dict]] = json.load(rec_file)
        for parent_video, recommendations_for_single_video in content.items():
            content[parent_video] = {YouTubeVideoRecord.decoder(record): index
                                     for index, record in
                                     enumerate(recommendations_for_single_video)}
        return content

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
    def generate_report():

        def cross_comparison(profile1_list, profile2_list, profile1_name, profile2_name, state):
            summary = {"name": "profile 1: {} vs profile 2: {} on {}.".format(
                profile1_name, profile2_name, state)}
            profile1_extra, profile2_extra, profile_common = \
                AnalyzerBySpearman.query_result_comparison(profile1_list,
                                                           profile2_list)
            summary["profile 1 extra"] = len(profile1_extra)
            summary["profile 2 extra"] = len(profile2_extra)
            summary["common"] = len(profile_common)
            summary["similarity of common"] = calculate_spearman_rho(profile_common)
            return summary

        pilot_data_path = "input_data/pilot_test_result"
        names = ["enoughtrumpspam", "the_donald", "blank"]
        results = {}
        for name in names:
            pilot_data_full_path = os.path.join(settings.ROOT_DIR, pilot_data_path, name)
            results[name] = AnalyzerBySpearman(
                pilot_data_full_path).read_and_parse_files()
        four_result_name = ["query stateful", "query stateless",
                            "recommendation stateful", "recommendation stateless"]
        inter_file_name: str = "inter-subreddits summary-" \
                               + datetime.now().strftime(settings.time_format_long) + ".txt"
        with open(inter_file_name, "w") as f:
            for i in range(len(names)):
                profile1 = names[i]
                profile2 = names[(i + 1) % len(names)]
                for argument in zip(results[profile1], results[profile2],
                                    itertools.repeat(profile1), itertools.repeat(profile2),
                                    four_result_name):
                    comparison_result = cross_comparison(*argument)
                    json.dump(obj=comparison_result, fp=f, indent=4)


class QueryAndRecommendationResult:
    QUERY = "query_result"
    REC = "recommendation"

    def __init__(self, raw_data: Dict):
        query_result: pd.DataFrame = pd.DataFrame(raw_data[QueryAndRecommendationResult.QUERY])
        recommendation: pd.DataFrame = pd.DataFrame(raw_data[QueryAndRecommendationResult.REC])
        self.df: pd.DataFrame = pd.concat([query_result, recommendation],
                                          keys=[QueryAndRecommendationResult.QUERY,
                                                QueryAndRecommendationResult.REC],
                                          sort=False)

    def get_query_result(self) -> Dict:
        return self.df.xs(QueryAndRecommendationResult.QUERY).to_dict()

    def get_rec_result(self) -> Dict:
        return self.df.xs(QueryAndRecommendationResult.REC).to_dict()

    def get_subreddits(self) -> List[str]:
        return self.df.columns.tolist()

    def get_query_result_for_tag(self, tag):
        return self.df.xs(QueryAndRecommendationResult.QUERY).xs(tag).to_dict()

    def get_rec_result_for_tag(self, tag):
        return self.df.xs(QueryAndRecommendationResult.REC).xs(tag).to_dict()

    def get_query_result_for_a_subreddit(self, subreddit):
        return self.df.xs(QueryAndRecommendationResult.QUERY).xs(subreddit, 1).to_dict()

    def get_rec_result_for_a_subreddit(self, subreddit):
        return self.df.xs(QueryAndRecommendationResult.REC).xs(subreddit, 1).to_dict()

    def get(self, category, tag, subreddit):
        return self.df.xs(category).xs(tag).xs(subreddit)


class AnalyzerByLevenshtein:
    def __init__(self):
        data_directories_with_timestamp: List[(datetime, int, str)] = []
        for dir_name in os.listdir(settings.DATA_ROOT):
            timestamp: str = dir_name.split("#")[0]
            sequence: int = int(dir_name.split("#")[1])
            data_directories_with_timestamp.append((datetime.strptime(timestamp,
                                                                      settings.time_format_short),
                                                    sequence,
                                                    dir_name))
        data_directories_with_timestamp.sort(key=lambda t: (t[0], t[1]))
        print(data_directories_with_timestamp)
        self.seed_dir = None
        if len(data_directories_with_timestamp) > 1 and data_directories_with_timestamp[0][1] == 0:
            self.seed_dir = os.path.join(settings.DATA_ROOT, data_directories_with_timestamp[0][-1])
        self.most_recent_dir = os.path.join(settings.DATA_ROOT,
                                            data_directories_with_timestamp[-1][-1])
        print(self.seed_dir, self.most_recent_dir)
        self.most_recent_files_content: QueryAndRecommendationResult = \
            self.decode_records_from_data_directory(self.most_recent_dir)

        if self.seed_dir:
            self.seed_files_content: QueryAndRecommendationResult = \
                self.decode_records_from_data_directory(self.seed_dir)

    def run_analysis(self):
        self.inter_subreddit_comparison()
        if self.seed_dir:
            self.seed_recent_comparison()

    @staticmethod
    def decode_records_from_data_directory(directory: str) -> QueryAndRecommendationResult:
        most_recent_files: List[str] = [file for file in os.listdir(directory)
                                        if os.path.isfile(os.path.join(directory, file))]
        result: Dict = {"query_result": defaultdict(dict), "recommendation": defaultdict(dict)}
        for file in most_recent_files:
            subreddit, tag, category = os.path.splitext(file)[0].split("-")
            if "query_result" in category:
                result[category][subreddit][tag] = \
                    decode_query_result_json(os.path.join(directory, file))
            else:
                result[category][subreddit][tag] = \
                    decode_recommendation_json(os.path.join(directory, file))
        return QueryAndRecommendationResult(result)

    def inter_subreddit_comparison(self):
        subreddits: List[str] = self.most_recent_files_content.get_subreddits()
        query_result_edit_distances: Dict = {i: {j: None for j in subreddits} for i in subreddits}
        recommendation_edit_distances: Dict = {i: {j: None for j in subreddits} for i in subreddits}
        query_result_for_stateful: Dict = \
            self.most_recent_files_content.get_query_result_for_tag("stateful")
        query_result_for_stateless: Dict = \
            self.most_recent_files_content.get_query_result_for_tag("stateless")
        rec_result_for_stateful: Dict = \
            self.most_recent_files_content.get_rec_result_for_tag("stateful")
        rec_result_for_stateless: Dict = \
            self.most_recent_files_content.get_rec_result_for_tag("stateless")
        for subreddit_a, subreddit_b in itertools.combinations(subreddits, 2):
            query_result_edit_distances[subreddit_a][subreddit_b] = \
                levenshtein_distance(query_result_for_stateful[subreddit_a],
                                     query_result_for_stateful[subreddit_b])
            query_result_edit_distances[subreddit_b][subreddit_a] = \
                levenshtein_distance(query_result_for_stateless[subreddit_a],
                                     query_result_for_stateless[subreddit_b])
            recommendation_edit_distances[subreddit_a][subreddit_b] = \
                self.recommendation_levenshtein_distance(rec_result_for_stateful[subreddit_a],
                                                         rec_result_for_stateless[subreddit_b])
            recommendation_edit_distances[subreddit_b][subreddit_a] = \
                self.recommendation_levenshtein_distance(rec_result_for_stateful[subreddit_a],
                                                         rec_result_for_stateless[subreddit_b])
        for subreddit in subreddits:
            query_result_edit_distances[subreddit][subreddit] = \
                levenshtein_distance(query_result_for_stateful[subreddit],
                                     query_result_for_stateless[subreddit])
            recommendation_edit_distances[subreddit][subreddit] = \
                self.recommendation_levenshtein_distance(rec_result_for_stateful[subreddit],
                                                         rec_result_for_stateless[subreddit])
        combined_results: pd.DataFrame = pd.concat(
            [pd.DataFrame(query_result_edit_distances),
             pd.DataFrame(recommendation_edit_distances)],
            keys=["query_result", "recommendation"])

        with open("inter-subreddits-comparison.csv", "a+") as f:
            combined_results.to_csv(path_or_buf=f)
            f.write("\n")

        return combined_results

    def seed_recent_comparison(self):
        subreddits: List[str] = self.most_recent_files_content.get_subreddits()
        query_result_edit_distances: Dict = {i: {"stateful": None, "stateless": None}
                                             for i in subreddits}
        rec_result_edit_distances: Dict = {i: {"stateful": None, "stateless": None}
                                           for i in subreddits}
        for subreddit in subreddits:
            for tag in ["stateful", "stateless"]:
                query_result_edit_distances[subreddit][tag] = levenshtein_distance(
                    self.seed_files_content.get("query_result", tag, subreddit),
                    self.most_recent_files_content.get("query_result", tag, subreddit))
                rec_result_edit_distances[subreddit][tag] = \
                    self.recommendation_levenshtein_distance(
                        self.seed_files_content.get("recommendation", tag, subreddit),
                        self.most_recent_files_content.get("recommendation", tag, subreddit))

        combined_results = pd.concat(
            [pd.DataFrame(query_result_edit_distances), pd.DataFrame(rec_result_edit_distances)],
            keys=["query_result", "recommendation"])

        with open("seed-recent-comparison.csv", "a+") as f:
            combined_results.to_csv(path_or_buf=f)
            f.write("\n")

        return combined_results

    @staticmethod
    def recommendation_levenshtein_distance(rec_a: Dict, rec_b: Dict) -> float:
        edit_distances: List[float] = []
        for url_a, rec_list_a in rec_a.items():
            if url_a not in rec_b:
                continue
            edit_distances.append(levenshtein_distance(rec_list_a, rec_b[url_a]))
        edit_distances_data_frame: pd.DataFrame = pd.DataFrame(edit_distances)
        return float(edit_distances_data_frame.mean().round(4))


def decode_recommendation_json(file: str) -> Dict[str, List[YouTubeVideoRecord]]:
    if not os.path.exists(file) or not os.path.isfile(file):
        raise RuntimeError("Invalid file input.")
    with open(file, "r") as rec_file:
        content: Dict[str: List[Dict]] = json.load(rec_file)
    for parent_video, recommendations_for_single_video in content.items():
        content[parent_video] = [YouTubeVideoRecord.decoder(record)
                                 for record in recommendations_for_single_video]
    return content


def decode_query_result_json(file: str) -> List[YouTubeVideoRecord]:
    if not os.path.exists(file) or not os.path.isfile(file):
        raise RuntimeError("Invalid file input.")
    with open(file, "r") as query_file:
        return json.load(query_file, object_hook=YouTubeVideoRecord.decoder)


def calculate_spearman_rho(common_videos_with_indices: Dict[str, Tuple[int, int]]) -> int:
    """
    calculate edit distance for two lists with common comment but different ranking
    :param common_videos_with_indices: Dict of video url with indices in two lists
    :return:
    """
    n = 0
    diff_sum = 0
    for index_pair in common_videos_with_indices.values():
        diff_sum += (index_pair[0] - index_pair[1]) ** 2
        n = max(n, index_pair[0], index_pair[1])
    return 1 - 6 * diff_sum / (n * (n ** 2 - 1))


def levenshtein_distance(source: List[YouTubeVideoRecord],
                         target: List[YouTubeVideoRecord]) -> float:
    """
    Edit distance converting source video list to target video list
    reference: https://en.wikipedia.org/wiki/Levenshtein_distance
    :param source:
    :param target:
    :return: the edit distance
    """
    size_a: int = len(source) + 1
    size_b: int = len(target) + 1
    mem: List[List[int]] = [[0 for _ in range(size_b)] for _ in range(size_a)]
    for i in range(1, size_a):
        mem[i][0] = i
    for j in range(1, size_b):
        mem[0][j] = j
    for j in range(1, size_b):
        for i in range(1, size_a):
            substitution_cost = 0
            if source[i - 1] != target[j - 1]:
                substitution_cost = 1
            mem[i][j] = min(mem[i - 1][j] + 1,
                            mem[i][j - 1] + 1,
                            mem[i - 1][j - 1] + substitution_cost)
    percentage = mem[size_a - 1][size_b - 1] / max(len(source), len(target))
    return round(percentage, 4)


if __name__ == '__main__':
    analyzer = AnalyzerByLevenshtein()
    analyzer.run_analysis()
