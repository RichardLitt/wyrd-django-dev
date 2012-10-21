#!/usr/bin/python3
#-*- coding: utf-8 -*-
# This code is PEP8-compliant. See http://www.python.org/dev/peps/pep-0008/.
"""

Wyrd In: Time tracker and task manager
CC-Share Alike 2012 © The Wyrd In team
https://github.com/WyrdIn

"""

import os.path


# Variables.
cl_args = dict()    # dictionary for command line argument values
config = dict()    # dictionary for configuration settings


def _process_args():
    """ Processes the command line arguments.
    """
    global cl_args  # the variable where the argument values shall be stored
    # TODO Implement.
    # Use argparse.
    pass


def _set_default_config():
    """ Sets configuration defaults without looking into any user-supplied
    files.
    """
    global config
    config[CFG_TASKS_FNAME] = 'tasks.csv'


def _read_config():
    """ Finds all relevant configuration files, reads them and acts
    accordingly.
    """
    global config   # configuration parameters will be stored here
    set_default_config()
    # Find config files.
    # TODO Extend. Include more options where configuration files can be put
    # (some user-specific, some global ones, perhaps some site-specific). Look
    # also in the command line arguments (cl_args).
    cfg_fname = "wyrdin.cfg"
    if os.path.exists(cfg_fname):
        with open(cfg_fname, encoding="UTF-8") as cfg_file:
            for line in cfg_file:
                # TODO Extend. This assumes
                cfg_key, cfg_value = map(str.strip,
                                         line.strip().split('=', 2))
                # TODO Extend. There can be more various actions to be done
                # when a value is set in the config file.
                config[cfg_key] = cfg_value


if __name__ == "__main__":
    _process_args()
    _set_default_config()
    _read_config()
