# Copyright 2016-2018 Dirk Thomas
# Licensed under the Apache License, Version 2.0

import platform
import sys

from colcon_core.event.job import JobEnded
from colcon_core.event.job import JobQueued
from colcon_core.event.job import JobStarted
from colcon_core.event_handler import EventHandlerExtensionPoint
from colcon_core.plugin_system import satisfies_version


class TerminalTitleEventHandler(EventHandlerExtensionPoint):
    """
    Show status in the terminal title.

    The extension handles events of the following types:
    - :py:class:`colcon_core.event.job.JobQueued`
    - :py:class:`colcon_core.event.job.JobStarted`
    - :py:class:`colcon_core.event.job.JobEnded`
    """

    # the priority should be lower than all status and notification extensions
    # in order to not trigger the notification before they are finished
    PRIORITY = 20

    def __init__(self):  # noqa: D107
        super().__init__()
        satisfies_version(
            EventHandlerExtensionPoint.EXTENSION_POINT_VERSION, '^1.0')
        self._queued_count = 0
        self._ongoing_count = 0
        self._ended_count = 0

    def __call__(self, event):  # noqa: D102
        data = event[0]

        if isinstance(data, JobQueued):
            self._queued_count += 1

        elif isinstance(data, JobStarted):
            self._ongoing_count += 1
            self._update()

        elif isinstance(data, JobEnded):
            assert self._ongoing_count > 0
            self._ongoing_count -= 1
            self._ended_count += 1
            self._update()

    def _update(self):
        message = '{context.command_name} build ' \
            '[{_ended_count}/{_queued_count} done] ' \
            '[{_ongoing_count} ongoing]'.format_map(self.__dict__)

        if platform.system() == 'Windows':
            return _windows_update_title(message)
        else:
            return _ascii_update_title(message)


def _ascii_update_title(message):
    sys.stdout.write('\x1b]0;{message}\x07'.format_map(locals()))


def _windows_update_title(message):
    import ctypes
    ctypes.windll.kernel32.SetConsoleTitleW(message)
