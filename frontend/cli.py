#!/usr/bin/python3
#-*- coding: utf-8 -*-
# This code is PEP8-compliant. See http://www.python.org/dev/peps/pep-0008/.
"""

Wyrd In: Time tracker and task manager
CC-Share Alike 2012 © The Wyrd In team
https://github.com/WyrdIn

"""
from task import Task


def get_task(session, selection=None):
    # Check that the selection is satisfiable.
    if selection is not None and not selection:
        raise ValueError("Cannot ask for a task with empty selection.")

    task = None
    print("What is the task? ")
    if selection is not None:
        restricted = True
    else:
        selection = session.tasks
        restricted = False

    str2task = dict()
    int2task = dict()
    for task_index, task in enumerate(selection):
        # FIXME Distinguish between different tasks with the same string
        # representation.
        task_str = str(task)
        str2task[task_str] = task
        int2task[task_index] = task
    if restricted:
        choosefrom(str2task.keys())

    shown_selection = False
    taskname = input("> ")
    while not taskname or taskname == "?":
        if restricted:
            choosefrom(str2task.keys())
        else:
            if selection:
                shown_selection = True
                choosefrom(str2task.keys(),
                           msg="You can choose from the existing tasks:")
            else:
                print("There are currently no tasks defined.")
        taskname = input("> ")
    # Should the task be one of existing Task tasks,
    if restricted:
        # Find the Task task.
        while taskname not in str2task and taskname not in int2task:
            if not taskname or taskname == "?":
                choosefrom(str2task.keys())
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
            # Create a new task, asking for its respective project too.
            project = get_project(session)
            task = Task(taskname, project)
    return task


def choosefrom(selection, msg="Choose from the following list:"):
    print(msg)
    for index, item in enumerate(selection):
        print ("    {: >4d} {}".format(index, item))
    print("")


def get_project(session):
    """Solicits a project name from the user.

    An empty project is accepted too.

    """
    # TODO: Here should be some form of tab-completion.
    print("What project does it belong to?")
    project = input("> ")
    while project and project not in session.projects:
        print("You have not told me about this project yet.")
        list_projects(session)
        print("Specify the project again, please.\n" + \
              "(You can always use an empty string, meaning no project.)")
        project = input("> ")
    return project


def list_projects(session):
    print("List of current projects:")
    for project in sorted(session.projects):
        print("    {}".format(project))
    print("")


def list_tasks(session):
    print("List of current tasks:")
    for task in sorted(session.tasks):
        print("    {}".format(task))
    print("")
