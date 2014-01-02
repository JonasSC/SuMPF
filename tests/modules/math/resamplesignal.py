# SuMPF - Sound using a Monkeyforest-like processing framework
# Copyright (C) 2012-2014 Jonas Schulte-Coerne
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

import unittest
import sumpf
import _common as common


@unittest.skipUnless(common.lib_available("numpy"), "These tests require the library 'numpy' to be available.")
@unittest.skipUnless(common.lib_available("scikits.samplerate"), "These tests require the library 'scikits.samplerate'")
class TestResampleSignal(unittest.TestCase):
	"""
	A test case for the ResampleSignal module.
	"""
	@unittest.skipUnless(sumpf.config.get("run_long_tests"), "Long tests are skipped")
	def test_resampling(self):
		"""
		Tests if the resampling yields the correct results.
		"""
		samplingrate_original = 32000.0
		samplingrate_high = 35734.0
		samplingrate_low = 30442.0
		self.assertNotEqual((samplingrate_high / samplingrate_original) % 1, 0.0)	# samplingrate_high must not be an integer multiple of samplingrate_original
		self.assertNotEqual((samplingrate_original / samplingrate_low) % 1, 0.0)	# samplingrate_low must not be an integer fraction of samplingrate_original
		# generate original signal and ideally resampled signals
		prp = sumpf.modules.ChannelDataProperties(samplingrate=samplingrate_original)
		dur = sumpf.modules.DurationToLength(duration=1.0)
		sumpf.connect(prp.GetSamplingRate, dur.SetSamplingRate)
		sumpf.connect(dur.GetLength, prp.SetSignalLength)
		gen1 = sumpf.modules.SineWaveGenerator(frequency=samplingrate_low / 2.1)
		sumpf.connect(prp.GetSignalLength, gen1.SetLength)
		sumpf.connect(prp.GetSamplingRate, gen1.SetSamplingRate)
		gen2 = sumpf.modules.TriangleWaveGenerator(raising=0.2, frequency=samplingrate_low / 17.3)
		sumpf.connect(prp.GetSignalLength, gen2.SetLength)
		sumpf.connect(prp.GetSamplingRate, gen2.SetSamplingRate)
		mrg = sumpf.modules.MergeSignals()
		sumpf.connect(gen1.GetSignal, mrg.AddInput)
		sumpf.connect(gen2.GetSignal, mrg.AddInput)
		signal = mrg.GetOutput()
		prp.SetSamplingRate(samplingrate_high)
		ideal_up = mrg.GetOutput()
		prp.SetSamplingRate(samplingrate_low)
		ideal_down = mrg.GetOutput()
		self.assertEqual(signal.GetDuration(), ideal_up.GetDuration())		# the duration of the ideally upsampled Signal has to be the same as the duration of the original Signal
		self.assertEqual(signal.GetDuration(), ideal_down.GetDuration())	# the duration of the ideally downsampled Signal has to be the same as the duration of the original Signal
		# resample the Signal with the ResampleSignal module
		resampled_up = sumpf.modules.ResampleSignal(signal=signal, samplingrate=samplingrate_high).GetOutput()
		res = sumpf.modules.ResampleSignal()
		res.SetInput(signal)
		res.SetSamplingRate(samplingrate_low)
		resampled_down = res.GetOutput()
		# compare the ideally resampled Signals with those from the ResampleSignal module
		for ideal, resampled in [(ideal_up, resampled_up), (ideal_down, resampled_down)]:
			self.assertEqual(resampled.GetSamplingRate(), ideal.GetSamplingRate())
			self.assertLessEqual(abs(len(ideal) - len(resampled)), 1)		# the length of the resampled Signal must not differ from the length of the ideally resampled Signal by more than one sample
			if len(ideal) > len(resampled):
				ideal = ideal[0:len(resampled)]
			elif len(ideal) < len(resampled):
				resampled = resampled[0:len(ideal)]
			margin = sumpf.modules.DurationToLength(duration=0.005, samplingrate=ideal.GetSamplingRate()).GetLength()
			error = ideal[margin:-margin] - resampled[margin:-margin]
			errorrms = sumpf.modules.RootMeanSquare(signal=error, integration_time=sumpf.modules.RootMeanSquare.FULL).GetOutput()
			signalrms = sumpf.modules.RootMeanSquare(signal=ideal[margin:-margin], integration_time=sumpf.modules.RootMeanSquare.FULL).GetOutput()
			for c in range(len(errorrms.GetChannels())):
				snr = signalrms.GetChannels()[c][0] / errorrms.GetChannels()[c][0]
#				self.assertGreaterEqual(snr, 10 ** (140.0 / 20.0))	# The signal to noise ratio of the sampling rate conversion must be at least 140dB
				self.assertGreaterEqual(snr, 10 ** (23.0 / 20.0))	# The signal to noise ratio of the sampling rate conversion must be at least 23dB
			self.assertEqual(resampled.GetLabels(), ideal.GetLabels())

	def test_connectors(self):
		"""
		Tests if the connectors are properly decorated.
		"""
		res = sumpf.modules.ResampleSignal()
		self.assertEqual(res.SetInput.GetType(), sumpf.Signal)
		self.assertEqual(res.SetSamplingRate.GetType(), float)
		self.assertEqual(res.GetOutput.GetType(), sumpf.Signal)
		common.test_connection_observers(testcase=self,
		                                 inputs=[res.SetInput, res.SetSamplingRate],
		                                 noinputs=[],
		                                 output=res.GetOutput)

