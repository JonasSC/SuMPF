# SuMPF - Sound using a Monkeyforest-like processing framework
# Copyright (C) 2012-2013 Jonas Schulte-Coerne
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


@unittest.skipUnless(sumpf.config.get("test_gui"), "The graphical user interface is not being tested")
@unittest.skipIf(sumpf.config.get("unload_numpy"), "Testing modules that require the full featured numpy are skipped")
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
		# change Data
		self.gen1.SetFrequency(5.0)
		self.assertEqual(len(plt1._panel._plots.values()[0].values()[0].lines), 2)	# The number of lines has to be the same as the number of channels in the input signal
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
		self.assertEqual(gc.garbage, [])											# The plot should not leave any dead objects behind
		sumpf.gui.join_mainloop()

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
		self.assertRaises(RuntimeError, plt.HidePhase)			# Attempting to hiding the last shown plot should raise an error
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
		self.assertEqual(gc.garbage, [])						# The plot should not leave any dead objects behind
		sumpf.gui.join_mainloop()

	def test_tiled_plots(self):
		"""
		Tests the TiledSignalPlotPanel and TiledSpectrumPlotPanel classes.
		"""
		import wx
		signal = sumpf.Signal(channels=((1.0, 2.0, 3.0, 4.0), (2.0, 1.0, 0.0, -1.0), (0.5, 0.5, 0.5, 0.5), (3.0, 0.0, 3.0, 1.0), (1.0, 2.0, 1.0, 3.0)), samplingrate=4.0)
		fft = sumpf.modules.FourierTransform(signal=signal)
		# TiledSignalPlotPanel
		twindow = sumpf.gui.Window(parent=None, size=(800, 600))
		tsizer = wx.BoxSizer(wx.VERTICAL)
		twindow.SetSizer(tsizer)
		tpanel = sumpf.modules.TiledSignalPlotPanel(parent=twindow)
		tpanel.SetSignal(signal)
		tsizer.Add(tpanel, 1, wx.EXPAND)
		twindow.Layout()
		twindow.Show()
		tpanel.SetMargin(0.2)
		twindow.Close()
		# TiledSpectrumPlotPanel in a SpectrumPlotWindow
		fwindow = sumpf.modules.SpectrumPlotWindow(panel_class=sumpf.modules.TiledSpectrumPlotPanel)
		sumpf.connect(fft.GetSpectrum, fwindow.SetSpectrum)
		fwindow.Show()
		fwindow.SetCursors([0.25, 0.5, 0.75])
		fwindow.ShowPhase()
		fwindow.Close()
		# collect garbage
		gc.collect()
		self.assertEqual(gc.garbage, [])	# The plot should not leave any dead objects behind
		sumpf.gui.join_mainloop()

