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
# FIXME Decide which of the backends should be imported when.
import csv
import datetime
import os.path
import pickle

from util import format_timedelta, group_by
from worktime import WorkSlot


# Public fields and methods.
__all__ = []

# Constants
FTYPE_CSV = 0
FTYPE_PICKLE = 1

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
        self.config['CFG_TASKS_FNAME'] = 'tasks.pkl'
        self.config['CFG_TASKS_FTYPE'] = FTYPE_PICKLE
        self.config['CFG_LOG_FNAME'] = 'timelog.pkl'
        self.config['CFG_LOG_FTYPE'] = FTYPE_PICKLE
        self.config['CFG_TIME_FORMAT'] = '%d %b %Y %H:%M:%S'
        # Initialise fields.
        self.projects = []
        # TODO Devise a more suitable data structure to keep tasks in
        # memory.
        self.tasks = []
        self.wtimes = []

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
            self.projects = sorted([proj.rstrip('\n') for proj in infile])

    def write_projects(self, outfname=None):
        """Writes the list of projects into a file.

        In the current implementation, simply writes out an alphabetically
        sorted list of all known projects to the file.

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
        elif inftype == FTYPE_PICKLE:
            if not os.path.exists(infname):
                open(infname, 'wb').close()
            with open(infname, 'rb') as infile:
                self.tasks = []
                while True:
                    try:
                        task = pickle.load(infile)
                        self.tasks.append(task)
                    except EOFError:
                        break
        else:
            raise NotImplementedError("Session.read_tasks() is not " + \
                                      "implemented for this type of files.")

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
        elif outftype == FTYPE_PICKLE:
            with open(outfname, 'wb') as outfile:
                for task in self.tasks:
                    pickle.dump(task, outfile)
        else:
            raise NotImplementedError("Session.write_tasks() is not " + \
                                      "implemented for this type of files.")

    def read_log(self, infname=None, inftype=None):
        """Reads the log of how time was spent."""
        # TODO: Think of when this really has to be done, and when only
        # a subset of the log needs to be read. In the latter case, allow for
        # doing so.
        if infname is None:
            infname = self.config['CFG_LOG_FNAME']
            inftype = self.config['CFG_LOG_FTYPE']
        if inftype == FTYPE_PICKLE:
            if not os.path.exists(infname):
                open(infname, 'wb').close()
            with open(infname, 'rb') as infile:
                self.wtimes = []
                while True:
                    try:
                        worktime = pickle.load(infile)
                        self.wtimes.append(worktime)
                    except EOFError:
                        break
        else:
            raise NotImplementedError("Session.read_log() is not " + \
                                      "implemented for this type of files.")

    def write_log(self, outfname=None, outftype=None):
        """TODO: Update docstring."""
        if outfname is None:
            outfname = self.config['CFG_LOG_FNAME']
            outftype = self.config['CFG_LOG_FTYPE']
        if outftype == FTYPE_PICKLE:
            with open(outfname, 'wb') as outfile:
                for wtime in self.wtimes:
                    pickle.dump(wtime, outfile)
        else:
            raise NotImplementedError("Session.write_log() is not " + \
                                      "implemented for this type of files.")

    def find_open_slots(self):
        """Returns work slots that are currently open."""
        return [slot for slot in self.wtimes if slot.end is None]


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
    arger_help.set_defaults(func=print_help)

    # begin
    arger_begin = subargers.add_parser('begin',
                                       aliases=['b'],
                                       help="To start working on a task.")
    arger_begin.set_defaults(func=begin)
    arger_begin.add_argument('-a', '--adjust',
                             default=0,
                             metavar='MIN',
                             help="Adjust the beginning time by " + \
                                  "subtracting this much.",
                             type=int)

    # end
    arger_end = subargers.add_parser(
        'end',
        aliases=['e'],
        help="When you have finished/interrupted work on a task.")
    arger_end.set_defaults(func=end)
    arger_end.add_argument('-a', '--adjust',
                           default=0,
                           metavar='MIN',
                           help="Adjust the end time by subtracting " + \
                                "this much.",
                           type=int)

    # retro (renamed from fence)
    arger_retro = subargers.add_parser('retro',
                                       help="Retrospective recording of work.")
    arger_retro.set_defaults(func=retro)

    # status (merged with state)
    arger_status = subargers.add_parser('status',
                                        help="Prints out the current status "\
                                             "info.")
    arger_status.set_defaults(func=status)

    # projects (renamed from topics)
    arger_projects = subargers.add_parser('projects',
                                          aliases=['p', 'proj'],
                                          help="Show info about projects.")
    arger_projects.set_defaults(func=projects)
    arger_projects.add_argument('-a', '--add', action='store_true',
                                help="Add a new project.")
    arger_projects.add_argument('-l', '--list', action='store_true',
                                help="List defined projects.")
    arger_projects.add_argument('-v', '--verbose', action='store_true',
                                help="Be verbose.")

    # tasks (instead of editing the tasks store directly)
    arger_tasks = subargers.add_parser('tasks',
                                       aliases=['t', 'tasks'],
                                       help="Show info about tasks.")
    arger_tasks.set_defaults(func=tasks)
    arger_tasks.add_argument('-a', '--add', action='store_true',
                             help="Add a new task.")
    arger_tasks.add_argument('-l', '--list', action='store_true',
                             help="List defined tasks.")
    arger_tasks.add_argument('-v', '--verbose', action='store_true',
                             help="Be verbose.")

    return arger


def _process_args(arger):
    """ Processes the command line arguments.
    """
    arger.parse_args(namespace=_cl_args)
    _cl_args.arger = arger


# Subcommand functions.
def print_help(args):
    args.arger.print_help()
    return 0


def begin(args):
    start = datetime.datetime.now() - datetime.timedelta(minutes=args.adjust)
    task = frontend.get_task(session)
    session.wtimes.append(WorkSlot(task=task, start=start))
    return 0


def end(args):
    end = datetime.datetime.now() - datetime.timedelta(minutes=args.adjust)
    open_slots = session.find_open_slots()
    if not open_slots:
        print("You have not told me you have been doing something. Use " + \
              "`begin' or `retro'.")
        return 1
    if len(open_slots) == 1:
        task = open_slots[0]
    else:
        task = frontend.get_task(session,
                                 map(lambda slot: slot.task, open_slots))
    session.wtimes.append(WorkSlot(task=task, end=end))
    return 0


def retro(args):
    raise NotImplementedError("The subcommand 'retro' is not implemented yet.")
    pass


def status(args):
    # Select work slots currently open.
    openslots = [slot for slot in session.wtimes if slot.iscurrent()]

    if not openslots:
        print("You don't seem to be working now.")
    else:
        print("You have been working on the following tasks:")
        now = datetime.datetime.now()
        task2slot = group_by(openslots, "task", single_attr=True)
        for task in task2slot:
            task_slots = task2slot[task]
            # Expected case: only working once on the task in parallel:
            if len(task_slots) == 1:
                time_spent = format_timedelta(now - task_slots[0].start)
                print("\t{time: >18}: {task}".format(task=task.name,
                                                     time=time_spent))
            else:
                for slot in task_slots:
                    time_spent = format_timedelta(now - slot.start)
                    print("M\t{time: >18}: {task}".format(task=task.name,
                                                          time=time_spent))
    return 0


def projects(args):
    was_output = False  # whether there has been any output from this function
                        # so far
    if args.list:
        frontend.list_projects(session, args.verbose)
        was_output = True
    if args.add:
        if was_output:
            print("")
        print("Adding a project...")
        print("Specify the project name: ")
        project = input("> ")
        while project in session.projects:
            print("Sorry, this project name is already used.  Try again: ")
            project = input("> ")
        session.projects.append(project)
        print("The project '{}' has been added successfully.".format(project))
    # if args.something_else:
    #     raise NotImplementedError("This action for the subcommand "\
    #                               "'projects' is not implemented yet.")
    return 0


def tasks(args):
    was_output = False  # whether there has been any output from this function
                        # so far
    if args.list:
        frontend.list_tasks(session, verbose=args.verbose)
        was_output = True
    if args.add:
        if was_output:
            print("")
        print("Adding a task...")
        task = frontend.get_task(session)
        session.tasks.append(task)
        print("The task '{}' has been added successfully.".format(task))
    return 0


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
    session.read_log()

    from frontend.cli import Cli as frontend
    # Perform commands.
    # FIXME: As seen, it does not work in a loop yet.
    ret = _cl_args.func(_cl_args)
    if ret == 0:
        print("Done.")

    # Write data on exit.
    session.write_log()
    session.write_tasks()
    session.write_projects()
