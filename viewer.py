from data import Data
import os
import time

input_path  = "C:\\Users\\Mikolaj\\Desktop\\Map.c2m"  # Change paths to whatever you want
output_path = "C:\\Users\\Mikolaj\\Desktop\\Map"
refresh_time = 0.5  # seconds

last_modified_time     = 0
last_modified_time_old = 0

while True:

    try:
        last_modified_time = os.path.getmtime(input_path)  # noqa

        if last_modified_time != last_modified_time_old:
            data = Data()
            data.load(input_path)
            data.extract(output_path)
    except FileNotFoundError:
        pass

    last_modified_time_old = last_modified_time
    time.sleep(refresh_time)
