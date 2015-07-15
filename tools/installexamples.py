#!/usr/bin/env python

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

import argparse
import inspect
import os
import stat

try:
    import sumpf
except ImportError:
    print("You have to install SuMPF first")
    exit()

parser = argparse.ArgumentParser(description="Creates files for each example in SuMPF to make them executable as normal programs")
parser.add_argument("-o, --output", dest="output_dir", action="store", default=".", help="The directory to where the output files shall be written")
args = parser.parse_args()

output_path = sumpf.helper.normalize_path(args.output_dir)
if not os.path.exists(output_path):
    os.makedirs(output_path)

examplevars = vars(sumpf.examples)
for name in list(examplevars.keys()):
    function = examplevars[name]
    if inspect.isfunction(function):
        parameters = {}
        shortcuts = {}
        argspec = inspect.getargspec(function)
        for i in range(len(argspec[0])):
            parameters[argspec[0][i]] = [argspec[3][i], ""]
        doclist = function.__doc__.split("@")
        doc = "\\n".join([l.strip() for l in doclist[0].strip().split("\n")])
        for d in doclist[1:]:
            if d.strip().startswith("param"):
                l = d.split("param")[1].strip()
                ll = l.split(":")
                pname = ll[0].strip()
                if pname in parameters:
                    parameters[pname][1] = ":".join(ll[1:]).strip()
        # create the source code for the file
        source = ["#!/usr/bin/env python"]
        source.append("")
        source.append("# This file has been created automatically with the installexamples-tool of SuMPF")
        source.append("# It makes the example '" + name + "' available as a shell command")
        source.append("")
        source.append("import argparse")
        source.append("import sumpf")
        source.append("")
        source.append("parser = argparse.ArgumentParser(description='" + doc + "')")
        for p in parameters:
            option = "--" + p
            if p in shortcuts:
                option = "-" + shortcuts[p] + ", " + option
            default = parameters[p][0]
            if isinstance(default, str):
                default = "'" + default + "'"
            else:
                default = str(default)
            source.append("parser.add_argument('" + option + "', dest='" + p + "', action='store', default=" + default + ", help='" + parameters[p][1] + "')")
        source.append("args = parser.parse_args()")
        source.append("")
        call = ["sumpf.examples.", name, "("]
        for p in parameters:
            call.append(p + "=args." + p + ", ")
        call[-1] = call[-1].rstrip(", ")
        call.append(")")
        source.append("".join(call))
        source.append("")
        # write the source to a file
        filename = os.path.join(output_path, "sumpf_" + name)
        with open(filename, "w") as script:
            script.write("\n".join(source))
        os.chmod(filename, stat.S_IMODE(os.stat(filename).st_mode) | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

