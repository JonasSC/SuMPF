#!/usr/bin/env python

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

import os
from distutils.core import setup

dirs = {}
additional_files = {}
for i in os.walk("."):
	dirname = i[0].lstrip("./")
	if dirname != "":
		package = dirname.replace(os.sep, ".")
		dirs[package] = dirname
		for filename in i[2]:
			if not filename.endswith(".py") and \
			   not filename.endswith(".pyc"):
				if package not in additional_files:
					additional_files[package] = []
				additional_files[package].append(filename)

setup(name="SuMPF",
      version="0.9",
      description="Sound using a Monkeyforest-like processing framework",
      author="Jonas Schulte-Coerne",
      author_email="jonas@schulte-coerne.de",
      license="License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
      packages=dirs.keys(),
      package_dir=dirs,
      package_data=additional_files,
      py_modules=["sumpf"])

