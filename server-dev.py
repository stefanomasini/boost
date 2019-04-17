import os
import sys


class CONFIG(object):
    server_port = 4000


if __name__ == '__main__':
    src_dirpath = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'src')
    sys.path.append(src_dirpath)
    from boost.main import run_application
    run_application(CONFIG)
