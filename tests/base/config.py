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

import os
import shutil
import tempfile
import unittest
import sumpf


class TestConfig(unittest.TestCase):
    """
    A TestCase for the config classes and the creation of config objects.
    """
    def test_get_set_parent(self):
        """
        Tests if the getter and setter methods work as expected and if the
        parent config system works.
        """
        NAME = "onlyfortesting1"
        config1 = sumpf.config.create_config(variables={NAME : 42}, path=None)
        self.assertEqual(config1.Get(NAME), sumpf.config.get(NAME))
        config2 = sumpf.config.create_config(variables={}, path=None)
        self.assertEqual(config1.Get(NAME), sumpf.config.get(NAME))
        self.assertEqual(config2.Get(NAME), sumpf.config.get(NAME))
        sumpf.config.set(NAME, 23)
        self.assertEqual(config1.Get(NAME), 42)
        self.assertEqual(sumpf.config.get(NAME), 23)
        self.assertEqual(config2.Get(NAME), sumpf.config.get(NAME))
        self.assertRaises(IndexError, sumpf.config.set, NAME + "666", 666)
        sumpf.config.set(NAME, "7")
        self.assertEqual(sumpf.config.get(NAME), 7)

    @unittest.skipUnless(sumpf.config.get("write_to_disk"), "Tests that write to disk are skipped")
    def test_file_handling(self):
        """
        Tests if writing to and loading from a file works.
        """
        NAME1 = "onlyfortesting1"
        NAME2 = "onlyfortesting2"
        tempdir = tempfile.mkdtemp()
        path = os.path.join(tempdir, "config")
        try:
            config1 = sumpf.config.create_config(variables={NAME1 : 42, NAME2 : 23}, path=path)
            sumpf.config.set(NAME2, 42)
            config2 = sumpf.config.create_config(variables={}, path=path)
            self.assertEqual(config2.Get(NAME2), 42)
            config1.Set(NAME1, 67)
            config1.Set(NAME2, 99)
            self.assertEqual(config2.Get(NAME1), 42)
            self.assertEqual(config2.Get(NAME2), 42)
        finally:
            shutil.rmtree(tempdir)

    def test_other_functions(self):
        """
        Runs some functions that are not run elsewhere during testing.
        """
        uc = sumpf.config.get_sumpf_user_config()
        sc = sumpf.config.get_sumpf_system_config()
        self.assertNotEqual(uc, sc)
        self.assertEqual(type(uc), type(sc))

