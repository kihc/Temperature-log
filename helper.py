__author__ = 'Miha'

import os


def is_debug():






    if os.environ['SERVER_SOFTWARE'].find('Development') > -1:
        return True
    else:
        return False