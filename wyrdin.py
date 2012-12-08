#!/usr/bin/python3
#-*- coding: utf-8 -*-
# This code is PEP8-compliant. See http://www.python.org/dev/peps/pep-0008/.
"""

Wyrd In: Time tracker and task manager
CC-Share Alike 2012 © The Wyrd In team
https://github.com/WyrdIn

"""

# TODO: today (list of all tasks/projects/workslots)

import argparse
import datetime
import os.path
import pickle

from util import format_timedelta, group_by
from worktime import WorkSlot, parse_interval


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
            import csv
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
            import csv
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

    def remove_project(self, project):
        tasks = filter(lambda task: task.project == project, self.tasks)
        for task in tasks:
            self.remove_task(task)
        self.projects.remove(project)

    def remove_task(self, task):
        slots = filter(lambda slot: slot.task == task, self.wtimes)
        for slot in slots:
            self.remove_workslot(slot)
        self.tasks.remove(task)

    def remove_workslot(self, slot):
        self.wtimes.remove(slot)


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
    arger_status.add_argument('-t', '--time',
                              type=parse_interval,
                              action='append',
                              help="Filter work slots by time.")
    arger_status.add_argument('-a', '--all',
                              action='store_true',
                              help="Include also closed slots.")

    # projects (renamed from topics)
    arger_projects = subargers.add_parser('projects',
                                          aliases=['p', 'proj'],
                                          help="Show info about projects.")
    arger_projects.set_defaults(func=projects)
    arger_projects.add_argument('-a', '--add',
                                dest='subcmd',
                                action='store_const',
                                const='add',
                                help="Add a new project.")
    arger_projects.add_argument('-l', '--list',
                                dest='subcmd',
                                action='store_const',
                                const='list',
                                help="List defined projects.")
    arger_projects.add_argument('-r', '--remove',
                                dest='subcmd',
                                action='store_const',
                                const='remove',
                                help="Remove an existing project.")
    arger_projects.add_argument('-v', '--verbose', action='store_true',
                                help="Be verbose.")

    # tasks (instead of editing the tasks store directly)
    arger_tasks = subargers.add_parser('tasks',
                                       aliases=['t', 'tasks'],
                                       help="Show info about tasks.")
    arger_tasks.set_defaults(func=tasks)
    arger_tasks.add_argument('-a', '--add',
                             dest='subcmd',
                             action='store_const',
                             const='add',
                             help="Add a new task.")
    arger_tasks.add_argument('-r', '--remove',
                             dest='subcmd',
                             action='store_const',
                             const='remove',
                             help="Remove an existing task.")
    arger_tasks.add_argument('-l', '--list',
                             dest='subcmd',
                             action='store_const',
                             const='list',
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
    task = frontend.get_task(session)
    start = datetime.datetime.now() - datetime.timedelta(minutes=args.adjust)
    session.wtimes.append(WorkSlot(task=task, start=start))
    return 0


def end(args):
    now = datetime.datetime.now() - datetime.timedelta(minutes=args.adjust)
    open_slots = session.find_open_slots()
    if not open_slots:
        print("You have not told me you have been doing something. Use " + \
              "`begin' or `retro'.")
        return 1
    # If currently working on a single task (once at a time), assume it is that
    # one to be ended.
    if len(open_slots) == 1:
        task = open_slots[0]
    # If more tasks are currently open, let the user specify which one is to be
    # ended.
    else:
        task = frontend.get_task(session,
                                 map(lambda slot: slot.task, open_slots))
    for slot in filter(lambda slot: slot.task == task, open_slots):
        slot.end = now
    return 0


def retro(args):
    raise NotImplementedError("The subcommand 'retro' is not implemented yet.")
    pass


def status(args):
    # Transform selection criteria into test functions.
    if args.time:
        filter_time = lambda slot: \
            all(filter(lambda invl: slot.intersects(invl), args.time))
    else:
        filter_time = True
    if not args.all:
        filter_open = lambda slot: slot.iscurrent()
    else:
        filter_open = True
    # Select work slots matching the selection criteria..
    slots = [slot for slot in session.wtimes \
             if filter_time(slot) and filter_open(slot)]

    if not slots:
        # FIXME Update the message.
        print("You don't seem to be working now.")
    else:
        # FIXME Update the message.
        print("You have been working on the following tasks:")
        now = datetime.datetime.now()
        task2slot = group_by(slots, "task", single_attr=True)
        for task in task2slot:
            task_slots = task2slot[task]
            # Expected case: only working once on the task in parallel:
            if len(task_slots) == 1:
                end = task_slots[0].end or now
                time_spent = format_timedelta(end - task_slots[0].start)
                print("\t{time: >18}: {task}".format(task=task.name,
                                                     time=time_spent))
            else:
                for slot in task_slots:
                    end = slot.end or now
                    time_spent = format_timedelta(end - slot.start)
                    print("M\t{time: >18}: {task}".format(task=task.name,
                                                          time=time_spent))
    return 0


def projects(args):

    # Define subcommand functions.
    def list():
        frontend.list_projects(session, args.verbose)

    def add():
        print("Adding a project...")
        print("Specify the project name: ")
        project = input("> ")
        while project in session.projects:
            print("Sorry, this project name is already used.  Try again: ")
            project = input("> ")
        session.projects.append(project)
        print("The project '{}' has been added successfully.".format(project))

    def remove():
        print("Removing a project...")
        project = frontend.get_project(session, accept_empty=False)
        # Remove the project.
        session.remove_project(project)
        print(("The project '{}' and all dependent tasks have been " + \
              "successfully removed.")\
              .format(project))

    try:
        # Call the subcommand function.
        locals()[args.subcmd]()
    except KeyError:
        raise NotImplementedError(
            'The subcommand `{sub!s}\' is not implemented.'\
            .format(sub=args.subcmd))
    return 0


def tasks(args):

    # Define subcommand functions.
    def list():
        frontend.list_tasks(session, verbose=args.verbose)

    def add():
        print("Adding a task...")
        task = frontend.get_task(session)
        session.tasks.append(task)
        print("The task '{}' has been added successfully.".format(task))

    def remove():
        print("Removing a task...")
        task = frontend.get_task(session, session.tasks)
        session.remove_task(task)
        print("The task '{}' has been removed successfully.".format(task))

    try:
        # Call the subcommand function.
        locals()[args.subcmd]()
    except KeyError:
        raise NotImplementedError(
            'The subcommand `{sub!s}\' is not implemented.'\
            .format(sub=args.subcmd))
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
