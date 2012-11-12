#!/usr/bin/python3
#-*- coding: utf-8 -*-
# This code is PEP8-compliant. See http://www.python.org/dev/peps/pep-0008/.
"""

Wyrd In: Time tracker and task manager
CC-Share Alike 2012 © The Wyrd In team
https://github.com/WyrdIn

"""

import argparse
# from .backend import csv as backend
import csv
import os.path

# Public fields and methods.
__all__ = []

# Constants
FTYPE_CSV = 0

# Variables
session = None


class ClArgs():
    """Class to hold command line attributes."""
    pass

_cl_args = ClArgs()


class Session(object):
    """
    Represents a user session, gathering such information as current
    configuration or the user's set of tasks.

    """
    def __init__(self):
        # Set the default configuration.
        self.config = dict()
        self.config['CFG_PROJECTS_FNAME'] = 'projects.lst'
        self.config['CFG_TASKS_FNAME'] = 'tasks.csv'
        self.config['CFG_TASKS_FTYPE'] = FTYPE_CSV
        # Initialise fields.
        # TODO Devise a more suitable data structure to keep tasks in
        # memory.
        # FIXME: Currently, tasks are just lists of values. They should be
        # task.Task instead.
        self.tasks = []

    def read_config(self, cl_args):
        """ Finds all relevant configuration files, reads them and acts
        accordingly.
        """
        # Find config files.
        # TODO Extend. Include more options where configuration files can be
        # put (some user-specific, some global ones, perhaps some
        # site-specific). Look also in the command line arguments (_cl_args).
        cfg_fname = "wyrdin.cfg"
        if os.path.exists(cfg_fname):
            with open(cfg_fname, encoding="UTF-8") as cfg_file:
                for line in cfg_file:
                    # TODO Extend. This assumes
                    cfg_key, cfg_value = map(str.strip,
                                             line.strip().split('=', 2))
                    # TODO Extend. There can be more various actions to be done
                    # when a value is set in the config file.
                    self.config[cfg_key] = cfg_value

    def read_projects(self, infname=None):
        """
        TODO: Write docstring.
        """
        if infname is None:
            infname = self.config['CFG_PROJECTS_FNAME']
        with open(infname) as infile:
            self.projects = sorted([proj.rstrip('\n\r') for proj in infile])

    def write_projects(self, outfname=None):
        """
        TODO: Write docstring.
        """
        if outfname is None:
            outfname = self.config['CFG_PROJECTS_FNAME']
        with open(outfname, 'w') as outfile:
            for project in self.projects:
                outfile.write(project + '\n')

    def read_tasks(self, infname=None, inftype=None):
        """
        Reads in tasks from files listing the user's tasks. Which files these
        are, can be found in `self.config'.

        TODO: Update docstring.

        """
        if infname is None:
            infname = self.config['CFG_TASKS_FNAME']
            inftype = self.config['CFG_TASKS_FTYPE']
        # This is a primitive implementation for the backend as a CSV.
        if inftype == FTYPE_CSV:
            # Read the tasks from the file to the memory.
            with open(infname, newline='') as infile:
                taskreader = csv.reader(infile)
                self.tasks = [task for task in taskreader]
        else:
            raise NotImplementedError("Session.read_tasks() is implemented "\
                                      "only for CSV files.")

    def write_tasks(self, outfname=None, outftype=None):
        """
        Writes out the current list of tasks from memory to a file.

        TODO: Update docstring.

        """
        if outfname is None:
            outfname = self.config['CFG_TASKS_FNAME']
            outftype = self.config['CFG_TASKS_FTYPE']
        if outftype == FTYPE_CSV:
            with open(outfname, newline='') as outfile:
                taskwriter = csv.writer(outfile)
                for task in self.tasks:
                    taskwriter.writerow(task)
        else:
            raise NotImplementedError("Session.write_tasks() is implemented "\
                                      "only for CSV files.")


def _init_argparser(arger):
    """
    Initialises the argument parser.
    """
    # Create a pool of subcommands.
    subargers = arger.add_subparsers()
    # Subcommands:
    #-------------

    # help
    arger_help = subargers.add_parser('help', help="Prints out this message.")
    arger_help.set_defaults(func=_print_help)

    # begin
    arger_begin = subargers.add_parser('begin',
                                       help="To start working on a task.")
    arger_begin.set_defaults(func=_begin)

    # end
    arger_end = subargers.add_parser(
        'end',
        help="When you have finished/interrupted work on a task.")
    arger_end.set_defaults(func=_end)

    # retro (renamed from fence)
    arger_retro = subargers.add_parser('retro',
                                       help="Retrospective recording of work.")
    arger_retro.set_defaults(func=_retro)

    # status (merged with state)
    arger_status = subargers.add_parser('status',
                                        help="Prints out the current status "\
                                             "info.")
    arger_status.set_defaults(func=_status)

    # projects (renamed from topics)
    arger_projects = subargers.add_parser('projects',
                                          aliases=['p', 'proj'],
                                          help="Show info about projects.")
    arger_projects.set_defaults(func=_projects)
    arger_projects.add_argument('-a', '--add', action='store_true',
                                help="Add a new project.")
    arger_projects.add_argument('-l', '--list', action='store_true',
                                help="List defined projects.")
    return arger


def _process_args(arger):
    """ Processes the command line arguments.
    """
    arger.parse_args(namespace=_cl_args)
    _cl_args.arger = arger


# Subcommand functions.
def _print_help(args):
    args.arger.print_help()


def _begin(args):
    raise NotImplementedError("The subcommand 'begin' is not implemented yet.")
    pass


def _end(args):
    raise NotImplementedError("The subcommand 'end' is not implemented yet.")
    pass


def _retro(args):
    raise NotImplementedError("The subcommand 'retro' is not implemented yet.")
    pass


def _status(args):
    raise NotImplementedError("The subcommand 'status' is not implemented "\
                              "yet.")
    pass


def _projects(args):
    was_output = False  # whether there has been any output from this function
                        # so far
    if args.list:
        print("List of current projects:")
        for project in sorted(session.projects):
            print("    {}".format(project))
        print(" --- end of list --- ")
        was_output = True
    if args.add:
        if was_output:
            print("")
        print("Adding a project...")
        project = input("Specify the project name: ")
        while project in session.projects:
            project = input("Sorry, this project name is already used. "\
                            "Try again: ")
        session.projects.append(project)
        print("The project '{}' has been added successfully.".format(project))
#     if args.something_else:
#         raise NotImplementedError("This action for the subcommand "\
#                                   "'projects' is not implemented yet.")


# The main program loop.
if __name__ == "__main__":
    # Read arguments and configuration.
    arger = argparse.ArgumentParser()
    _init_argparser(arger)
    _process_args(arger)
    session = Session()
    session.read_config(_cl_args)

    # Read data.
    session.read_projects()
    session.read_tasks()

    # Perform commands.
    # FIXME: As seen, it does not work in a loop yet.
    _cl_args.func(_cl_args)

    # Write data on exit.
    session.write_tasks()
    session.write_projects()
