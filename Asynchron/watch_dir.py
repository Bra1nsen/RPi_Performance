
# !/usr/bin/python3      #https://www.the-analytics.club/python-monitor-file-changes
# https://thepythoncorner.com/posts/2019-01-13-how-to-create-a-watchdog-in-python-to-look-for-filesystem-changes/

'''
checks directory where images/numpy arrays are saved
0. recognize timeseries (9frames same utc timestamp)
1. preprocesses them
2. upload2cloud (skydrive)
'''

import datetime
import os
import sys
import glob
import multiprocessing
import time
import shutil
import numpy as np
from subprocess import call
from datetime import timezone, timedelta, datetime
from multiprocessing import Process
from time import sleep
from watchdog.observers import Observer  # https://pypi.org/project/watchdog/
from watchdog.events import FileSystemEventHandler

# from cfet import communication


SS = datetime.now(timezone.utc).second
MM = datetime.now(timezone.utc).minute
HH = datetime.now(timezone.utc).hour
DD = datetime.now(timezone.utc).day
MM = datetime.now(timezone.utc).month
YYYY = datetime.now(timezone.utc).year

YYYYs = str(YYYY)
MMs = str(MM)
DDs = str(DD)

os.chdir("/home/pi/testenv/processing")

list = []  # npz
list_exp = []  # npy's

img_index_list = [0, 1, 2, 3, 4, 5, 6, 7, 8]  # 9 frames
expo_r = ["60", "106", "166", "273", "470", "773", "1258", "2032", "3291"]  # 9 exposure times
expos = [60, 106, 166, 273, 470, 773, 1258, 2032, 3291]
dic = dict(zip(expo_r, img_index_list))


# {60: 0, 106: 1, 166: 2, 273: 3, 470: 4, 773: 5, 1258: 6, 2032: 7, 3291: 8}

# target_arr = np.zeros((1520,2032,9), dtype="uint16")

class EventHandler(FileSystemEventHandler):

    # after one images arrive: functions runs once
    def on_created(self, event):
        os.chdir("/home/pi/testenv/processing/")
        img_id = os.path.basename(event.src_path)
        img_utc = os.path.basename(event.src_path).split('_')[0]
        img_utc_exp = os.path.basename(event.src_path).split('.')[0]
        img_exp = img_utc_exp.split('_')[1]
        index = dic[str(img_exp)]
        print(f"captured: {img_id}")
        try:
            temp = np.load(f"{img_id}", allow_pickle=True)  # type(temp) = narray
        except:
            print("file did not load completely - trying again#1")
            try:
                time.sleep(0.1)
                temp = np.load(f"{img_id}", allow_pickle=True)  # type(temp) = narray
            except:
                print("file did not load completely - trying again#2")
                try:
                    time.sleep(0.5)
                    temp = np.load(f"{img_id}", allow_pickle=True)  # type(temp) = narray
                except:
                    print("file did not load completely - trying again#3")
                    try:
                        time.sleep(0.5)
                        temp = np.load(f"{img_id}", allow_pickle=True)  # type(temp) = narray
                    except:
                        print("file did not load completely - trying again#4")
                        try:
                            time.sleep(0.5)
                            temp = np.load(f"{img_id}", allow_pickle=True)  # type(temp) = narray
                        except:
                            print("file did not load completely - trying again#5")
                            try:
                                time.sleep(1.5)
                                temp = np.load(f"{img_id}", allow_pickle=True)  # type(temp) = narray
                            except:
                                print("file did not load completely - trying again#6")
                                try:
                                    time.sleep(3.5)
                                    temp = np.load(f"{img_id}", allow_pickle=True)  # type(temp) = narray
                                except:
                                    print("FAIL")

        list.insert(index, temp)

        print(f"img_id: {img_id}")

        if len(list) == 9:
            print("9 from 9 frames captured - timeseries complete")

            def appe(timestamp):

                filenames = list
                print(f"type: {type(filenames[0])} and shape: {filenames[0].shape}")
                os.chdir("/home/pi/testenv/fuse")
                np.savez(f"{timestamp}.npz", filenames[0], filenames[1], filenames[2], filenames[3], filenames[4],
                         filenames[5],
                         filenames[6], filenames[7], filenames[8])

                shutil.move(f"/home/pi/testenv/fuse/{timestamp}.npz",
                            f"/home/pi/mnt/skydrive/DATASETS/TUDD/original/npz/{YYYYs}/{MMs}/{DDs}/{timestamp}.npz")

            def append(timestamp):

                filenames = list
                combine = np.array(filenames, dtype=np.uint16)
                print(f"combine: {combine.shape}")
                os.chdir("/home/pi/testenv/fuse")
                np.save(f"{timestamp}_1520_2032_9.npy", combine)
                print("saved as timeseries in shape (1520,2032,9).npy")

                summed_new = np.sum(combine, axis=0, dtype="uint16")

                np.save(f"{timestamp}_sum_1520_2032_1.npy", summed_new)
                print("saved images summed in shape 1520,2032,1 with hdr [0-255]x9")

                shutil.move(f"/home/pi/testenv/fuse/{timestamp}_1520_2032_9.npy",
                            f"/home/pi/mnt/skydrive/DATASETS/TUDD/original/1520_2032_9_npy/{YYYYs}/{MMs}/{DDs}/{timestamp}_1520_2032_9.npy")
                shutil.move(f"/home/pi/testenv/fuse/{timestamp}_sum_1520_2032_1.npy",
                            f"/home/pi/mnt/skydrive/DATASETS/TUDD/original/sum_npy/{YYYYs}/{MMs}/{DDs}/{timestamp}_sum_1520_2032_1.npy")

                print(f"uploaded combined to google skydrive: {timestamp}_1520_2032_9.npy")
                print(f"uploaded summed to google skydrive: {timestamp}_sum_1520_2032_1.npy")


            a = multiprocessing.Process(target=appe, args=[img_utc])
            b = multiprocessing.Process(target=append, args=[img_utc])

            a.start()
            b.start()
            a.join()
            b.join()
            del list[:]
            print(f"after del list: len(list) = {len(list)}")
            print("READY FOR NEW TIMESERIES")



        else:
            print(f"{len(list)} from 9 frames captured")


# new_image = img[:, :, 0]*0.299 + img[:, :, 1]*0.587 + img[:, :, 2]*0.114

while True:

    path = "/home/pi/testenv/processing"  # make sure folder is empty when starting script

    event_handler = EventHandler()
    observer = Observer()
    observer.schedule(event_handler, ".", recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        my_observer.stop()
        my_observer.join()


