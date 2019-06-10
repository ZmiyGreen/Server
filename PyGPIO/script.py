import random
import sys
import os
import argparse
import datetime

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--filename', type=str, default=f"file-{datetime.datetime.now()}")
    parser.add_argument('-c', '--count', type=int, default=5)
    arg = parser.parse_args(sys.argv[1:])
    if len(sys.argv) != 2 or int(sys.argv[2]) <= 0:
        raise ValueError("Invalid arguments!")
    else:
        with open(f"{os.getcwd()}/{arg.filename}", 'w') as wr:
            for i in arg.count:
                wr.write(str(random.randint(0, 9)))
