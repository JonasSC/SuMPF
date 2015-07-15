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

import sumpf
from .plotwindow import PlotWindow
from .spectrumplotpanel import SpectrumPlotPanel


class SpectrumPlotWindow(PlotWindow):
    """
    A class whose instances create a window in which plots of Spectrums are shown.
    It basically has the same properties as a SpectrumPlotPanel, but it comes with
    its own window. This window is created every time, when the Show-method is
    called and the window is currently not shown. This means that a closed
    SpectrumPlotWindow can be shown again after closing.
    """
    def __init__(self):
        PlotWindow.__init__(self)
        self.LogarithmicX()
        self.__spectrum = sumpf.Spectrum()
        self.__log_magnitude = True
        self.__log_phase = False
        self.__log_continuousphase = False
        self.__log_groupdelay = False
        self.__show_magnitude = True
        self.__show_phase = True
        self.__show_continuousphase = False
        self.__show_groupdelay = False

    def _GetPanel(self):
        """
        Returns a properly initialized plot panel instance.
        @retval : a plot panel instance
        """
        panel = SpectrumPlotPanel(parent=self._window)
        panel.SetSpectrum(self.__spectrum)
        if self.__log_magnitude:
            panel.LogarithmicMagnitude()
        else:
            panel.LinearMagnitude()
        if self.__log_phase:
            panel.LogarithmicPhase()
        else:
            panel.LinearPhase()
        if self.__log_continuousphase:
            panel.LogarithmicContinuousPhase()
        else:
            panel.LinearContinuousPhase()
        if self.__log_groupdelay:
            panel.LogarithmicGroupDelay()
        else:
            panel.LinearGroupDelay()
        if self.__show_magnitude:
            panel.ShowMagnitude()
        if self.__show_phase:
            panel.ShowPhase()
        if self.__show_continuousphase:
            panel.ShowContinuousPhase()
        if self.__show_groupdelay:
            panel.ShowGroupDelay()
        else:
            panel.HideGroupDelay()
        if not self.__show_continuousphase:
            panel.HideContinuousPhase()
        if not self.__show_phase:
            panel.HidePhase()
        if not self.__show_magnitude:
            panel.HideMagnitude()
        return panel

    @sumpf.Input(sumpf.Spectrum)
    def SetSpectrum(self, spectrum):
        """
        Sets the Spectrum which shall be plotted.
        @param spectrum: The Spectrum to plot
        """
        self.__spectrum = spectrum
        if self._panel is not None:
            self._panel.SetSpectrum(spectrum)

    @sumpf.Trigger()
    def LinearMagnitude(self):
        """
        Shows the magnitude linearly
        """
        self.__log_magnitude = False
        if self._panel is not None:
            self._panel.LinearMagnitude()

    @sumpf.Trigger()
    def LogarithmicMagnitude(self):
        """
        Shows the magnitude logarithmically.
        """
        self.__log_magnitude = True
        if self._panel is not None:
            self._panel.LogarithmicMagnitude()

    @sumpf.Trigger()
    def LinearPhase(self):
        """
        Shows the phase linearly.
        """
        self.__log_phase = False
        if self._panel is not None:
            self._panel.LinearPhase()

    @sumpf.Trigger()
    def LogarithmicPhase(self):
        """
        Shows the phase logarithmically.
        """
        self.__log_phase = True
        if self._panel is not None:
            self._panel.LogarithmicPhase()

    @sumpf.Trigger()
    def LinearContinuousPhase(self):
        """
        Shows the continuous phase linearly.
        """
        self.__log_continuousphase = False
        if self._panel is not None:
            self._panel.LinearContinuousPhase()

    @sumpf.Trigger()
    def LogarithmicContinuousPhase(self):
        """
        Shows the continuous phase logarithmically.
        """
        self.__log_continuousphase = True
        if self._panel is not None:
            self._panel.LogarithmicContinuousPhase()


    @sumpf.Trigger()
    def LinearGroupDelay(self):
        """
        Shows the group delay linearly.
        """
        self.__log_groupdelay = False
        if self._panel is not None:
            self._panel.LinearGroupDelay()

    @sumpf.Trigger()
    def LogarithmicGroupDelay(self):
        """
        Shows the group delay logarithmically.
        """
        self.__log_groupdelay = True
        if self._panel is not None:
            self._panel.LogarithmicGroupDelay()

    @sumpf.Trigger()
    def ShowMagnitude(self):
        """
        Shows the magnitude plot.
        """
        self.__show_magnitude = True
        if self._panel is not None:
            self._panel.ShowMagnitude()

    @sumpf.Trigger()
    def HideMagnitude(self):
        """
        Hides the magnitude plot.
        """
        self.__show_magnitude = False
        if self._panel is not None:
            self._panel.HideMagnitude()

    @sumpf.Trigger()
    def ShowPhase(self):
        """
        Shows the phase plot.
        """
        self.__show_phase = True
        if self._panel is not None:
            self._panel.ShowPhase()

    @sumpf.Trigger()
    def HidePhase(self):
        """
        Hides the phase plot.
        """
        self.__show_phase = False
        if self._panel is not None:
            self._panel.HidePhase()

    @sumpf.Trigger()
    def ShowContinuousPhase(self):
        """
        Shows the continuous phase plot.
        """
        self.__show_continuousphase = True
        if self._panel is not None:
            self._panel.ShowContinuousPhase()

    @sumpf.Trigger()
    def HideContinuousPhase(self):
        """
        Hides the continuous phase plot.
        """
        self.__show_continuousphase = False
        if self._panel is not None:
            self._panel.HideContinuousPhase()

    @sumpf.Trigger()
    def ShowGroupDelay(self):
        """
        Shows the group delay plot.
        """
        self.__show_groupdelay = True
        if self._panel is not None:
            self._panel.ShowGroupDelay()

    @sumpf.Trigger()
    def HideGroupDelay(self):
        """
        Hides the group delay plot.
        """
        self.__show_groupdelay = False
        if self._panel is not None:
            self._panel.HideGroupDelay()

