import time
import sys

done = False

def animate():
    while not done:
        sys.stdout.write('\rProcessing |')
        time.sleep(0.1)
        sys.stdout.write('\rProcessing /')
        time.sleep(0.1)
        sys.stdout.write('\rProcessing -')
        time.sleep(0.1)
        sys.stdout.write('\rProcessing \\')
        time.sleep(0.1)
    sys.stdout.write('\rDone!     ')
