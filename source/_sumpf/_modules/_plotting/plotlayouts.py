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

import math
from matplotlib.ticker import MaxNLocator


class PlotLayout(object):
    """
    Abstract base class for different plot layouts.
    """
    @staticmethod
    def FormatData(data, labels, components):
        """
        Overrides of this static method shall sort the input data and labels into
        a data structure that is the same as the one for the plots:
        data[GROUP][COMPONENT] = list_of_sequences (one sequence per line)
        labels[GROUP][COMPONENT] = list_of_labels
        data and labels are lists, data[GROUP] and labels[GROUP] are dictionaries.
        @param data: a dict of input the data: input_data[component] = list_of_sequences (one sequence per channel)
        @param labels: a list of labels, one for each channel. A label can be either a string or None
        @param components: a list of component names in the order in which they shall be displayed from top to bottom
        @retval : a tuple of (data, labels), where data and labels are data structures as described above
        """
        raise NotImplementedError("This method should have been overridden in a derived class")

    @staticmethod
    def CreatePlots(figure, data, components, margin, x_caption):
        """
        Overrides of this methods shall create plots and return them in a data
        structure like the following:
        plots[GROUP][COMPONENT] = matplotlib.Axes instance
        plots is a list, plots[GROUP] is a dictionary.
        @param figure: the figure in which the plots shall be created
        @param data: the data that shall be plotted (sorted by FormatData)
        @param components: a list of component names in the order in which they shall be displayed from top to bottom
        @param margin: the margin between the plots and the border of the figure
        @param x_caption: the caption for the x axis
        @retval : the plots in a data structure like described above
        """
        raise NotImplementedError("This method should have been overridden in a derived class")



class PlotLayout_OnePlot(PlotLayout):
    """
    This Layout Plots all channels of the input data in one plot. Each component
    has a separate plot.
    """
    @staticmethod
    def FormatData(data, labels, components):
        """
        Static method that sorts the input data and labels into a data structure
        that is the same as the one for the plots:
        data[GROUP][COMPONENT] = list_of_sequences (one sequence per line)
        labels[GROUP][COMPONENT] = list_of_labels
        data and labels are lists, data[GROUP] and labels[GROUP] are dictionaries.
        @param data: a dict of input the data: input_data[component] = list_of_sequences (one sequence per channel)
        @param labels: a list of labels, one for each channel. A label can be either a string or None
        @param components: a list of component names in the order in which they shall be displayed from top to bottom
        @retval : a tuple of (data, labels), where data and labels are data structures as described above
        """
        data_dict = data
        labels_dict = {components[0]: labels}
        for c in components[1:]:
            labels_dict[c] = (None,) * len(labels)
        return [data_dict], [labels_dict]

    @staticmethod
    def CreatePlots(figure, data, components, margin, x_caption):
        """
        Static method that creates plots and returns them in a data structure
        like the following:
        plots[GROUP][COMPONENT] = matplotlib.Axes instance
        plots is a list, plots[GROUP] is a dictionary.
        @param figure: the figure in which the plots shall be created
        @param data: the data that shall be plotted (sorted by FormatData)
        @param components: a list of component names in the order in which they shall be displayed from top to bottom
        @param margin: the margin between the plots and the border of the figure
        @param x_caption: the caption for the x axis
        @retval : the plots in a data structure like described above
        """
        number_of_shown_components = len(components)
        plots = {}
        width = 1.0 - 2.0 * margin
        height = (1.0 - margin) / number_of_shown_components - margin / 2.0
        left = 1.3 * margin
        for c in components:
            bottom = margin + (number_of_shown_components - 1.0) * (height + margin / 2.0)
            number_of_shown_components -= 1
            plots[c] = figure.add_axes([left, bottom, width, height])
            plots[c].set_ylabel(c)
        plots[components[-1]].set_xlabel(x_caption)
        return [plots]



class PlotLayout_Tiled(PlotLayout):
    """
    Abstract class that creates one group of plots for each channel of the input
    data. Each group of plots consists of one plot per component.
    Derived classes of this differ in the way, the groups are layouted in rows
    and columns.
    """
    @staticmethod
    def FormatData(data, labels, components):
        """
        Static method that sorts the input data and labels into a data structure
        that is the same as the one for the plots:
        data[GROUP][COMPONENT] = list_of_sequences (one sequence per line)
        labels[GROUP][COMPONENT] = list_of_labels
        data and labels are lists, data[GROUP] and labels[GROUP] are dictionaries.
        @param data: a dict of input the data: input_data[component] = list_of_sequences (one sequence per channel)
        @param labels: a list of labels, one for each channel. A label can be either a string or None
        @param components: a list of component names in the order in which they shall be displayed from top to bottom
        @retval : a tuple of (data, labels), where data and labels are data structures as described above
        """
        data_list = []
        labels_list = []
        for i in range(len(data[components[0]])):
            tmp_data = {components[0]: [data[components[0]][i]]}
            tmp_labels = {components[0]: [labels[i]]}
            for c in components[1:]:
                tmp_data[c] = [data[c][i]]
                tmp_labels[c] = [None]
            data_list.append(tmp_data)
            labels_list.append(tmp_labels)
        return data_list, labels_list

    @classmethod
    def CreatePlots(cls, figure, data, components, margin, x_caption):
        """
        Static method that creates plots and returns them in a data structure
        like the following:
        plots[GROUP][COMPONENT] = matplotlib.Axes instance
        plots is a list, plots[GROUP] is a dictionary.
        @param figure: the figure in which the plots shall be created
        @param data: the data that shall be plotted (sorted by FormatData)
        @param components: a list of component names in the order in which they shall be displayed from top to bottom
        @param margin: the margin between the plots and the border of the figure
        @param x_caption: the caption for the x axis
        @retval : the plots in a data structure like described above
        """
        number_of_plots = len(data[components[0]])
        number_of_shown_components = len(components)
        rows, cols = cls._GetRowsAndColumns(number_of_plots)
        width = (1.0 - margin) / float(cols) - margin
        height = (1.0 - margin) / float(rows) - margin
        subheight = height / number_of_shown_components
        plots = []
        for i in range(number_of_plots):
            plotgroup = {}
            left = 1.3 * margin + (i % cols) * (width + margin)
            bottom = margin + (rows - i // cols - 1) * (height + margin)
            offset = number_of_shown_components - 1
            plot = None
            for c in components:
                subbottom = bottom + subheight * offset
                plot = figure.add_axes([left, subbottom, width, subheight])
                offset -= 1
                plot.get_xaxis().set_visible(False)
                plot.set_ylabel(c)
                plot.yaxis.set_major_locator(MaxNLocator(prune='upper'))
                plotgroup[c] = plot
            plot.set_xlabel(x_caption)
            plot.get_xaxis().set_visible(True)
            plots.append(plotgroup)
        return plots

    @classmethod
    def _GetRowsAndColumns(cls, number_of_plots):
        """
        Overrides of this classmethod shall return the number of rows and columns
        to which the plots are distributed.
        @param number_of_plots: the number of plots that shall be distributed
        @retval : a tuple (rows, cols)
        """
        raise NotImplementedError("This method should have been overridden in a derived class")



class PlotLayout_HorizontallyTiled(PlotLayout_Tiled):
    """
    A PlotLayout class that creates one group of plots for each channel of the
    input data. Each group of plots consists of one plot per component.
    This class tries to create a square of plot groups. When the number of plots
    requires the layout to be a rectangle, this rectangle will have more columns
    than rows.
    """
    @classmethod
    def _GetRowsAndColumns(cls, number_of_plots):
        """
        This classmethod returns the number of rows and columns to which the plots
        are distributed.
        @param number_of_plots: the number of plots that shall be distributed
        @retval : a tuple (rows, cols)
        """
        cols = int(math.ceil(number_of_plots ** 0.5))
        rows = int(math.ceil(number_of_plots / float(cols)))
        return rows, cols



class PlotLayout_VerticallyTiled(PlotLayout_Tiled):
    """
    A PlotLayout class that creates one group of plots for each channel of the
    input data. Each group of plots consists of one plot per component.
    This class tries to create a square of plot groups. When the number of plots
    requires the layout to be a rectangle, this rectangle will have more rows than
    columns.
    """
    @classmethod
    def _GetRowsAndColumns(cls, number_of_plots):
        """
        This classmethod returns the number of rows and columns to which the plots
        are distributed.
        @param number_of_plots: the number of plots that shall be distributed
        @retval : a tuple (rows, cols)
        """
        rows = int(math.ceil(number_of_plots ** 0.5))
        cols = int(math.ceil(number_of_plots / float(rows)))
        return rows, cols

