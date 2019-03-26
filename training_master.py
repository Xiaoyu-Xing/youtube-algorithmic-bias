import subprocess
import os
import sys
import Settings

def run_command(cmd):
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    return result.stdout.decode('utf-8'), result.stderr.decode('utf-8')


def main():
    names = [path.split('/')[-1].split('_')[-1].split('.json')[0] for path in Settings.training_list]
    scl = Settings.seed_cookies_list
    tcl = Settings.training_cookies_list
    tl = Settings.training_list
    abs_p = Settings.absolute_path_to_py
    log = Settings.log_root_path
    if len(scl) != len(tcl) or len(tcl) != len(tl):
        raise Exception('names list, cookies dimentions not match')
    for n, sc, tc, t in zip(names, scl, tcl, tl):
        cmd = f'nohup {sys.executable} {abs_p}training.py \
                --path {abs_p+t} --sc {abs_p+sc} --tc {abs_p+tc} > {abs_p+log+n}.out'
        run_command(cmd)


if __name__ == '__main__':
    if Settings.master_mode:
        main()
    else:
        raise Exception('Not in master training mode')