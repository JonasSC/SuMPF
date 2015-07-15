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
import os


folders = ["source", "tests", "tools"]


parser = argparse.ArgumentParser(description="Print some statistics about the source code of SuMPF.")
parser.add_argument("-f, --html", dest="html_file", action="store", default="", help="If the statistics shall be written to a html file, the path to this file can be given here.")
args = parser.parse_args()

def count_files(path):
    result = 0
    for root, dirs, files in os.walk(path):
        for filename in files:
            if filename.endswith(".py"):
                result += 1
    return result

def count_lines(path):
    source = 0
    comments = 0
    headers = 0
    empty = 0
    emptycomment = 0
    for root, dirs, files in os.walk(path):
        for filename in files:
            if filename.endswith(".py"):
                f = open(os.path.join(root, filename), 'r')
                lines = f.readlines()
                f.close()
                in_comment = False
                start = 0
                if lines[0].startswith('#!'):
                    headers += 1
                    start += 1
                for l in lines:
                    line = l.strip()
                    if len(line.split('"""')) % 2 == 0:
                        in_comment = not in_comment
                    if line == "":
                        if in_comment:
                            emptycomment += 1
                        else:
                            empty += 1
                    elif in_comment or line.startswith('#') or line.startswith('"""'):
                        comments += 1
                    else:
                        source += 1
                comments -= 15 # subtract the length of the license header
                headers += 15
    return source, comments, headers, empty, emptycomment

statistics = {}
for f in folders:
#   path = os.path.join("..", f)
    path = f
    statistics[f] = {}
    lines = count_lines(path)
    statistics[f]["files"] = count_files(path)
    statistics[f]["source"] = lines[0]
    statistics[f]["comments"] = lines[1]
    statistics[f]["headers"] = lines[2]
    statistics[f]["empty"] = lines[3]
    statistics[f]["emptycomment"] = lines[4]
    statistics[f]["total"] = lines[0] + lines[1] + lines[2] + lines[3] + lines[4]

total = {}
for s in list(statistics.values()):
    for k in s:
        if not k in total:
            total[k] = 0
        total[k] += s[k]

documentation = {"files" : 0,
                 "lines" : 0,
                 "images" : set(),
                 "image files" : 0}

for f in os.listdir("documentation"):
    if f.endswith(".htm") or f.endswith(".js") or f.endswith(".css"):
        if f != "statistics.htm":
            documentation["files"] += 1
            with open(os.path.join("documentation", f)) as d:
                l = d.readlines()
                documentation["lines"] += len(l)

for f in os.listdir(os.path.join("documentation", "images")):
    documentation["image files"] += 1
    documentation["images"].add(".".join(f.split(".")[0:-1]))



def statistics_to_stdout():
    def print_statistics(headline, data):
        print(headline)
        print("  Number of files                %i" % data["files"])
        print("  Total lines of code            %i" % data["total"])
        print("    source code                  %i" % data["source"])
        print("    comments                     %i" % data["comments"])
        print("    header lines (#! or license) %i" % data["headers"])
        print("    empty lines                  %i" % data["empty"])
        print("    empty lines in comments      %i" % data["emptycomment"])
    print_statistics(headline="Total", data=total)
    for f in statistics:
        print("")
        print_statistics(headline="Folder: " + f, data=statistics[f])
    print("")
    print("Manually written Documentation")
    print("  Number of documentation files      %i" % documentation["files"])
    print("  Number of images                   %i" % len(documentation["images"]))
    print("  Number of image files              %i" % documentation["image files"])
    print("  Lines of documentation             %i" % documentation["lines"])

def statistics_to_html(html_file):
    def print_statistics(s, folder, data):
        s.append("          <tr>")
        s.append("              <td class='subsection' rowspan='6'>" + folder + "</td>")
        s.append("              <td class='text'>Files</td>")
        s.append("              <td class='text'>" + str(data["files"]) + "</td>")
        s.append("              <td class='text'></td>")
        s.append("              <td class='text'></td>")
        s.append("              <td class='text'>" + "%2.2f" % (100.0 * data["files"] / total["files"]) + " %</td>")
        s.append("          </tr>")
        s.append("          <tr>")
        s.append("              <td class='text'>Total</td>")
        s.append("              <td class='text'>" + str(data["total"]) + "</td>")
        s.append("              <td class='text'></td>")
        s.append("              <td class='text'></td>")
        s.append("              <td class='text'>" + "%2.2f" % (100.0 * data["total"] / total["total"]) + " %</td>")
        s.append("          </tr>")
        s.append("          <tr>")
        s.append("              <td class='text'>Source</td>")
        s.append("              <td class='text'>" + str(data["source"]) + "</td>")
        s.append("              <td class='text'>" + "%2.2f" % (100.0 * data["source"] / data["total"]) + " % of lines in " + folder + "</td>")
        s.append("              <td class='text'>" + "%2.2f" % (100.0 * data["source"] / total["source"]) + " % of total source code lines</td>")
        s.append("              <td class='text'>" + "%2.2f" % (100.0 * data["source"] / total["total"]) + " % of total number of lines</td>")
        s.append("          </tr>")
        s.append("          <tr>")
        s.append("              <td class='text'>Comments</td>")
        s.append("              <td class='text'>" + str(data["comments"]) + "</td>")
        s.append("              <td class='text'>" + "%2.2f" % (100.0 * data["comments"] / data["total"]) + " % of lines in " + folder + "</td>")
        s.append("              <td class='text'>" + "%2.2f" % (100.0 * data["comments"] / total["comments"]) + " % of total comment lines</td>")
        s.append("              <td class='text'>" + "%2.2f" % (100.0 * data["comments"] / total["total"]) + " % of total number of lines</td>")
        s.append("          </tr>")
        s.append("          <tr>")
        s.append("              <td class='text'>Headers</td>")
        s.append("              <td class='text'>" + str(data["headers"]) + "</td>")
        s.append("              <td class='text'>" + "%2.2f" % (100.0 * data["headers"] / data["total"]) + " % of lines in " + folder + "</td>")
        s.append("              <td class='text'>" + "%2.2f" % (100.0 * data["headers"] / total["headers"]) + " % of total header lines</td>")
        s.append("              <td class='text'>" + "%2.2f" % (100.0 * data["headers"] / total["total"]) + " % of total number of lines</td>")
        s.append("          </tr>")
        s.append("          <tr>")
        s.append("              <td class='text'>Empty</td>")
        s.append("              <td class='text'>" + str(data["empty"] + data["emptycomment"]) + "</td>")
        s.append("              <td class='text'>" + "%2.2f" % (100.0 * (data["empty"] + data["emptycomment"]) / data["total"]) + " % of lines in " + folder + "</td>")
        s.append("              <td class='text'>" + "%2.2f" % (100.0 * (data["empty"] + data["emptycomment"]) / (total["empty"] + total["emptycomment"])) + " % of total empty lines</td>")
        s.append("              <td class='text'>" + "%2.2f" % (100.0 * (data["empty"] + data["emptycomment"]) / total["total"]) + " % of total number of lines</td>")
        s.append("          </tr>")
    src = []
    src.append("<html>")
    src.append("    <head>")
    src.append("        <title>SuMPF: Statistics</title>")
    src.append("        <link rel='stylesheet' type='text/css' href='style.css' />")
    src.append("        <script type='text/javascript'>")
    src.append("            dont_go_back = true;    // This is needed for the header script at the beginning of the body tag")
    src.append("        </script>")
    src.append("    </head>")
    src.append("    <body>")
    src.append("        <script src='header.js' type='text/javascript'></script>")
    src.append("        <table class='maintable'>")
    src.append("            <tr>")
    src.append("                <th colspan='6' class='headline'>Statistics</th>")
    src.append("            </tr>")
    src.append("            <tr>")
    src.append("                <td colspan='6' class='text'>")
    src.append("                    Some statistics about the source code of SuMPF.<br />")
    src.append("                    This file has been created with the script statistics.py in the tools folder.")
    src.append("                </td>")
    src.append("            </tr>")
    src.append("            <tr>")
    src.append("                <th colspan='6' class='section'>Total</th>")
    src.append("            </tr>")
    src.append("            <tr>")
    src.append("                <td colspan='6' class='text'>")
    src.append("                    <table style='margin-left:auto;margin-right:auto;'>")
    src.append("                        <tr>")
    src.append("                            <td>Number of files</td>")
    src.append("                            <td>" + str(total["files"]) + "</td>")
    src.append("                            <td></td>")
    src.append("                        </tr>")
    src.append("                        <tr>")
    src.append("                            <td>Total lines of code</td>")
    src.append("                            <td>" + str(total["total"]) + "</td>")
    src.append("                            <td></td>")
    src.append("                        </tr>")
    src.append("                        <tr>")
    src.append("                            <td>Source code lines</td>")
    src.append("                            <td>" + str(total["source"]) + "</td>")
    src.append("                            <td>" + "%2.2f" % (100.0 * total["source"] / total["total"]) + " %</td>")
    src.append("                        </tr>")
    src.append("                        <tr>")
    src.append("                            <td>Comment lines and documentation</td>")
    src.append("                            <td>" + str(total["comments"]) + "</td>")
    src.append("                            <td>" + "%2.2f" % (100.0 * total["comments"] / total["total"]) + " %</td>")
    src.append("                        </tr>")
    src.append("                        <tr>")
    src.append("                            <td>License header lines and #!-lines</td>")
    src.append("                            <td>" + str(total["headers"]) + "</td>")
    src.append("                            <td>" + "%2.2f" % (100.0 * total["headers"] / total["total"]) + " %</td>")
    src.append("                        </tr>")
    src.append("                        <tr>")
    src.append("                            <td>Empty lines</td>")
    src.append("                            <td>" + str(total["empty"] + total["emptycomment"]) + "</td>")
    src.append("                            <td>" + "%2.2f" % (100.0 * (total["empty"] + total["emptycomment"]) / total["total"]) + " %</td>")
    src.append("                        </tr>")
    src.append("                    </table>")
    src.append("                </td>")
    src.append("            </tr>")
    src.append("            <tr>")
    src.append("                <th colspan='6' class='section'>Per folder</th>")
    src.append("            </tr>")
    for f in statistics:
        print_statistics(s=src, folder=f, data=statistics[f])
    src.append("            <tr>")
    src.append("                <th colspan='6' class='section'>Manually written documentation</th>")
    src.append("            </tr>")
    src.append("            <tr>")
    src.append("                <td class='subsection' rowspan='2'>Text</td>")
    src.append("                <td class='text'>Files</td>")
    src.append("                <td class='text'>%i</td>" % documentation["files"])
    src.append("                <td class='text' colspan='3'>The number of .htm, .js and .css files in the documentation folder</td>")
    src.append("            </tr>")
    src.append("            <tr>")
    src.append("                <td class='text'>Lines</td>")
    src.append("                <td class='text'>%i</td>" % documentation["lines"])
    src.append("                <td class='text' colspan='3'>The number lines in these files</td>")
    src.append("            </tr>")
    src.append("            <tr>")
    src.append("                <td class='subsection' rowspan='2'>Images</td>")
    src.append("                <td class='text'>Files</td>")
    src.append("                <td class='text'>%i</td>" % documentation["image files"])
    src.append("                <td class='text' colspan='3'>The number of image files, including vector graphics, that have been converted to a .png</td>")
    src.append("            </tr>")
    src.append("            <tr>")
    src.append("                <td class='text'>Images</td>")
    src.append("                <td class='text'>%i</td>" % len(documentation["images"]))
    src.append("                <td class='text' colspan='3'>The number images that are used in the documentation</td>")
    src.append("            </tr>")
    src.append("        </table>")
    src.append("    </body>")
    src.append("</html>")
    path = html_file
    path = os.path.expandvars(path)
    path = os.path.expanduser(path)
    path = os.path.abspath(path)
    path = os.path.normpath(path)
    with open(path, "w") as html_file:
        html_file.write("\n".join(src))

if args.html_file == "":
    statistics_to_stdout()
else:
    statistics_to_html(args.html_file)

