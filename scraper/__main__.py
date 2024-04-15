from sys import exit as sysexit
from time import time

from consts import pprint, Status
from loops import do_loop

def main() -> None:
    """Main process of the util"""
    try:
        do_loop()
        sysexit(0)
    except Exception as e:
        pprint.print(Status.ERR, f'An error occurred: {e}')
        end = time()
        pprint.print(Status.INFO, f'Time elapsed: {convert_float_to_time(end - start)}')
        sysexit(1)

if __name__ == '__main__':
    main()
