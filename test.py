# from selenium import webdriver
# from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
# import time
# import Settings


# binary = FirefoxBinary(Settings.firefox_binary_path)
# fp = webdriver.FirefoxProfile()
# fp.add_extension(Settings.ad_block_path)

# browser = webdriver.Firefox(firefox_profile=fp, firefox_binary=binary)

# browser.get('https://www.youtube.com/watch?v=4_7bPNQxp1o')
# time.sleep(15)

# browser.close()


import subprocess
import os
import sys
import Settings
import time
from concurrent.futures import ProcessPoolExecutor as Pool


def run_command(cmd):
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    return result.stdout.decode('utf-8'), result.stderr.decode('utf-8')


def main():
    s = time.time()
    for i in range(5):
        cmd = f'{sys.executable} /home/xx/code/youtube-algorithmic-bias/test2.py > /home/xx/code/youtube-algorithmic-bias/log/{str(time.time())}.log'
        run_command(cmd)
    e = time.time()
    print(e - s)
    print("done")


def mp_main():
    s = time.time()
    cmds = [f'{sys.executable} /home/xx/code/youtube-algorithmic-bias/test2.py > /home/xx/code/youtube-algorithmic-bias/log/{str(time.time())}.log' for i in range(5)]
    with Pool(max_workers=12) as pool:
        pool.map(run_command, cmds)
    e = time.time()
    print(e - s)
    print('mp done')
    

if __name__ == '__main__':
    mp_main()