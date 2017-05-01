# SuMPF - Sound using a Monkeyforest-like processing framework
# Copyright (C) 2012-2017 Jonas Schulte-Coerne
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
import collections
import inspect
import os
import sumpf

parser = argparse.ArgumentParser(description="Write the javascript file with the data types and the class descriptions for the \"find module\" documentation page.")
parser.add_argument("-f, --file", dest="file", action="store", default="../documentation/findmodule/modules.js", help="The file to which the data shall be written.")
parser.add_argument("-d, --doxygen", dest="doxygen_dir", action="store", default="../doxygen/html", help="The directory where the class documentation from doxygen can be found")
args = parser.parse_args()

imported_modules = {sumpf : "sumpf", collections: "collections"}

def get_class_name(class_object, modules):
    if class_object is not None:
        if class_object.__module__ == "__builtin__":
            return class_object.__name__
        else:
            for m in modules:
                if class_object.__name__ in m.__dict__:
                    return modules[m] + "." + class_object.__name__
            return class_object.__module__ + "." + class_object.__name__
    else:
        return "None"

def get_ancestry(class_object, modules):
    result = []
    for cls in inspect.getmro(class_object)[1:]:
        result.append(get_class_name(class_object=cls, modules=modules))
    return str(result)

namespace = sumpf.modules

types = set()
classes = {}
for item in sumpf.helper.walk_module(namespace):
    path = ""
    for i_module in item[0][1:]:
        path = path + i_module.__name__.split(".")[-1] + "."
    for i_class in item[2]:
        typed_connectors = {sumpf.Output : {}, sumpf.Input : {}, sumpf.MultiInput : {}}
        trigger = 0
        multitype_connectors = [[], [], []]
        for i_superclass in inspect.getmro(i_class):
            attributes = vars(i_superclass)
            for name in attributes:
                connector_type = type(attributes[name])
                if connector_type in typed_connectors.keys():
                    data_type = attributes[name].GetType()
                    if isinstance(data_type, collections.Iterable):
                        index = {sumpf.Output: 0, sumpf.Input: 1, sumpf.MultiInput: 2}
                        types_of_multi = []
                        for single_type in data_type:
                            types.add(single_type)
                            data_type_name = get_class_name(class_object=single_type, modules=imported_modules)
                            types_of_multi.append(data_type_name)
                        multitype_connectors[index[connector_type]].append(types_of_multi)
                    else:
                        types.add(data_type)
                        data_type_name = get_class_name(class_object=data_type, modules=imported_modules)
                        if data_type_name in typed_connectors[connector_type]:
                            typed_connectors[connector_type][data_type_name] += 1
                        else:
                            typed_connectors[connector_type][data_type_name] = 1
                elif isinstance(attributes[name], sumpf.Trigger):
                    trigger += 1
        classname = path + i_class.__name__
        fullpath = inspect.getfile(i_class)
        relpath = fullpath.split(os.path.split(sumpf.__file__)[0] + os.sep)[1].split(".pyc")[0]
        doxygen_file = "class_"
        doxygen_file += relpath.replace(os.sep + "_", "_1_1__").replace(os.sep, "_1_1")
        doxygen_file += "_1_1" + i_class.__name__.replace("_", "__").rstrip(".py")
        doxygen_file += ".html"
        doxygen_link = os.path.join(args.doxygen_dir, doxygen_file)
        classes[classname] = (typed_connectors[sumpf.Output], typed_connectors[sumpf.Input], typed_connectors[sumpf.MultiInput], trigger, multitype_connectors, doxygen_link)

if None in types:
    types.remove(None)
types_dict = {}
for t in types:
    types_dict[get_class_name(class_object=t, modules=imported_modules)] = t
sorted_types = []
tmp = []
for t in types_dict:
    if "." not in t:
        tmp.append(t)
sorted_types.extend(sorted(tmp))
tmp = []
for t in types_dict:
    if t not in sorted_types and types_dict[t] in collections.__dict__.values():
        tmp.append(t)
sorted_types.extend(sorted(tmp))
tmp = []
for t in types_dict:
    if t not in sorted_types and types_dict[t] in sumpf.__dict__.values():
        tmp.append(t)
sorted_types.extend(sorted(tmp))
tmp = []
for t in types_dict:
    if t not in sorted_types:
        tmp.append(t)
sorted_types.extend(sorted(tmp))
types_source = []
types_source.append("var data_types = {'%s': %s," % (sorted_types[0], get_ancestry(class_object=types_dict[sorted_types[0]], modules=imported_modules)))
for t in sorted_types[1:-1]:
    types_source.append("                  '%s': %s," % (t, get_ancestry(class_object=types_dict[t], modules=imported_modules)))
types_source.append("                  '%s': %s};" % (sorted_types[-1], get_ancestry(class_object=types_dict[sorted_types[-1]], modules=imported_modules)))

modules_source = []
for classname in sorted(classes):
    modules_source.append("classes[\"%s\"] = new SumpfModule(%s," % (classname, str(classes[classname][0])))
    modules_source.append("%s                              %s," % (" " * len(classname), str(classes[classname][1])))
    modules_source.append("%s                              %s," % (" " * len(classname), str(classes[classname][2])))
    modules_source.append("%s                              %s," % (" " * len(classname), classes[classname][3]))
    modules_source.append("%s                              %s," % (" " * len(classname), classes[classname][4]))
    modules_source.append("%s                              \"%s\");\n" % (" " * len(classname), classes[classname][5]))

document_source = "\n".join(types_source) + "\n\n\n" + "\n".join(modules_source)
with open(args.file, "w") as docfile:
    docfile.write(document_source)

