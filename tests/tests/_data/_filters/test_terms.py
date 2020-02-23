# This file is a part of the "SuMPF" package
# Copyright (C) 2018-2020 Jonas Schulte-Coerne
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

"""Contains tests for the term classes, from which a the filter's transfer functions are built"""

import json
import hypothesis
import tests
from sumpf import _internal as sumpf_internal


@hypothesis.given(tests.strategies.terms)
def test_as_dict(term):
    """Tests the serialization and deserialization of terms to/from a dictionary."""
    dictionary = term.as_dict()
    assert json.dumps(dictionary) is not None   # the dictionaries should be serializable to a JSON string
    restored = sumpf_internal.filter_readers.term_from_dict(dictionary)
    assert restored == term
