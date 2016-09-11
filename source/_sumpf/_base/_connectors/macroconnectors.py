# SuMPF - Sound using a Monkeyforest-like processing framework
# Copyright (C) 2012-2016 Jonas Schulte-Coerne
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

"""
i    o    I    O
C
F -> A -> A -> A
  -> R
________________
               C
          Q <-
     Q <- V
            -> R
"""

from .singleinputconnector import SingleInputConnector
from .outputconnectors import NotCachingOutputConnector


class MacroInputConnector(SingleInputConnector):
    def __init__(self, instance, input_data_type, method, output_data_type):
        SingleInputConnector.__init__(self, instance=instance, data_type=input_data_type, method=method, observers=())
        self.GetOutput = NotCachingOutputConnector()

