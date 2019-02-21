import os
import random
import json
from pprint import pprint
import math
import sys
import Settings


class Build_Profiles:
        # Specify data location, and output location.
    def __init__(self,
                 input_path=Settings.input_path,
                 output_path=Settings.output_path,
                 limit=Settings.base_video_number):
        '''
        Input:
            input_path: data dir, default '/data'
            output_put: output dir, default '/ouput', make dir if not exists
        '''
        self.input_path = input_path
        self.output_path = output_path
        if not os.path.exists(self.input_path):
            raise Exception('Input path not found, or /Data folder not exist.')
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)
        # Average profile details, keyed with last word of each json profile filename
        self.profiles = {}
        # Fully normalized profiles based on all the subreddits they have
        self.profiles_norm_ratio = {}
        # Partially normalized profiles based on top N*diversity subreddits
        self.profiles_norm_ratio_N_diversity = {}
        # *_dirs are the root directories path for files of profiles, base/related videos
        self.profiles_dir, self.videos_base_dir, self.videos_related_dir = '', '', ''
        # Names of files are stored separately, used together with dir path above
        self.profiles_files, self.videos_base_files, self.videos_related_files = [], [], []
        # Profile videos for each profile, keyed with filename of each json base-video filename
        # Non-detailed version only contains urls in a List,
        # Detailed version, keyed by the url, contains author, timestamp, score, and title.
        self.base_videos, self.base_videos_details, self.base_videos_summary = {}, {}, {}
        # Extended/related profile videos for each profile, keyed with filename of each json related-video filename
        self.related_videos, self.related_videos_details, self.related_videos_summary = {}, {}, {}
        # Run to parse the input folder
        self._parse_folders()
        # Run to generate profile details
        self._generate_profiles()
        # Profile video upper bound
        self.limit = limit

    # Parse data folder
    def _parse_folders(self):
        path = self.input_path
        for (cur_dirpath, sub_dirnames, cur_filenames) in os.walk(path):
            # Average profile files
            if 'profiles' in cur_dirpath:
                self.profiles_dir = cur_dirpath
                self.profiles_files = cur_filenames
            # Base videos, parse json files only
            elif 'videos' in cur_dirpath and 'base' in cur_dirpath:
                self.videos_base_dir = cur_dirpath
                self.videos_base_files = [
                    each for each in cur_filenames if 'ndjson' not in each]
            # Related videos, parse json files only
            elif 'videos' in cur_dirpath and 'related' in cur_dirpath and 'ndjson' not in cur_dirpath:
                self.videos_related_dir = cur_dirpath
                self.videos_related_files = cur_filenames

    # Read json file
    def _read_json(self, path):
        '''
        Input:
            path: file path
        Return:
            json file, lenght, type
        '''
        with open(path) as f:
            jfile = json.load(f)
        return jfile, len(jfile), type(jfile)

    # Populate profile details
    def _generate_profiles(self):
        for profile in self.profiles_files:
            if 'ndjson' in profile or 'table' in profile:  # Skip ndjson
                continue
            # Use last word as key
            name = os.path.splitext(profile)[0].split('_', 2)[-1]
            profile_path = os.path.join(self.profiles_dir, profile)
            self.profiles[name] = self._read_json(profile_path)[0]

    # Collect all the videos from a json file
    def _load_videos(self, file):
        '''
        Input:
            file: json file path
        Return:
            video list, and detailed video dict keyed with url
        '''
        videos_short, videos_details = [], []
        videos, length, _ = self._read_json(file)
        for video in videos:
            videos_short.append(video['url'])
            details = video.copy()
            del details['url']
            videos_details.append({video['url']: details})
        return videos_short, videos_details

    # Collect all the base videos for all profiles
    def _build_profiles_base(self):
        for file in self.videos_base_files:
            path = os.path.join(self.videos_base_dir, file)
            v, v_d = self._load_videos(path)
            key = os.path.splitext(file)[0]
            self.base_videos[key] = v[:self.limit]
            self.base_videos_details[key] = v_d[:self.limit]
            self.base_videos_summary[key] = len(self.base_videos[key])

    # Give data and file_path (need include .json extension), write file, overwrite if exists.
    def _write_json(self, data, file):
        '''
        Input:
            data: data to write
            file: file path to write
        '''
        with open(file, 'w') as f:
            # Indent will help json viewer properly display the format
            json.dump(data, f, indent=4)

    # Generate files based on the base output
    # Only output file will be shuffled is shuffle is True, the class attributes will not be shuffled,
    # to prevent uneven shuffle after sampled with related videos
    # Turn details False will stop write detailed version of videos
    def output_profiles_base(self,
                             shuffle=Settings.base_shuffle,
                             details=Settings.base_detailed):
        '''
        Input:
            shuffle: boolean, whether to shuffle the ourput
            details: boolean, whether to output detailed version
        '''
        # Run to generate base profile videos
        self._build_profiles_base()
        out_path = self.output_path
        for file, videos in self.base_videos.items():
            name_base = 'base_videos_' + file + '.json'
            data = videos[:]
            if shuffle:
                random.shuffle(data)
            self._write_json(data, os.path.join(out_path, name_base))
        self._write_json(self.base_videos_summary,
                         os.path.join(out_path, 'base_summary.json'))
        if details:
            for file, videos in self.base_videos_details.items():
                name_base_details = 'base_videos_details_' + file + '.json'
                data = videos[:]
                if shuffle:
                    random.shuffle(data)
                self._write_json(data, os.path.join(
                    out_path, name_base_details))

    # Read a json profile file, output content, lenght, type. For external use.
    def read_json(self, file_path):
        return self._read_json(file_path)

    # Read a json video file, output short list (url only), detailed list. For external use.
    def read_videos(self, file_path):
        return self._load_videos(file_path)

    def _load_related_videos(self, file):
        '''
        Input:
            file: json file path
        Return:
            video list, and detailed video dict keyed with url
        '''
        videos_short, videos_details = [], []
        videos, length, _ = self._read_json(file)
        for video in videos['data']:
            videos_short.append(video['url'])
            details = video.copy()
            del details['url']
            videos_details.append({video['url']: details})
        return videos_short, videos_details

    def _build_profiles_related(self):
        for file in self.videos_related_files:
            key = os.path.splitext(file)[0]
            path = os.path.join(self.videos_related_dir, file)
            v, v_d = self._load_related_videos(path)
            self.related_videos[key] = v
            self.related_videos_details[key] = v_d
            self.related_videos_summary[key] = len(self.related_videos[key])

    # NOT IN USE: normalize the profile ratios for all subreddits contained.
    def _normalize_profile_ratios(self):
        for profile_name, details in self.profiles.items():
            total = sum([float(v['ratio']) for v in details.values()])
            print(profile_name, total)
            self.profiles_norm_ratio[profile_name] = {
                k: float(v['ratio']) / total for k, v in details.items()}

    # Normalize profile ratios only for top N subreditts.
    # N is the "diversity" determined by base video numbers, read from base_summary
    # Must run output_profile_base first!
    def _normalize_profile_ratios_N_diversity(self,
                                              diversity_index):
        for profile_name, details in self.profiles.items():
            N = round(self.base_videos_summary[profile_name] * diversity_index)
            temp = sorted([(k, float(v['ratio'])) for k, v in details.items()], key=lambda x: x[1], reverse=True
                          )[:N]
            total = sum([each[1] for each in temp])
            self.profiles_norm_ratio_N_diversity[profile_name] = [
                (each[0], round(each[1] / total * N)) for each in temp]

    # First method to implement the extended file:
    # Each profile consists of: 1) base profile #: max(videos_in_base_profile, top_LIMIT_in_base_profile)
    # 2) N*# of extended videos from subreddits by <1> normalize ratios for each subreddits for top LIMIT videos
    # <2> total # of extended videos (roughly) equals to # of base profile, choose top N videos calculated by ratio，
    # rounded up/down to whole number
    def output_profiles_related_diversity_method(self,
                                                 shuffle=Settings.extended_shuffle_by_diversity,
                                                 diversity_index=Settings.diversity_index):
        '''
        diversity_index: control the ratio of extended videos / base videos numbers
        '''
        # Process the related/extended videos if not yet.
        if len(self.related_videos_summary) == 0:
            print(
                "*****This step might take long time and large memory, please hold tight!*****\n")
            sys.stdout.flush()
            self._build_profiles_related()
        self._normalize_profile_ratios_N_diversity(diversity_index)
        out_path = self.output_path
        summary = {}
        summary['diversity_index'] = diversity_index
        for profile_name, details in self.profiles_norm_ratio_N_diversity.items():
            # Make a local copy of base videos, don't mess up with base files
            short = self.base_videos[profile_name][:]
            for subreddit, count in details:
                try:
                    short.extend(self.related_videos[subreddit][:count])
                except Exception as e:
                    print(e)
                    print(
                        "Check related video folder or above subreddit name to match each other.")
            if shuffle:
                random.shuffle(short)
            summary[profile_name] = len(short)
            name_related = 'related_videos_diversity_' + profile_name + '.json'
            self._write_json(short, os.path.join(out_path, name_related))
        self._write_json(summary,
                         os.path.join(out_path, 'related_summary.json'))

    def output_profiles_related_RNG_method(self,
                                           shuffle=Settings.extended_shuffle_by_random_number,
                                           sampling_index=Settings.sampling_percent_index):
        # Process the related/extended videos if not yet.
        if len(self.related_videos_summary) == 0:
            print(
                "*****This step might take long time and large memory, please hold tight!*****\n")
            sys.stdout.flush()
            self._build_profiles_related()
        # Hyperparameter: significant digits after decimal of overlapping ratios with subreddits in base profiles
        DIGIT = Settings.subreddit_ratio_decimal
        out_path = self.output_path
        summary = {}
        for profile_name, details in self.profiles.items():
            # Make a local copy of base videos, don't mess up with base files
            short = self.base_videos[profile_name][:]
            subreddits_count = 0
            for subreddit_name, detail in details.items():
                this_chance = random.choice(range(pow(10, DIGIT)))
                # Get ratio of this subreddit and times 1000 and convert to int.
                if int(float(detail['ratio']) * pow(10, DIGIT)) >= this_chance:
                    # If this one get chosen
                    try:
                        top_N_percent = round(
                            sampling_index * len(self.related_videos[subreddit_name]))
                        short.extend(
                            self.related_videos[subreddit_name][:top_N_percent])
                        subreddits_count += 1
                    except Exception as e:
                        print(e)
                        print(
                            "Check related video folder or above subreddit name to match each other.")
            if shuffle:
                random.shuffle(short)
            summary[profile_name] = len(short)
            summary[profile_name + '_subreddits_total'] = len(details)
            summary[profile_name + '_subreddits_chosen'] = subreddits_count
            name_related = 'related_videos_RNG_' + profile_name + '.json'
            self._write_json(short, os.path.join(out_path, name_related))
        self._write_json(summary, os.path.join(
            out_path, 'related_summary_RNG.json'))

    def one_click(self,
                  base=Settings.base,
                  diversity=Settings.by_diversity,
                  random=Settings.by_random_number_generator):
        if base:
            self.output_profiles_base(shuffle=Settings.base_shuffle,
                                      details=Settings.base_detailed,
                                      limit=Settings.base_video_number)
        if diversity:
            self.output_profiles_related_diversity_method(shuffle=Settings.extended_shuffle_by_diversity,
                                                          diversity_index=Settings.diversity_index)

        if random:
            self.output_profiles_related_RNG_method(shuffle=Settings.extended_shuffle_by_random_number,
                                                    sampling_index=Settings.sampling_percent_index)


if __name__ == '__main__':
    BP = Build_Profiles()
    BP.one_click()
