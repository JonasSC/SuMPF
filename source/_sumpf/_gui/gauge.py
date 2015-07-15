# SuMPF - Sound using a Monkeyforest-like processing framework
# Copyright (C) 2012-2015 Jonas Schulte-Coerne
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import wx
import sumpf


class Gauge(wx.Gauge):
    """
    An extension to a standard wx.Gauge, so it can be connected to a progress
    indicator. This way, the connection system can automatically update the
    visualization of its progress.
    It also has a the method "AddToStatusBar" which can be used to add an instance
    of this gauge to a status bar.
    """
    @sumpf.Input(tuple)
    def SetProgress(self, progress):
        """
        This method can be connected to a progress indicator's GetProgressAsTuple
        method, so this Gauge can keep updated about the progress of a processing
        chain's calculation.
        @param progress: a tuple (max, current), where max is the total number of methods, that have to be run and current is the number of those, which have finished
        """
        if progress[0] != 0 and progress[1] == 0:
            self.Pulse()
        else:
            self.SetRange(progress[0])
            self.SetValue(progress[1])
        sumpf.gui.run_in_mainloop(self.Update)

    def AddToStatusBar(self, statusbar, field):
        """
        A method to add the gauge to a status bar.
        @param statusbar: the statusbar instance to which the gauge shall be added
        @param field: the integer field index for the field in which the gauge shall be shown
        """
        statusbar.Bind(wx.EVT_SIZE, self.__OnStatusBarResize)
        self.Reparent(statusbar)
        self.__statusbar = statusbar
        self.__statusbarfield = field
        self.__OnStatusBarResize()

    def __OnStatusBarResize(self, event=None):
        """
        This non public method is bound to a resize event of the status bar.
        This way, the gauge is resized and repositioned accordingly, when the
        size of the status bar changes.
        """
        rect = self.__statusbar.GetFieldRect(self.__statusbarfield)
        self.SetPosition((rect.x + 2, rect.y + 2))
        self.SetSize((rect.width - 4, rect.height - 4))

