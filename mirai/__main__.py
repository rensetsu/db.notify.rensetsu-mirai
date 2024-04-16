from sys import exit as sysexit
from time import time

from librensetsu import convert_float_to_time

from consts import pprint, Status
from loops import do_loop
from download import download_database
import traceback

def main() -> None:
    """Main process of the util"""
    start = time()
    try:
        if not download_database():
            raise Exception("Failed to download database")
        do_loop()
        end = time()
        pprint.print(Status.INFO, f'Time elapsed: {convert_float_to_time(end - start)}')
        sysexit(0)
    except Exception as e:
        pprint.print(Status.ERR, f'An error occurred: {e}')
        traceback.print_exc()
        end = time()
        pprint.print(Status.INFO, f'Time elapsed: {convert_float_to_time(end - start)}')
        sysexit(1)

if __name__ == '__main__':
    main()
