from os import walk
from os.path import join
from pathlib import Path
import random
import json
from pprint import pprint


class Build_Profiles:
    def __init__(self, input_path='data', output_path='output'):
        self.input_path = input_path
        self.output_path = output_path
        # Average profile details, keyed with last word of each json profile filename
        self.profiles = {}
        # Profile videos for each profile, keyed with filename of each json base-videos filename
        # Non-detailed version only contains urls in a List,
        # detailed version, keyed by the url, contains author, timestamp, score, and title.
        self.base_videos, self.base_videos_details, self.base_videos_summary = {}, {}, {}
        # *_dirs are the root directories path for files of profiles, base/related videos
        self.profiles_dir, self.videos_base_dir, self.videos_related_dir = '', '', ''
        # Names of files are stored separately, used together with dir path above
        self.profiles_files, self.videos_base_files, self.videos_related_files = [], [], []
        # Run to parse the input folder
        self._parse_folders()
        # Run to generate profile details
        self._generate_profiles()
        # Run to generate base profile videos
        self._build_profiles_base()

    # Parse data folder
    def _parse_folders(self):
        path = self.input_path
        for (cur_dirpath, sub_dirnames, cur_filenames) in walk(path):
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
            elif 'videos' in cur_dirpath and 'related' in cur_dirpath and 'json' in cur_dirpath:
                self.videos_related_dir = cur_dirpath
                self.videos_related_files = cur_filenames

    # Read json file
    def _read_json(self, path):
        with open(path) as f:
            jfile = json.load(f)
        return jfile, len(jfile), type(jfile)

    # Populate profile details
    def _generate_profiles(self):
        for profile in self.profiles_files:
            if 'ndjson' in profile:  # Skip ndjson
                continue
            # Use last word as key
            name = profile.strip('.json').split('_')[-1]
            profile_path = join(self.profiles_dir, profile)
            self.profiles[name] = self._read_json(profile_path)[0]

    # Collect all the videos from a json file
    def _load_videos(self, file):
        videos_short, videos_details = [], {}
        videos, length, _ = self._read_json(file)
        for video in videos:
            videos_short.append(video['url'])
            details = video.copy()
            del details['url']
            videos_details[video['url']] = details
        return videos_short, videos_details

    # Collect all the base videos for all profiles
    def _build_profiles_base(self):
        for file in self.videos_base_files:
            path = join(self.videos_base_dir, file)
            v, v_d = self._load_videos(path)
            key = file.strip('.json')
            self.base_videos[key] = v
            self.base_videos_details[key] = v_d
            self.base_videos_summary[key] = len(v)

    # Generate files based on the base output
    # Only output file will be shuffled is shuffle is True, the class attributes will not be shuffled,
    # to prevent uneven shuffle after sampled with extended videos
    def output_profiles_base(self, output=None, shuffle=False):
        out_path = output or self.output_path
        for file, videos in self.base_videos.items():
            name_base = 'base_videos_' + file + '.json'
            if shuffle:
                data = videos.copy()
                random.shuffle(data)
            with open(join(out_path, name_base), 'w') as f:
                # Indent will help json viewer properly display the format, same below
                json.dump(data, f, indent=4)
        for file, videos in self.base_videos_details.items():
            name_base_details = 'base_videos_details_' + file + '.json'
            videos = videos.items()
            # Unable to shuffle a dictionary
            if shuffle:
                data = list(videos)
                random.shuffle(data)
            with open(join(out_path, name_base_details), 'w') as f:
                # May because dictionary 'videos' is large, so the videos is type 'dict_values', json complains
                json.dump(dict(data), f, indent=4)
        with open(join(out_path, 'base_summary.json'), 'w') as f:
            json.dump(self.base_videos_summary, f, indent=4)

    def _build_profiles_extended(self):
        pass

    def output_profiles_extended(self):
        pass
