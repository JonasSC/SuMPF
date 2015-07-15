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
from matplotlib.backends.backend_wx import NavigationToolbar2Wx

import sumpf


class Toolbar(wx.Panel):
    """
    A toolbar for plots
    """
    def __init__(self, parent, canvas, components):
        """
        @param parent: the parent wx Window of this toolbar
        @param canvas: the matplotlib canvas to which this toolbar belongs
        @param components: a list of names of the plotted data's components
        """
        wx.Panel.__init__(self, parent=parent)
        self.__parent = parent
        self.__canvas = canvas
        # wx stuff
        self.__sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(self.__sizer)
        # matplotlib toolbar
        self.__mpl_toolbar = sumpf.gui.run_in_mainloop(NavigationToolbar2Wx, self.__canvas)
        self.__mpl_toolbar.Realize()
        self.__mpl_toolbar.Reparent(self)
        self.__sizer.Add(self.__mpl_toolbar)
        self.__mpl_toolbar.update()
        # other entries
        self.__AddSeparator()
        self.__legend = self.__AddCheckbox(caption=" legend ", onclick=self.__OnLegend, description="Shows/Hides the legend in the plot")
        self.__grid = self.__AddCheckbox(caption=" grid ", onclick=self.__OnGrid, threestate=True, description="Shows/Hides the grid")
        self.__cursors = self.__AddCheckbox(caption=" cursors ", onclick=self.__OnCursors, description="Shows/Hides the cursors")
        self.__AddSeparator()
        self.__logx = self.__AddCheckbox(caption=" log x ", onclick=self.__OnLogX, description="Shows the x axis logarithmicly")
        self.__components = {}
        for c in components:
            self.__components[c] = {}
        self.__AddMenu(label="log y", entries=components, function=self.__OnLogY)
        if len(components) > 1:
            self.__AddSeparator()
            self.__AddMenu(label="show", entries=components, function=self.__OnShow)
        self.__AddSeparator()
        self.__move_plots_together = self.__AddCheckbox(caption="join moves", onclick=self.__OnMoveTogether, description="Sets if the plots shall be panned and\nzoomed together or independently")
        # finish
        sumpf.gui.run_in_mainloop(self.Layout)

    def UpdateToolbar(self, legend, grid, cursors, logx, logy, shown, move_plots_together):
        """
        Updates the checkboxes in the toolbar.
        """
        def update():
            self.__legend.SetValue(legend)
            if grid is None:
                self.__grid.Set3StateValue(wx.CHK_UNDETERMINED)
            elif grid:
                self.__grid.Set3StateValue(wx.CHK_CHECKED)
            else:
                self.__grid.Set3StateValue(wx.CHK_UNCHECKED)
            self.__cursors.SetValue(cursors)
            self.__logx.SetValue(logx)
            if len(self.__components) > 1:
                for p in self.__components:
                    self.__components[p]["log y"].Check(check=p in logy)
                    self.__components[p]["log y"].Enable(p in shown)
                    self.__components[p]["show"].Check(check=p in shown)
                    self.__components[p]["show"].Enable()
                if len(shown) == 1:
                    self.__components[list(shown)[0]]["show"].Enable(False)
            self.__move_plots_together.SetValue(move_plots_together)
        sumpf.gui.run_in_mainloop(update)

    def __AddCheckbox(self, caption, onclick, threestate=False, description=""):
        """
        Adds a checkbox to the toolbar.
        """
        checkbox = None
        sizer = wx.BoxSizer(wx.VERTICAL)
        if threestate:
            checkbox = wx.CheckBox(parent=self, style=wx.CHK_3STATE | wx.CHK_ALLOW_3RD_STATE_FOR_USER)
        else:
            checkbox = wx.CheckBox(parent=self)
        label = wx.StaticText(parent=self, label=caption)
        sizer.Add(checkbox, 0, wx.ALIGN_CENTER)
        sizer.Add(label, 0, wx.ALIGN_CENTER)
        self.__sizer.Add(sizer)
        if description != "":
            checkbox.SetToolTip(wx.ToolTip(description))
            label.SetToolTip(wx.ToolTip(description))
        checkbox.Bind(wx.EVT_CHECKBOX, onclick)
        return checkbox

    def __AddSeparator(self):
        """
        Adds a separator to the toolbar.
        """
        self.__sizer.AddStretchSpacer()
#       self.__sizer.Add(wx.StaticText(parent=self, label=" "))

    def __AddMenu(self, label, entries, function):
        """
        Adds a button to the toolbar that shows a menu of checkboxes.
        """
        button = wx.Button(parent=self, label=label, style=wx.BU_EXACTFIT)
        menu = wx.Menu()
        def popup_menu(event):
            self.PopupMenu(menu)
        self.Bind(event=wx.EVT_BUTTON, handler=popup_menu, source=button)
        for e in entries:
            item = menu.AppendCheckItem(id=wx.ID_ANY, text=e)
            self.Bind(event=wx.EVT_MENU, handler=function, source=item)
            self.__components[e][label] = item
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(button, 1, wx.EXPAND)
        self.__sizer.Add(sizer, 0, wx.EXPAND)
        return menu

    def __OnLegend(self, event):
        """
        Event handler for when the "Legend"-checkbox is clicked.
        """
        if self.__legend.IsChecked():
            self.__parent.ShowLegend()
        else:
            self.__parent.HideLegend()

    def __OnGrid(self, event):
        """
        Event handler for when the "Grid"-checkbox is clicked.
        """
        state = self.__grid.Get3StateValue()
        if state == wx.CHK_CHECKED:
            self.__parent.ShowFullGrid()
        elif state == wx.CHK_UNDETERMINED:
            self.__parent.ShowMajorGrid()
        elif state == wx.CHK_UNCHECKED:
            self.__parent.HideGrid()

    def __OnCursors(self, event):
        """
        Event handler for when the "Cursors"-checkbox is clicked.
        """
        if self.__cursors.IsChecked():
            self.__parent.ShowCursors()
        else:
            self.__parent.HideCursors()

    def __OnLogX(self, event):
        """
        Event handler for when the "log x"-checkbox is clicked.
        """
        if self.__logx.IsChecked():
            self.__parent.LogarithmicX()
        else:
            self.__parent.LinearX()

    def __OnLogY(self, event):
        """
        Event handler for when a "log y"-checkbox is clicked.
        """
        for c in self.__components:
            if event.GetId() == self.__components[c]["log y"].GetId():
                self.__parent.LogarithmicY(component=c, log=self.__components[c]["log y"].IsChecked())

    def __OnShow(self, event):
        """
        Event handler for when a "join moves"-checkbox is clicked.
        """
        for c in self.__components:
            if event.GetId() == self.__components[c]["show"].GetId():
                self.__parent.ShowComponent(component=c, show=self.__components[c]["show"].IsChecked())

    def __OnMoveTogether(self, event):
        """
        Event handler for when a "join moves"-checkbox is clicked.
        """
        if self.__move_plots_together.IsChecked():
            self.__parent.MovePlotsTogether()
        else:
            self.__parent.MovePlotsIndependently()

