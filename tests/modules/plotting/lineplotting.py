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

import gc
import time
import unittest

import sumpf
import _common as common


@unittest.skipUnless(sumpf.config.get("test_gui"), "The graphical user interface is not being tested")
@unittest.skipUnless(common.lib_available("numpy"), "These tests require the library 'numpy' to be available.")
class TestLinePlotting(unittest.TestCase):
    """
    A TestCase for the line plotting modules.
    """
    def setUp(self):
        frq = 10.0
        lng = 4800
        self.gen1 = sumpf.modules.SineWaveGenerator(frequency=frq, phase=1.6, samplingrate=4800.0, length=lng)
        self.gen2 = sumpf.modules.SineWaveGenerator(frequency=frq / 4, phase=0.8, samplingrate=4800.0, length=lng)
        self.mrg = sumpf.modules.MergeSignals()
        sumpf.connect(self.gen1.GetSignal, self.mrg.AddInput)
        sumpf.connect(self.gen2.GetSignal, self.mrg.AddInput)

    def test_signal_plot_and_threads(self):
        """
        Creates two signals, plots them and modifies them and the plots.
        """
        # setup plots
        plt1 = sumpf.modules.SignalPlotWindow()
        plt2 = sumpf.modules.SignalPlotWindow()
        sumpf.connect(self.mrg.GetOutput, plt1.SetSignal)
        sumpf.connect(self.gen1.GetSignal, plt2.SetSignal)
        # show window
        plt1.Show()
        plt2.Show()
        # wait until windows are initialized
        while plt1._window is None or plt1._panel is None:
            time.sleep(0.01)
        while plt2._window is None or plt2._panel is None:
            time.sleep(0.01)
        # change data
        self.gen1.SetFrequency(5.0)
        # change plots
        plt1.HideLegend()
        plt2.HideGrid()
        plt1.LogarithmicY()
        plt2.LogarithmicX()
        plt1.SetCursors([0.15])
        plt1.HideCursors()
        plt2.HideCursors()
        plt2.ShowCursors()
        plt1.ShowCursors()
        # close windows
        plt1.Close()
        plt2.Close()
        # show window 2 again
        plt2.Show()
        # wait until frame is initialized
        while plt2._window is None:
            time.sleep(0.01)
        # close Window
        plt2.Close()
        # join windows
        plt1.Join()
        plt2.Join()
        # collect garbage
        gc.collect()
        self.assertEqual(gc.garbage, [])                # The plot should not leave any dead objects behind

    def test_spectrum_plot(self):
        """
        Creates a spectrum plot.
        """
        # setup fft
        fft = sumpf.modules.FourierTransform()
        sumpf.connect(self.mrg.GetOutput, fft.SetSignal)
        # setup plot
        plt = sumpf.modules.SpectrumPlotWindow()
        sumpf.connect(fft.GetSpectrum, plt.SetSpectrum)
        # modify plot before showing
        plt.HideMagnitude()
        # show window
        plt.Show()
        # modify while showing
        plt.SetXInterval(None)
        self.assertRaises(RuntimeError, plt.HidePhase)  # Attempting to hiding the last shown plot should raise an error
        plt.ShowGroupDelay()
        plt.SetMargin(0.4)
        plt.LinearMagnitude()
        plt.HidePhase()
        plt.LogarithmicGroupDelay()
        plt.ShowContinuousPhase()
        plt.SetXInterval((10, 22050))
        # close Window
        plt.Close()
        # collect garbage
        gc.collect()
        self.assertEqual(gc.garbage, [])                # The plot should not leave any dead objects behind

