import os
import random
import json
from pprint import pprint


class Build_Profiles:
    # Specify data location, and output location.
    def __init__(self, input_path='data', output_path='output'):
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
    def _build_profiles_base(self, limit):
        '''
        Input:
            limit: int, how many top videos to choose
        '''
        for file in self.videos_base_files:
            path = os.path.join(self.videos_base_dir, file)
            v, v_d = self._load_videos(path)
            key = os.path.splitext(file)[0]
            self.base_videos[key] = v[:limit]
            self.base_videos_details[key] = v_d[:limit]
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
    def output_profiles_base(self, shuffle=False, details=True, limit=50):
        '''
        Input:
            shuffle: boolean, whether to shuffle the ourput
            details: boolean, whether to output detailed version
            limit: int, how many to output
        '''
        # Run to generate base profile videos
        self._build_profiles_base(limit)
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

    def _build_profiles_related(self, limit):
        for file in self.videos_related_files:
            key = os.path.splitext(file)[0]
            path = os.path.join(self.videos_related_dir, file)
            v, v_d = self._load_related_videos(path)
            self.related_videos[key] = v[:limit]
            self.related_videos_details[key] = v_d[:limit]
            self.related_videos_summary[key] = len(self.related_videos[key])

    def output_profiles_related(self, shuffle=False, details=True, limit=50):
        self._build_profiles_related(limit)
        pass
