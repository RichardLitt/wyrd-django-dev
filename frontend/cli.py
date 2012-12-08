#!/usr/bin/python3
#-*- coding: utf-8 -*-
# This code is PEP8-compliant. See http://www.python.org/dev/peps/pep-0008/.
"""

Wyrd In: Time tracker and task manager
CC-Share Alike 2012 © The Wyrd In team
https://github.com/WyrdIn

"""
from collections import Mapping

from worktime import parse_delta, parse_datetime
from task import Task


# TODO: Inherit from IFrontend (to be implemented).
class Cli(object):
    """ Basic command-line user interface. """

    @staticmethod
    def get_task(session, selection=None):
        """ Asks the user for a task from a given selection or a new one.

        Keyword arguments:
        session -- the user session object
        selection -- a selection of tasks to choose from (default: anything)

        """
        # Check that the selection is satisfiable.
        if selection is not None and not selection:
            raise ValueError("Cannot ask for a task from an empty selection.")

        task = None
        print("What is the task? ")
        if selection is not None:
            restricted = True
        else:
            selection = session.tasks
            restricted = False

        str2task = dict()
        int2task = dict()
        for task_index, a_task in enumerate(selection):
            # FIXME Distinguish between different tasks with the same string
            # representation.
            task_str = str(a_task)
            str2task[task_str] = a_task
            int2task[str(task_index)] = a_task
        if restricted:
            Cli.choosefrom(int2task)

        shown_selection = False
        taskname = input("> ")
        while not taskname or taskname == "?":
            if restricted:
                Cli.choosefrom(int2task)
            else:
                if selection:
                    shown_selection = True
                    Cli.choosefrom(int2task,
                                   msg="You can choose from the " + \
                                       "existing tasks:")
                else:
                    print("There are currently no tasks defined.")
            taskname = input("> ")
        # Should the task be one of existing Task tasks,
        if restricted:
            # Find the Task task.
            while taskname not in str2task and taskname not in int2task:
                if not taskname or taskname == "?":
                    Cli.choosefrom(int2task)
                else:
                    print("Sorry, this task was not on the menu. Try again.")
                taskname = input("> ")
            if taskname in int2task:
                task = int2task[taskname]
            else:
                task = str2task[taskname]
        # If we are asking for a new task,
        else:
            if shown_selection:
                if taskname in int2task:
                    task = int2task[taskname]
                elif taskname in str2task:
                    task = str2task[taskname]
            if task is None:
                # Create a new task, asking for optional details.
                project = Cli.get_project(session)
                print("Estimated time?")
                time = input("> ").strip()
                print("Deadline?")
                deadline = input("> ").strip()
                task = Task(taskname, project)
                if time:
                    task.time = parse_delta(time)
                if deadline:
                    task.deadline = parse_datetime(deadline)
        return task

    @staticmethod
    def choosefrom(selection, msg="Choose from the following list:"):
        print(msg)
        # Find what indexing to use for the selection.
        numbered_map = None
        if isinstance(selection, Mapping):
            try:
                sorted_keys = sorted(selection, key=int)
            except ValueError:
                try:
                    sorted_keys = sorted(selection)
                except KeyError:
                    numbered_map = selection
        else:
            numbered_map = enumerate(selection)
        if numbered_map is None:
            numbered_map = ((key, selection[key]) for key in sorted_keys)
        # Print the selection.
        for index, item in numbered_map:
            print ("    {idx: >4} {item!s}".format(idx=index, item=item))
        print("")

    @staticmethod
    def get_project(session):
        """Solicits a project name from the user.

        An empty project is accepted too.

        """
        # TODO: Here should be some form of tab-completion.
        print("What project does it belong to?")
        project = input("> ").strip()
        while project and project not in session.projects:
            if project != "?":
                print("You have not told me about this project yet.")
            Cli.choosefrom(session.projects,
                           msg="You can choose from the existing " + \
                               "projects.\n" + \
                               "You can also use an empty string, meaning " + \
                               "no project.")
            # Cli.list_projects(session)
            project = input("> ").strip()
            # Try to interpret the input as a project index into the selection
            # list.
            try:
                proj_idx = int(project)
                try:
                    return session.projects[proj_idx]
                except IndexError:
                    pass
            except ValueError:
                pass
            # If it wasn't a project index that the user supplied, take it as
            # a string (i.e., do nothing).
        return project

    @staticmethod
    def list_projects(session, verbose=False):
        # TODO Implement verbosity.
        print("List of current projects:")
        for project in sorted(session.projects):
            print("    {}".format(project))
        print("")

    @staticmethod
    def list_tasks(session, verbose=False):
        # TODO Say when the tasks were worked on.
        print("List of current tasks:")
        if verbose:
            for task in sorted(session.tasks):
                print("    {}".format(task.name))
                for attr in task.__dict__:
                    print("      {attr: >10}: {val!s}".format(
                        attr=attr, val=task.__dict__[attr]))
                print("")
        else:
            for task in sorted(session.tasks):
                print("    {}".format(task))
        print("")
