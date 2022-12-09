#!bin/usr/python

'''
captures 10 frames in different exposure times and saves them as follow:

utc_timestamp_exposuretime.npy

'''
import time
import datetime
import os
import time
import numpy as np
from datetime import timezone, timedelta, datetime
from time import sleep
from picamera2 import Picamera2

# https://stackoverflow.com/questions/41912594/how-to-speed-up-numpy-sum-and-python-for-loop
# operating directory for image saving
os.chdir("/home/pi/testenv/processing")

expos_ = []
images_ = []


def capture_multiple_exposures(picam2, exp_list, callback):
    def match_exp(metadata, indexed_list):
        err_factor = 0.00001
        err_exp_offset = 33
        exp = metadata["ExposureTime"]
        gain = metadata["AnalogueGain"]
        for want in indexed_list:
            want_exp, _ = want
            if abs(gain - 1.0) < err_factor and abs(exp - want_exp) < want_exp * err_factor + err_exp_offset:
                return want
        return None

    indexed_list = [(exp, i) for i, exp in enumerate(exp_list)]
    while indexed_list:
        request = picam2.capture_request()
        match = match_exp(request.get_metadata(), indexed_list)
        if match is not None:
            indexed_list.remove(match)
            exp, i = match
            callback(i, exp, request)
        if indexed_list:
            exp, _ = indexed_list[0]
            picam2.set_controls({"ExposureTime": exp, "AnalogueGain": 1.0, "ColourGains": (1.0, 1.0),
                                 "FrameDurationLimits": (25000, 50000)})
            indexed_list.append(indexed_list.pop(0))
        request.release()


def callback_func(i, wanted_exp, request):
    print(i, "wanted", wanted_exp, "got", request.get_metadata()["ExposureTime"])
    expos_.append((i, request.get_metadata()["ExposureTime"]))
    images_.append((i, request.make_array("raw")))



t1 = time.perf_counter()
def cap():

    with Picamera2() as picam2:
        config = picam2.create_preview_configuration(raw={"format": "SRGGB12", "size": (2032, 1520)},
                                                         buffer_count=3)

        picam2.configure(config)
        picam2.start()

        exposure_list = [60, 120, 180, 300, 480, 780, 1260, 2040, 3300]
        count = 1
        while count < 5:
            count = count + 1
            start = time.monotonic()
            images = images_
            expos = expos_  # real exposure times
            timestamp = int(datetime.now(timezone.utc).timestamp())
            

            capture_multiple_exposures(picam2, exposure_list, callback_func)
            images.sort(key=lambda tup: tup[0])
            expos.sort(key=lambda tup: tup[0])
            
            #finish = False
	
            for x in range(len(exposure_list)):
                y = np.array(images[x][1]).view(np.uint16)
                print(f"{y.shape} + max: + {np.max(y)}")
                xp = expos[x][1]
                np.save(f'{timestamp}_{xp}.npy', y, allow_pickle=True)
                
			
            del expos_[:]
            del images_[:]
            finish = True # series complete
            
		
            end = time.monotonic()
            print("Time:", end - start)

        picam2.stop()


cap()
t2 = time.perf_counter()
print(f"Finished in {t2 - t1} seconds")



