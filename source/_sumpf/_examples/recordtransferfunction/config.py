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

def create_config():
    defaults = {"capture_port": 0,
                "playback_port": 0,
                "sweep_duration": 2.0,
                "silence_duration": 0.06,
                "sweep_start_frequency": 20.0,
                "sweep_stop_frequency": 20000.0,
                "sweep_exponentially": True,
                "fade_out": 0.02,
                "amplitude": 0.9,
                "averages": 1,
                "apply_regularization": True,
                "regularization_start_frequency": 20.0,
                "regularization_stop_frequency": 20000.0,
                "regularization_transition_width": 20.0,
                "regularization_epsilon": 0.1,
                "apply_lowpass": False,
                "lowpass_cutoff_frequency": 20000.0,
                "lowpass_order": 16,
                "apply_window": False,
                "window_function": "Hanning",
                "window_start": 0.3,
                "window_stop": 0.5,
                "normalization": 0,
                "normalize_individually": False,
                "normalization_frequency": 1000.0,
                "view_start_frequency": 20.0,
                "view_stop_frequency": 20000.0}
    sumpf.config.create_config(variables=defaults, path=sumpf.helper.normalize_path("/etc/sumpf/recordtransferfunction"))
    sumpf.config.create_config(variables={}, path=sumpf.helper.normalize_path("~/.sumpf/recordtransferfunction"))

