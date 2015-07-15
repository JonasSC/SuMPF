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

import numpy


class XDataManager(object):
    """
    This class is an abstract base class for different XDataManager implementations.
    These classes are meant to be mixed into a LineManager implementation via
    multi-inheritance.
    The purpose of these classes is to provide the static method GetXData, which
    generates the x axis data for the plot.
    """
    @staticmethod
    def GetXData(data_interval, shown_interval, number_of_samples, figure_width):
        """
        Abstract method that creates the x axis data for the plot.
        @param data_interval: the x axis interval, in which the input data is equidistantly sampled
        @param shown_interval: the x axis interval that is actually visible in the plot
        @param number_of_samples: the number of input data samples per channel
        @param figure_width: the width of the plot figure in pixels
        @retval : a list of x data values
        """
        raise NotImplementedError("This method should have been overridden in a derived class")



class XDataManagerNoDownsample(XDataManager):
    """
    This class is meant to be mixed into a LineManager implementation via
    multi-inheritance.
    This class provides an implementation of the static method GetXData, that
    generates the x axis data for the plot without any cropping of the data to
    the visible x axis interval of the plot.
    """
    @staticmethod
    def GetXData(data_interval, shown_interval, number_of_samples, figure_width):
        """
        This method creates the x axis data for the plot. This method does not
        crop the plotted data to the visible interval of the x axis.
        @param data_interval: the x axis interval, in which the input data is equidistantly sampled
        @param shown_interval: the x axis interval that is actually visible in the plot
        @param number_of_samples: the number of input data samples per channel
        @param figure_width: the width of the plot figure in pixels
        @retval : a list of x data values
        """
        data_range = float(data_interval[1] - data_interval[0])
        resolution = data_range / number_of_samples
        return [data_interval[0] + resolution * i for i in range(number_of_samples)]



class XDataManagerCropAndDownsample(XDataManager):
    """
    This class is meant to be mixed into a LineManager implementation via
    multi-inheritance.
    This class provides an implementation of the static method GetXData, that
    generates the x axis data for the plot. If the number of samples of the input
    data is very high, the generated x axis data is cropped to the visible interval
    of the x axis and resampled to an acceptable number of samples. If the number
    of samples is low enough to be plotted directly, no cropping or downsampling
    is performed.
    """
    @staticmethod
    def GetXData(data_interval, shown_interval, number_of_samples, figure_width):
        """
        This method creates the x axis data for the plot. This method crops
        the plotted data to the visible interval of the x axis.
        @param data_interval: the x axis interval, in which the input data is equidistantly sampled
        @param shown_interval: the x axis interval that is actually visible in the plot
        @param number_of_samples: the number of input data samples per channel
        @param figure_width: the width of the plot figure in pixels
        @retval : a list of x data values
        """
        maximum_number_of_samples = figure_width * 50
        desired_number_of_samples = figure_width * 4
        data_range = float(data_interval[1] - data_interval[0])
        shown_range = float(shown_interval[1] - shown_interval[0])
        show_ratio = shown_range / data_range
        resolution = data_range / number_of_samples
        if number_of_samples * show_ratio > maximum_number_of_samples:
            resolution = data_range / desired_number_of_samples
            number_of_samples = desired_number_of_samples
        return [data_interval[0] + resolution * i for i in range(number_of_samples)]



class LineManager(object):
    """
    An abstract base class for other LineManager implementations.
    Instances of derived classes of this take care of the display of one line in
    a plot.
    Derived classes can implement the method _PlotDownsampledData to add automatic
    downsampling functionality to the plots.
    Each instantiatable LineManager class must also inherit from a XDataManager
    implementation to be able to generate the x axis data for the plot.
    """
    def __init__(self, plot, x_data, y_data, interval, label):
        """
        @param plot: the matplotlib.Axes instance in which the managed line shall be plotted
        @param x_data: a sequence of x axis data samples (generated by the XDataManager.GetXData method)
        @param y_data: the complete (non cropped) sequence of y axis data samples for the plotted line
        @param interval: the x axis interval over which the (non cropped) y axis data is sampled
        @param label: the label for the managed line, which is displayed in the legend
        """
        self.__plot = plot
        self.__x_data = x_data
        self.__y_data = y_data
        self.__interval = interval
        self.__label = label
        self.__lines = []
        self.__Plot()

    def HasLine(self, line):
        """
        Returns True, if the given matplotlib line object is managed by this instance.
        @param line: a matplotlib Artist object
        @retval : True if the given object is managed by this instance, False otherwise
        """
        return line in self.__lines

    def Bold(self):
        """
        Displays all managed lines with an increased thickness.
        """
        for l in self.__lines:
            l.set_linewidth(2)

    def Normal(self):
        """
        Displays all managed lines with normal thickness.
        """
        for l in self.__lines:
            l.set_linewidth(1)

    def Delete(self):
        """
        Deletes the line from the plot.
        """
        for i in range(len(self.__lines)):
            index = self.__plot.lines.index(self.__lines[i])
            del self.__plot.lines[index]

    def SetData(self, x_data, y_data, interval, label):
        """
        Changes the data of the line.
        @param x_data: a sequence of x axis data samples (generated by the XDataManager.GetXData method)
        @param y_data: the complete (non cropped) sequence of y axis data samples for the plotted line
        @param interval: the x axis interval over which the (non cropped) y axis data is sampled
        @param label: the label for the managed line, which is displayed in the legend
        """
        self.__x_data = x_data
        self.__y_data = y_data
        self.__interval = interval
        self.__label = label
        self.__Plot()

    def SetXData(self, x_data):
        """
        Changes the x axis of the line without changing other data.
        This method is called for example, when the visible x axis interval has
        changed and the XDataManager.GetXData has generated a different sequence
        of x axis samples.
        @param x_data: a sequence of x axis data samples (generated by the XDataManager.GetXData method)
        """
        self.__x_data = x_data
        self.__Plot()

    def __Plot(self):
        """
        Plots the line or updates the already plotted line.
        Before the actual plotting, this method decides, if the data shall be
        plotted as it is, or if it shall be downsampled.
        """
        if len(self.__x_data) == len(self.__y_data):
            self._PlotLines(x_data=self.__x_data, y_data_list=[self.__y_data])
        else:
            shown_interval = (self.__x_data[0], self.__x_data[-1])
            resolution = float(self.__x_data[0] - self.__x_data[-1]) / len(self.__x_data)
            start_index = int(round((shown_interval[0] - self.__interval[0]) / resolution))
            stop_index = int(round((shown_interval[1] - self.__interval[0]) / resolution)) + 1
            cropped_y_data = self.__y_data[start_index:stop_index]
            self._PlotDownsampledData(x_data=self.__x_data, y_data=cropped_y_data)

    def _PlotLines(self, x_data, y_data_list):
        """
        Method that plots the data as one ore more lines in the same color.
        @param x_data: the x axis data for the plotted data
        @param y_data_list: a list of y axis data sequences. Each sequence in this list will be plotted as an individual line
        """
        color = None
        # replace values of existing lines
        for i in range(min(len(self.__lines), len(y_data_list))):
            line = self.__lines[i]
            line.set_xdata(x_data)
            line.set_ydata(y_data_list[i])
            line.set_label(self.__label)
            color = line.get_color()
        # create new lines if necessary
        for i in range(len(self.__lines), len(y_data_list)):
            line = None
            if color is None:
                line = self.__plot.plot(x_data, y_data_list[i], label=self.__label, picker=True)[0]
                color = line.get_color()
            else:
                line = self.__plot.plot(x_data, y_data_list[i], color=color, picker=True)[0]
            self.__lines.append(line)
        # delete surplus lines
        for i in range(len(y_data_list), len(self.__lines)):
            index = self.__plot.lines.index(self.__lines[i])
            del self.__plot.lines[index]
        del self.__lines[len(y_data_list):]

    def _PlotDownsampledData(self, x_data, y_data):
        """
        Overrides of this method shall downsample the given y axis data and plot
        it.
        @param x_data: the cropped and downsampled x axis data
        @param y_data: the cropped, but not downsampled y axis data
        """
        raise NotImplementedError("This method should have been overridden in a derived class")



class LineManagerNoDownsample(LineManager, XDataManagerNoDownsample):
    """
    Instances of this class plot their data always as it is. It does neither
    a cropping to the visible interval of the x axis, nor a downsampling of the
    plotted data.
    """
    def _PlotDownsampledData(self, x_data, y_data):
        """
        Plots the data without any downsampling.
        @param x_data: the cropped and downsampled x axis data
        @param y_data: the cropped, but not downsampled y axis data
        """
        self._PlotLines(x_data=x_data, y_data_list=[y_data])



class LineManagerDownsampleFFT(LineManager, XDataManagerCropAndDownsample):
    """
    THIS CLASS DOES NOT YIELD ACCEPTABLE RESULTS, SO PLEASE DO NOT USE IT.

    Instances of this class plot a cropped and downsampled version of the input
    data if necessary.
    If the number of samples of the input data is very high, the plotted data is
    cropped to the visible interval of the x axis and resampled to an acceptable
    number of samples. If the number of samples is low enough to be plotted directly,
    no cropping or downsampling is performed.
    The downsampling is done by calculating the fourier transform of the input
    data set, cropping the high frequency coefficients and inversely transforming
    the data back to its original domain.
    """
    def _PlotDownsampledData(self, x_data, y_data):
        """
        Plots the data after downsampling it by cropping high frequency fft
        coefficients.
        @param x_data: the cropped and downsampled x axis data
        @param y_data: the cropped, but not downsampled y axis data
        """
        y_data = numpy.fft.irfft(numpy.fft.rfft(y_data), len(x_data))
        self._PlotLines(x_data=x_data, y_data_list=[y_data])

