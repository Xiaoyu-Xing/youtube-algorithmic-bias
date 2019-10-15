import shutil
from datetime import datetime
import os
from typing import List, Dict

from deprecated import deprecated

import settings


@deprecated
class PilotTestingFilePipeline:
    @staticmethod
    def move_files_to_input_folder(index: int):
        generated_data_base_path: str = os.path.join(settings.ROOT_DIR, settings.GEN_DATA)
        dirs: List[str] = [dir_name for dir_name in os.listdir(generated_data_base_path)
                           if "test" in dir_name]
        sorted_dirs_dict: Dict[str, Dict[str, List]] = {"stateful": {}, "stateless": {}}
        for data_dir in dirs:
            collected_time = datetime.strptime(data_dir.split(" ", 1)[-1],
                                               settings.time_format_long)
            state: str = data_dir.split("-")[0]
            if "blank" not in data_dir:
                subreddit: str = data_dir.split("_", 2)[-1].split(" ")[0]
            else:
                subreddit: str = "blank"
            if subreddit not in sorted_dirs_dict[state]:
                sorted_dirs_dict[state][subreddit] = []
            sorted_dirs_dict[state][subreddit].append((collected_time, data_dir))
        for state_dirs_dict in sorted_dirs_dict.values():
            for subreddit_dirs in state_dirs_dict.values():
                subreddit_dirs.sort(key=lambda x: x[0])
        print(sorted_dirs_dict)
        input_data_dir: str = os.path.join(settings.ROOT_DIR,
                                           settings.INPUT_DATA, "pilot_test_result")
        for state, state_dirs_dict in sorted_dirs_dict.items():
            for subreddit, subreddit_dirs in state_dirs_dict.items():
                source_dir: str = os.path.join(generated_data_base_path, subreddit_dirs[index][1])
                destination_dir: str = os.path.join(input_data_dir, subreddit, state)
                for file in os.listdir(source_dir):
                    if "query" in file:
                        shutil.copy(os.path.join(source_dir, file),
                                    os.path.join(destination_dir, "query_result.json"))
                    elif "recommendation" in file:
                        shutil.copy(os.path.join(source_dir, file),
                                    os.path.join(destination_dir, "recommendation.json"))
        return


if __name__ == '__main__':
    PilotTestingFilePipeline.move_files_to_input_folder(-1)

