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
from .window import Window
from .gauge import Gauge


class ProgressDialog(Window):
    """
    A simple progress dialog.
    Other than the wx.ProgressDialog, this one does not offer a "Cancel"-button
    and it has a different way of setting the progress.
    This dialog is meant to be connected to a progress indicator, to track the
    progress of a calculation of a progressing chain.
    """
    def __init__(self, message="", parent=None, *args, **kwargs):
        """
        @param message: the message string that shall be displayed in the dialog
        @param parent: the parent wx Widget
        @param *args, **kwargs: other parameters for the constructor of a sumpf.gui.Window
        """
        Window.__init__(self, parent=parent, *args, **kwargs)
        self.__sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.__sizer)
        self.__sizer.AddStretchSpacer()
        self.__message = wx.StaticText(parent=self, label=message)
        self.__sizer.Add(self.__message, 0, wx.ALIGN_CENTER_HORIZONTAL)
        self.__gauge = Gauge(parent=self, range=1, size=(400, 25))
        self.__sizer.Add(self.__gauge, 0, wx.EXPAND)
        self.__sizer.AddStretchSpacer()
        self.Layout()
        self.Fit()
        self.__shown = False

    @sumpf.Input(tuple)
    def SetProgress(self, progress):
        """
        This method can be connected to a progress indicator's GetProgressAsTuple
        method, so this Dialog can keep updated about the progress of a processing
        chain's calculation.
        The parameter progress can be either a tuple with two values (max, current),
        where max is the total number of tasks, that have to be completed and current
        is the number of those, which have finished.
        If progress is a three-element tuple (max, current, message), the message
        of the progress dialog will be updated to the value of the third parameter.
        @param progress: a tuple (max, current)
        """
        try:
            self.__gauge.SetProgress(progress)
            if not self.__shown:
                self.Show()
                self.Center()
                self.__shown = True
            if progress[2] is not None:
                self.SetMessage(progress[2])
            if progress[0] > 0:
                if progress[0] <= progress[1]:
                    self.__shown = False
                    self.Close()
        except wx.PyDeadObjectError:
            pass

    @sumpf.Input(str)
    def SetMessage(self, message):
        """
        Sets the message for the ProgressDialog.
        @param message: the new message string
        """
        try:
            sumpf.gui.run_in_mainloop(self.__message.SetLabel, message)
            self.Layout()
        except wx.PyDeadObjectError:
            pass

    def Destroy(self):
        """
        An override of the Window's Destroy method.
        This method also destroys the connectors, so that this dialog can be
        easily garbage collected.
        """
        sumpf.destroy_connectors(self)
        Window.Destroy(self)

