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

import sumpf


parser = argparse.ArgumentParser(description="Load a module and print its docstrings into some HTML files.")
parser.add_argument("-o, --output", dest="output_dir", action="store", default=".", help="The directory to where the HTML-files shall be written")
parser.add_argument("-d, --doxygen", dest="doxygen_dir", action="store", default="", help="Optional: The directory where the class documentation from doxygen can be found")
parser.add_argument("-m, --module", dest="module", action="store", default="sumpf", help="The module that shall be documented")
parser.add_argument("-V, --no-variables", dest="no_variables", action="store_true", default=False, help="Do not create a column for the variables in the module")
parser.add_argument("-s, --script", dest="script", action="store", default="", help="A javascript file that will be imported at the beginning of the <body> tag. This could be used to add a header or a navigation bar.")
args = parser.parse_args()


def format_docstring(docstring):
    return docstring.strip().replace("\n", "<br />\n")


exec("import " + args.module + " as module")

link_to_doxygen = args.doxygen_dir != ""
include_variables = not args.no_variables
cols = 4
if not include_variables:
    cols -= 1

module_path = os.sep.join(module.__file__.split(os.sep)[0:-1])
if module.__file__.startswith(os.sep) and not module_path.startswith(os.sep):
    module_path = os.sep + module_path
output_path = sumpf.helper.normalize_path(args.output_dir)
doxygen_path = sumpf.helper.normalize_path(args.doxygen_dir)
if link_to_doxygen:
    op_list = output_path.split(os.sep)
    dp_list = doxygen_path.split(os.sep)
    index = 1
    for i in range(len(op_list)):
        if op_list[i] == dp_list[i]:
            index = i + 1
        else:
            break
    dp_new = [".."] * (len(op_list) - index)
    for d in dp_list[index:]:
        dp_new.append(d)
    doxygen_path = os.path.join(*dp_new)

script = None
if args.script != "":
    script = sumpf.helper.normalize_path(args.script)
    op_list = output_path.split(os.sep)
    sp_list = script.split(os.sep)
    index = 1
    for i in range(len(op_list)):
        if op_list[i] == sp_list[i]:
            index = i + 1
        else:
            break
    sp_new = [".."] * (len(op_list) - index)
    for d in sp_list[index:]:
        sp_new.append(d)
    script = os.path.join(*sp_new)

if not os.path.exists(output_path):
    os.makedirs(output_path)


tree = sumpf.helper.walk_module(module)

color1 = "#6080FF"
color2 = "#C8E0FF"
color3 = "#E0F0FF"

for b in tree:
    mpath = module.__name__
    lmpath = "<a href='" + module.__name__ + ".htm'>" + module.__name__ + "</a>"
    for p in b[0][1:]:
        m = p.__name__.split(".")[-1]
        mpath += "." + m
        lmpath += "." + "<a href='" + mpath + ".htm'>" + m + "</a>"
    src = []
    src.append("<html>")
    src.append("    <head>")
    src.append("        <title>ModuleDoc: " + mpath + "</title>")
    src.append("        <style type='text/css'>")
    src.append("            *{")
    src.append("                vertical-align: top;")
#   src.append("                color: #000000;")
    src.append("            }")
    src.append("            *.maintable{")
    src.append("                width: 80%;")
    src.append("                margin-left: auto;")
    src.append("                margin-right: auto;")
    src.append("            }")
    src.append("            *.maintablecell{")
    src.append("                width: " + str(100 / cols) + "%;")
    src.append("                font-size: medium;")
    src.append("                background: " + color3 + ";")
    src.append("            }")
    src.append("            *.attribute{")
    src.append("            }")
    src.append("            *.attributes{")
    src.append("                font-size: larger;")
    src.append("                background: " + color1 + ";")
    src.append("            }")
    src.append("            *.modulepath{")
    src.append("                font-size: x-large;")
    src.append("                background: " + color1 + ";")
    src.append("            }")
    src.append("            *.moduledoc{")
    src.append("                font-size: medium;")
    src.append("                background: " + color3 + ";")
    src.append("            }")
    src.append("            *.headline{")
    src.append("                font-size: larger;")
    src.append("                background: " + color2 + ";")
    src.append("            }")
    src.append("            *.functiondoc{")
    src.append("                position: absolute;")
    src.append("                background-color: " + color2 + ";")
    src.append("                border-style: solid;")
    src.append("            }")
    src.append("        </style>")
    src.append("        <script type='text/javascript'>")
    src.append("            function Toggle(id){")
    src.append("                element = document.getElementById(id);")
    src.append("                if (element.style.display != 'none')")
    src.append("                    element.style.display = 'none';")
    src.append("                else{")
    src.append("                    HideFunctionDoc();")
    src.append("                    element.style.display = 'block';")
    src.append("                }")
    src.append("            }")
    src.append("")
    src.append("            function HideFunctionDoc(){")
    for f in b[3]:
        if f.__doc__ is not None:
            src.append("                document.getElementById('" + f.__name__ + "').style.display = 'none';")
    src.append("            }")
    src.append("        </script>")
    src.append("    </head>")
    src.append("    <body onLoad='HideFunctionDoc()'>")
    if script is not None:
        src.append("        <script src='" + script + "' type='text/javascript'></script>")
    src.append("        <table class='maintable'>")
    src.append("            <tr>")
    src.append("                <td class='maintablecell modulepath'>Module</td>")
    src.append("                <th colspan='" + str(cols - 1) + "' class='maintablecell modulepath'>" + lmpath + "</th>")
    src.append("            </tr>")
    src.append("            <tr>")
    src.append("                <td class='maintablecell headline'>Docstring</td>")
    src.append("                <td colspan='" + str(cols - 1) + "' class='maintablecell moduledoc'>" + format_docstring(b[0][-1].__doc__) + "</td>")
    src.append("            </tr>")
    src.append("            <tr>")
    src.append("                <th colspan='" + str(cols) + "' class='maintablecell attributes'>Attributes</th>")
    src.append("            </tr>")
    src.append("            <tr>")
    src.append("                <th class='maintablecell headline'>Modules</th>")
    src.append("                <th class='maintablecell headline'>Classes</th>")
    src.append("                <th class='maintablecell headline'>Functions</th>")
    if include_variables:
        src.append("                <th class='maintablecell headline'>Variables</th>")
    src.append("            </tr>")
    src.append("            <tr>")
    src.append("                <td class='maintablecell'>")
    mlist = []
    for m in b[1]:
        mlist.append(m.__name__.split(".")[-1])
    mlist.sort()
    for m in mlist:
        src.append("                    <div class='attribute'><a href='" + mpath + "." + m + ".htm'>" + m + "</a></div>")
    src.append("                </td>")
    src.append("                <td class='maintablecell'>")
    cdict = {}
    for c in b[2]:
        cdict[c.__name__] = c
    clist = list(cdict.keys())
    clist.sort()
    for c in clist:
        if cdict[c] in (int, float, bool, str) or inspect.isbuiltin(cdict[c]) or not link_to_doxygen:
            src.append("                    <div class='attribute'>" + c + "</div>")
        else:
            fullpath = inspect.getfile(cdict[c])
            relpath = fullpath.split(module_path + os.sep)[1].split(".pyc")[0]
            doxygenfile = "class_"
            doxygenfile += relpath.replace(os.sep + "_", "_1_1__").replace(os.sep, "_1_1")
            doxygenfile += "_1_1" + c.replace("_", "__").rstrip(".py")
            doxygenfile += ".html"
            src.append("                    <div class='attribute'><a href=" + os.path.join(doxygen_path, doxygenfile) + ">" + c + "</a></div>")
    src.append("                </td>")
    src.append("                <td class='maintablecell'>")
    fdict = {}
    for f in b[3]:
        fdict[f.__name__] = f
    flist = list(fdict.keys())
    flist.sort()
    for f in flist:
        src.append("                    <div class='attribute'>")
        if f.__doc__ is not None:
            src.append("                        <a href='javascript:Toggle(\"" + f + "\")'>" + f + "<a>")
            src.append("                        <div class='functiondoc hidden' id='" + f + "'>" + format_docstring(fdict[f].__doc__) + "</div>")
        else:
            src.append("                        " + f)
            print("%s is not documented %s" % (str(f), str(b[0])))
        src.append("                    </div>")
    src.append("                </td>")
    if include_variables:
        src.append("                <td class='maintablecell'>")
        vlist = b[4]
        vlist.sort()
        for v in vlist:
            if v not in ["__builtins__", "__doc__", "__file__", "__name__", "__package__"]:
                src.append("                    <div class='attribute'>" + v + "</div>")
        src.append("                </td>")
    src.append("            </tr>")
    src.append("        </table>")
    src.append("    </body>")
    src.append("</html>")

    with open(os.path.join(output_path, mpath + ".htm"), "w") as docfile:
        docfile.write("\n".join(src))

