import time


def dummy_function():
    count = 0

    while(True):
        count = count+1
        print("Test Count", count)
        time.sleep(1)

