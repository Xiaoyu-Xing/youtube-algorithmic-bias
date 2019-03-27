import subprocess
import time
import os
import sys
import Settings
from concurrent.futures import ProcessPoolExecutor as Pool
import datetime

def run_command(cmd):
    # Shell need to set to true
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    return result.stdout.decode('utf-8'), result.stderr.decode('utf-8')


def main():
    # Name list extracted from path, to name log file
    names = [path.split('/')[-1].split('_')[-1].split('.json')[0] for path in Settings.training_list]
    # Seed cookies, list of path
    scl = Settings.seed_cookies_list
    # After training cookies, list of path
    tcl = Settings.training_cookies_list
    # Video for training json files, list of path
    tl = Settings.training_list
    # Useful in virtual environment to run through specific interpreter
    # abs_p = os.getcwd()
    log = Settings.log_root_path
    # For current project, assume each training list corrsponds to one cookie/profile
    if len(scl) != len(tcl) or len(tcl) != len(tl):
        raise Exception('names list, cookies dimentions not match')
    cmds = []
    today = str(datetime.datetime.now().strftime('%Y-%b-%d-%H-%M'))
    log_path = os.path.join(Settings.log_root_path + '-log', today)
    if not os.path.exists(log_path):
        os.makedirs(log_path)
    for n, sc, tc, t in zip(names, scl, tcl, tl):
        cmd = f'nohup {sys.executable} training.py ' + \
                f'--path {t} ' + \
                f'--sc {sc} ' + \
                f'--tc {tc} ' + \
                f'> {os.path.join(log_path, n)}.log &'
        print(f'Command for {n}: {cmd}')
        cmds.append(cmd)
    print(f'\nMaster training starts, current time: {time.ctime()}')
    with Pool(max_workers=len(cmds)) as pool:
        pool.map(run_command, cmds)
    print(f'\nMaster training ends, current time: {time.ctime()}')



if __name__ == '__main__':
    if Settings.master_mode:
        main()
    else:
        raise Exception('Not in master training mode')