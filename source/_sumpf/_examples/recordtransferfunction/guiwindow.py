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

import wx
import wx.lib.masked
import wx.lib.dialogs
import sumpf


class GuiWindow(sumpf.gui.Window):
    def __init__(self, signalchain):
        self.__signalchain = signalchain
        sumpf.gui.Window.__init__(self, parent=None, title="Record Transfer Function")
        # menu
        self.__menubar = wx.MenuBar()
        self.SetMenuBar(self.__menubar)
        self.__AddMenu(parent=self.__menubar,
                       title="Save",
                       items=[("Unprocessed transfer function", self.__SaveUnprocessedTransferFunction),
                              ("Unprocessed impulse response", self.__SaveUnprocessedImpulseResponse),
                              ("Processed transfer function", self.__SaveProcessedTransferFunction),
                              ("Processed impulse response", self.__SaveProcessedImpulseResponse)])
        self.__AddMenu(parent=self.__menubar,
                       title="Load",
                       items=[("Unprocessed transfer function", self.__LoadUnprocessedTransferFunction),
                              ("Unprocessed impulse response", self.__LoadUnprocessedImpulseResponse),
                              ("Processed transfer function", self.__LoadProcessedTransferFunction),
                              ("Processed impulse response", self.__LoadProcessedImpulseResponse)])
        self.__AddMenu(parent=self.__menubar,
                       title="Unload",
                       items=[("Unprocessed transfer function", self.__UnloadUnprocessedTransferFunction),
                              ("Unprocessed impulse response", self.__UnloadUnprocessedImpulseResponse),
                              ("Processed transfer function", self.__UnloadProcessedTransferFunction),
                              ("Processed impulse response", self.__UnloadProcessedImpulseResponse)])
        # sizer
        self.__mainsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.__controlsizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.__mainsizer)
        self.__mainsizer.Add(self.__controlsizer, 0, wx.EXPAND)
        # parameter notebook
        self.__parameter_notebook = wx.Notebook(parent=self)
        self.__controlsizer.Add(self.__parameter_notebook, 1, wx.EXPAND)
        self.__record_panel = wx.Panel(parent=self.__parameter_notebook)
        self.__record_sizer = wx.BoxSizer(wx.VERTICAL)
        self.__record_panel.SetSizer(self.__record_sizer)
        self.__parameter_notebook.AddPage(self.__record_panel, "Recording")
        self.__postprocessing_panel = wx.Panel(parent=self.__parameter_notebook)
        self.__postprocessing_sizer = wx.BoxSizer(wx.VERTICAL)
        self.__postprocessing_panel.SetSizer(self.__postprocessing_sizer)
        self.__parameter_notebook.AddPage(self.__postprocessing_panel, "Post Processing")
        # jack
        self.__jack_sizer = self.__AddStaticBoxSizer(parent=self.__record_panel, sizer=self.__record_sizer, label="JACK Properties")
        self.__jack_update = self.__AddButton(parent=self.__record_panel, sizer=self.__jack_sizer, label="Update port lists", buttontext="Update", function=self.__UpdatePortlists)
        self.__jack_capture = self.__AddChoice(parent=self.__record_panel, sizer=self.__jack_sizer, label="Playback to", choices=[])
        self.__jack_playback = self.__AddChoice(parent=self.__record_panel, sizer=self.__jack_sizer, label="Record from", choices=[])
        self.__UpdatePortlists()
        if sumpf.config.get("capture_port") < len(self.__jack_capture.GetItems()):
            self.__jack_capture.SetSelection(sumpf.config.get("capture_port"))
        if sumpf.config.get("playback_port") < len(self.__jack_playback.GetItems()):
            self.__jack_playback.SetSelection(sumpf.config.get("playback_port"))
        # sweep
        self.__sweep_sizer = self.__AddStaticBoxSizer(parent=self.__record_panel, sizer=self.__record_sizer, label="Sweep properties")
        self.__sweep_duration = self.__AddFloatField(parent=self.__record_panel, sizer=self.__sweep_sizer, label="Duration [s]", value=sumpf.config.get("sweep_duration"))
        self.__sweep_silenceduration = self.__AddFloatField(parent=self.__record_panel, sizer=self.__sweep_sizer, label="Silence [s]", value=sumpf.config.get("silence_duration"))
        self.__sweep_start = self.__AddFloatField(parent=self.__record_panel, sizer=self.__sweep_sizer, label="Start frequency [Hz]", value=sumpf.config.get("sweep_start_frequency"), minimum=0.0001, maximum=self.__signalchain.GetSamplingRate() / 2)
        self.__sweep_stop = self.__AddFloatField(parent=self.__record_panel, sizer=self.__sweep_sizer, label="Stop frequency [Hz]", value=sumpf.config.get("sweep_stop_frequency"), minimum=0.0001, maximum=self.__signalchain.GetSamplingRate() / 2)
        self.__sweep_scale = self.__AddRadioButtons(parent=self.__record_panel, sizer=self.__sweep_sizer, labels=["Linear", "Exponential"], selected="Exponential")
        if not sumpf.config.get("sweep_exponentially"):
            self.__sweep_scale["Linear"].SetValue(True)
        self.__sweep_fade = self.__AddFloatField(parent=self.__record_panel, sizer=self.__sweep_sizer, label="Fade in/out", value=sumpf.config.get("fade_out"), minimum=0.0)
        self.__sweep_amplitude = self.__AddFloatField(parent=self.__record_panel, sizer=self.__sweep_sizer, label="Amplitude", value=sumpf.config.get("amplitude"), minimum=0.0, maximum=1.0)
        self.__sweep_average = self.__AddIntegerField(parent=self.__record_panel, sizer=self.__sweep_sizer, label="Averages", value=sumpf.config.get("averages"), minimum=1)
        # regularization
        self.__regularization_sizer = self.__AddStaticBoxSizer(parent=self.__record_panel, sizer=self.__record_sizer, label="Regularization properties")
        self.__regularization_checkbox = self.__AddCheckbox(parent=self.__record_panel, sizer=self.__regularization_sizer, label="Apply regularization", checked=sumpf.config.get("apply_regularization"), function=self.__OnUpdateRegularization)
        self.__regularization_start = self.__AddFloatField(parent=self.__record_panel, sizer=self.__regularization_sizer, label="Start frequency [Hz]", value=sumpf.config.get("regularization_start_frequency"), minimum=0.0001, maximum=self.__signalchain.GetSamplingRate() / 2)
        self.__regularization_stop = self.__AddFloatField(parent=self.__record_panel, sizer=self.__regularization_sizer, label="Stop frequency [Hz]", value=sumpf.config.get("regularization_stop_frequency"), minimum=0.0001, maximum=self.__signalchain.GetSamplingRate() / 2)
        self.__regularization_transition = self.__AddFloatField(parent=self.__record_panel, sizer=self.__regularization_sizer, label="Transition width [Hz]", value=sumpf.config.get("regularization_transition_width"), minimum=0.0001, maximum=self.__signalchain.GetSamplingRate() / 2)
        self.__regularization_epsilon_max = self.__AddFloatField(parent=self.__record_panel, sizer=self.__regularization_sizer, label="Epsilon max", value=sumpf.config.get("regularization_epsilon"))
        self.__regularization_update = self.__AddButton(parent=self.__record_panel, sizer=self.__regularization_sizer, label="Update regularization", buttontext="Update", function=self.__OnUpdateRegularization)
        if not self.__regularization_checkbox.GetValue():
            self.__regularization_start.Disable()
            self.__regularization_stop.Disable()
            self.__regularization_transition.Disable()
            self.__regularization_epsilon_max.Disable()
            self.__regularization_update.Disable()
        # lowpass filter
        self.__lowpass_sizer = self.__AddStaticBoxSizer(parent=self.__postprocessing_panel, sizer=self.__postprocessing_sizer, label="Lowpass")
        self.__lowpass_checkbox = self.__AddCheckbox(parent=self.__postprocessing_panel, sizer=self.__lowpass_sizer, label="Lowpass filter", checked=sumpf.config.get("apply_lowpass"), function=self.__OnUpdateLowpass)
        self.__lowpass_frequency = self.__AddFloatField(parent=self.__postprocessing_panel, sizer=self.__lowpass_sizer, label="Cutoff Frequency [Hz]", value=sumpf.config.get("lowpass_cutoff_frequency"), minimum=0.0001)
        self.__lowpass_order = self.__AddIntegerField(parent=self.__postprocessing_panel, sizer=self.__lowpass_sizer, label="Order", value=sumpf.config.get("lowpass_order"), minimum=1)
        self.__lowpass_update = self.__AddButton(parent=self.__postprocessing_panel, sizer=self.__lowpass_sizer, label="Update filter", buttontext="Update", function=self.__OnUpdateLowpass)
        if not self.__lowpass_checkbox.GetValue():
            self.__lowpass_frequency.Disable()
            self.__lowpass_order.Disable()
            self.__lowpass_update.Disable()
        # window function
        self.__window_sizer = self.__AddStaticBoxSizer(parent=self.__postprocessing_panel, sizer=self.__postprocessing_sizer, label="Window function")
        self.__window_checkbox = self.__AddCheckbox(parent=self.__postprocessing_panel, sizer=self.__window_sizer, label="Apply window", checked=sumpf.config.get("apply_window"), function=self.__OnUpdateWindow)
        self.__window_functions = {"Bartlett": sumpf.modules.WindowGenerator.Bartlett(),
                                   "Blackman": sumpf.modules.WindowGenerator.Blackman(),
                                   "Hamming": sumpf.modules.WindowGenerator.Hamming(),
                                   "Hanning": sumpf.modules.WindowGenerator.Hanning()}
        self.__window_function = self.__AddChoice(parent=self.__postprocessing_panel, sizer=self.__window_sizer, label="Window function", choices=list(self.__window_functions.keys()))
        self.__window_function.SetStringSelection(sumpf.config.get("window_function"))
        self.__window_start = self.__AddFloatField(parent=self.__postprocessing_panel, sizer=self.__window_sizer, label="Window start [s]", value=sumpf.config.get("window_start"))
        self.__window_stop = self.__AddFloatField(parent=self.__postprocessing_panel, sizer=self.__window_sizer, label="Window stop [s]", value=sumpf.config.get("window_stop"))
        self.__window_update = self.__AddButton(parent=self.__postprocessing_panel, sizer=self.__window_sizer, label="Update window", buttontext="Update", function=self.__OnUpdateWindow)
        if not self.__window_checkbox.GetValue():
            self.__window_function.Disable()
            self.__window_start.Disable()
            self.__window_stop.Disable()
            self.__window_update.Disable()
        # normalization
        self.__normalize_sizer = self.__AddStaticBoxSizer(parent=self.__postprocessing_panel, sizer=self.__postprocessing_sizer, label="Normalization")
        self.__normalize_choice = self.__AddChoice(parent=self.__postprocessing_panel, sizer=self.__normalize_sizer, label="Normalize", choices=["Don't normalize", "to average", "to frequency"], function=self.__OnUpdateNormalize)
        self.__normalize_choice.SetSelection(sumpf.config.get("normalization"))
        self.__normalize_individually = self.__AddCheckbox(parent=self.__postprocessing_panel, sizer=self.__normalize_sizer, label="Normalize individually", checked=sumpf.config.get("normalize_individually"), function=self.__OnUpdateNormalize)
        if self.__normalize_choice.GetSelection() != 1:
            self.__normalize_individually.Disable()
        self.__normalize_frequency = self.__AddFloatField(parent=self.__postprocessing_panel, sizer=self.__normalize_sizer, label="Frequency [Hz]", value=sumpf.config.get("normalization_frequency"))
        if self.__normalize_choice.GetSelection() != 2:
            self.__normalize_frequency.Disable()
        # view
        self.__view_sizer = self.__AddStaticBoxSizer(parent=self.__postprocessing_panel, sizer=self.__postprocessing_sizer, label="View")
        self.__view_showrecent = self.__AddCheckbox(parent=self.__postprocessing_panel, sizer=self.__view_sizer, label="Show recent", checked=True, function=self.__ShowRecent)
        self.__view_showrecent.Disable()
        self.__view_start = self.__AddFloatField(parent=self.__postprocessing_panel, sizer=self.__view_sizer, label="Minimal Frequency [Hz]", value=sumpf.config.get("view_start_frequency"), minimum=0.0001, maximum=self.__signalchain.GetSamplingRate() / 2)
        self.__view_stop = self.__AddFloatField(parent=self.__postprocessing_panel, sizer=self.__view_sizer, label="Maximal Frequency [Hz]", value=sumpf.config.get("view_stop_frequency"), minimum=0.0001, maximum=self.__signalchain.GetSamplingRate() / 2)
        self.__view_update = self.__AddButton(parent=self.__postprocessing_panel, sizer=self.__view_sizer, label="Update View", buttontext="Update", function=self.__UpdateView)
        # control buttons
        self.__start = wx.Button(parent=self, label="Start")
        self.Bind(wx.EVT_BUTTON, self.__Start, self.__start)
        self.__controlsizer.Add(self.__start, 0, wx.ALIGN_BOTTOM | wx.EXPAND)
        self.__keep = wx.Button(parent=self, label="Keep")
        self.__keep.Disable()
        self.Bind(wx.EVT_BUTTON, self.__Keep, self.__keep)
        self.__controlsizer.Add(self.__keep, 0, wx.ALIGN_BOTTOM | wx.EXPAND)
        self.__clear = wx.Button(parent=self, label="Clear")
        self.__clear.Disable()
        self.Bind(wx.EVT_BUTTON, self.__Clear, self.__clear)
        self.__controlsizer.Add(self.__clear, 0, wx.ALIGN_BOTTOM | wx.EXPAND)
        # plots
        self.__plotnotebook = wx.Notebook(parent=self, size=(800, 600))
        self.__recordedtransferfunctionpage = sumpf.modules.SpectrumPlotPanel(parent=self.__plotnotebook, hidden_components=set(["Phase", "ContinuousPhase", "GroupDelay"]))
        self.__plotnotebook.AddPage(self.__recordedtransferfunctionpage, "Recorded Transfer Function")
        self.__recordedimpulseresponsepage = sumpf.modules.SignalPlotPanel(parent=self.__plotnotebook)
        self.__plotnotebook.AddPage(self.__recordedimpulseresponsepage, "Recorded Impulse Response")
        self.__processedtransferfunctionpage = sumpf.modules.SpectrumPlotPanel(parent=self.__plotnotebook, hidden_components=set(["Phase", "ContinuousPhase", "GroupDelay"]))
        self.__plotnotebook.AddPage(self.__processedtransferfunctionpage, "Processed Transfer Function")
        self.__processedimpulseresponsepage = sumpf.modules.SignalPlotPanel(parent=self.__plotnotebook)
        self.__plotnotebook.AddPage(self.__processedimpulseresponsepage, "Processed Impulse Response")
        self.__mainsizer.Add(self.__plotnotebook, 1, wx.EXPAND)
        # status bar
        self.__statusbar = self.CreateStatusBar(3)
        self.__statusbar.SetStatusWidths([-7, -2, -1])
        self.__gauge = sumpf.gui.Gauge(parent=self.__statusbar)
        self.__gauge.AddToStatusBar(statusbar=self.__statusbar, field=2)
        # finish gui initialization
        self.Fit()
        self.Layout()
        # make the connections between signal chain and plots
        sumpf.connect(self.__signalchain.GetUnprocessedTransferFunction, self.__recordedtransferfunctionpage.SetSpectrum)
        sumpf.connect(self.__signalchain.GetUnprocessedImpulseResponse, self.__recordedimpulseresponsepage.SetSignal)
        sumpf.connect(self.__signalchain.GetProcessedTransferFunction, self.__processedtransferfunctionpage.SetSpectrum)
        sumpf.connect(self.__signalchain.GetProcessedImpulseResponse, self.__processedimpulseresponsepage.SetSignal)
        sumpf.connect(self.__signalchain.GetProgress, self.__gauge.SetProgress)
        # finish
        self.__UpdateView()

    def Destroy(self):
        self.__signalchain.Delete()
        sumpf.gui.Window.Destroy(self)

    def __Start(self, event=None):
        # save the excitation parameters to the config
        self.__statusbar.SetStatusText("Storing configuration")
        sumpf.config.set("amplitude", self.__sweep_amplitude.GetValue())
        if self.__sweep_duration.IsEnabled():
            sumpf.config.set("sweep_duration", self.__sweep_duration.GetValue())
            sumpf.config.set("silence_duration", self.__sweep_silenceduration.GetValue())
        sumpf.config.set("sweep_start_frequency", self.__sweep_start.GetValue())
        sumpf.config.set("sweep_stop_frequency", self.__sweep_stop.GetValue())
        sumpf.config.set("sweep_exponentially", self.__sweep_scale["Exponential"].GetValue())
        sumpf.config.set("fade_out", self.__sweep_fade.GetValue())
        sumpf.config.set("averages", self.__sweep_average.GetValue())
        sumpf.config.set("capture_port", self.__jack_capture.GetSelection())
        sumpf.config.set("playback_port", self.__jack_playback.GetSelection())
        # run the record
        self.__statusbar.SetStatusText("Recording transfer function")
        sweep_duration = None
        silence_duration = None
        if self.__sweep_duration.IsEnabled():
            sweep_duration = self.__sweep_duration.GetValue()
            silence_duration = self.__sweep_silenceduration.GetValue()
        capture_port = None
        if self.__jack_capture.GetSelection() < self.__jack_capture.GetCount() - 1:
            capture_port = self.__jack_capture.GetStringSelection()
        playback_port = None
        if self.__jack_playback.GetSelection() < self.__jack_playback.GetCount() - 1:
            playback_port = self.__jack_playback.GetStringSelection()
        self.__signalchain.Start(amplitude=self.__sweep_amplitude.GetValue(),
                                 sweep_duration=sweep_duration,
                                 silence_duration=silence_duration,
                                 start_frequency=self.__sweep_start.GetValue(),
                                 stop_frequency=self.__sweep_stop.GetValue(),
                                 exponential=self.__sweep_scale["Exponential"].GetValue(),
                                 fade=self.__sweep_fade.GetValue(),
                                 averages=self.__sweep_average.GetValue(),
                                 capture_port=capture_port,
                                 playback_port=playback_port)
        # other stuff
        self.__statusbar.SetStatusText("Updating GUI")
        self.__keep.Enable()
        self.__statusbar.SetStatusText("Done")

    def __Keep(self, event=None):
        self.__statusbar.SetStatusText("Asking for a name")
        dlg = wx.TextEntryDialog(parent=self, message="Select a label for the kept channel", caption="Select a label")
        dlg.SetValue("Kept")
        if dlg.ShowModal() == wx.ID_OK:
            self.__statusbar.SetStatusText("Keeping data")
            self.__signalchain.Keep(label=str(dlg.GetValue()))
            self.__statusbar.SetStatusText("Updating GUI")
            self.__sweep_duration.Disable()
            self.__sweep_silenceduration.Disable()
            self.__view_showrecent.Enable()
            self.__clear.Enable()
        dlg.Destroy()
        self.__statusbar.SetStatusText("Done")

    def __Clear(self, event=None):
        self.__statusbar.SetStatusText("Deleting stored data")
        self.__signalchain.Clear()
        self.__statusbar.SetStatusText("Updating GUI")
        if len(self.__signalchain.GetLoadedUnprocessedTransferFunctions()) == 0 and \
           len(self.__signalchain.GetLoadedUnprocessedImpulseResponses()) == 0 and \
           len(self.__signalchain.GetLoadedProcessedTransferFunctions()) == 0 and \
           len(self.__signalchain.GetLoadedProcessedImpulseResponses()) == 0:
            self.__sweep_duration.Enable()
            self.__sweep_silenceduration.Enable()
            self.__view_showrecent.SetValue(True)
            self.__view_showrecent.Disable()
        self.__clear.Disable()
        self.__statusbar.SetStatusText("Done")

    def __UpdatePortlists(self, event=None):
        selected_capture_port = self.__jack_capture.GetStringSelection()
        selected_playback_port = self.__jack_playback.GetStringSelection()
        available_capture_ports = self.__signalchain.GetCapturePorts()
        available_capture_ports.append("Select manually")
        available_playback_ports = self.__signalchain.GetPlaybackPorts()
        available_playback_ports.append("Select manually")
        self.__jack_capture.SetItems(available_capture_ports)
        self.__jack_playback.SetItems(available_playback_ports)
        if selected_capture_port in available_capture_ports:
            self.__jack_capture.SetStringSelection(selected_capture_port)
        else:
            self.__jack_capture.SetSelection(0)
        if selected_playback_port in available_playback_ports:
            self.__jack_playback.SetStringSelection(selected_playback_port)
        else:
            self.__jack_playback.SetSelection(0)

    def __OnUpdateRegularization(self, event=None):
        epsilon_max = 0.0
        self.__statusbar.SetStatusText("Storing configuration")
        sumpf.config.set("apply_regularization", self.__regularization_checkbox.GetValue())
        sumpf.config.set("regularization_start_frequency", self.__regularization_start.GetValue())
        sumpf.config.set("regularization_stop_frequency", self.__regularization_stop.GetValue())
        sumpf.config.set("regularization_transition_width", self.__regularization_transition.GetValue())
        sumpf.config.set("regularization_epsilon", self.__regularization_epsilon_max.GetValue())
        self.__statusbar.SetStatusText("Updating GUI")
        if self.__regularization_checkbox.GetValue():
            epsilon_max = self.__regularization_epsilon_max.GetValue()
            self.__regularization_start.Enable()
            self.__regularization_stop.Enable()
            self.__regularization_transition.Enable()
            self.__regularization_epsilon_max.Enable()
            self.__regularization_update.Enable()
            self.__statusbar.SetStatusText("Applying regularization")
        else:
            self.__regularization_start.Disable()
            self.__regularization_stop.Disable()
            self.__regularization_transition.Disable()
            self.__regularization_epsilon_max.Disable()
            self.__regularization_update.Disable()
            self.__statusbar.SetStatusText("Disabling regularization")
        self.__signalchain.SetRegularization(start_frequency=self.__regularization_start.GetValue(),
                                             stop_frequency=self.__regularization_stop.GetValue(),
                                             transition_width=self.__regularization_transition.GetValue(),
                                             epsilon_max=epsilon_max)
        self.__statusbar.SetStatusText("Done")

    def __OnUpdateLowpass(self, event=None):
        self.__statusbar.SetStatusText("Storing configuration")
        sumpf.config.set("apply_lowpass", self.__lowpass_checkbox.GetValue())
        sumpf.config.set("lowpass_cutoff_frequency", self.__lowpass_frequency.GetValue())
        sumpf.config.set("lowpass_order", self.__lowpass_order.GetValue())
        if self.__lowpass_checkbox.GetValue():
            self.__statusbar.SetStatusText("Applying lowpass filter")
            self.__signalchain.SetLowpass(frequency=self.__lowpass_frequency.GetValue(), order=self.__lowpass_order.GetValue())
            self.__statusbar.SetStatusText("Updating GUI")
            self.__lowpass_frequency.Enable()
            self.__lowpass_order.Enable()
            self.__lowpass_update.Enable()
        else:
            self.__statusbar.SetStatusText("Disabling lowpass filtering")
            self.__signalchain.SetLowpass(None)
            self.__statusbar.SetStatusText("Updating GUI")
            self.__lowpass_frequency.Disable()
            self.__lowpass_order.Disable()
            self.__lowpass_update.Disable()
        self.__statusbar.SetStatusText("Done")

    def __OnUpdateWindow(self, event=None):
        self.__statusbar.SetStatusText("Storing configuration")
        sumpf.config.set("apply_window", self.__window_checkbox.GetValue())
        sumpf.config.set("window_function", self.__window_function.GetStringSelection())
        sumpf.config.set("window_start", self.__window_start.GetValue())
        sumpf.config.set("window_stop", self.__window_stop.GetValue())
        if self.__window_checkbox.GetValue():
            self.__statusbar.SetStatusText("Applying window")
            function = self.__window_functions[self.__window_function.GetStringSelection()]
            interval = (self.__window_start.GetValue(), self.__window_stop.GetValue())
            self.__signalchain.SetWindow(function=function, interval=interval)
            self.__statusbar.SetStatusText("Updating GUI")
            self.__window_function.Enable()
            self.__window_start.Enable()
            self.__window_stop.Enable()
            self.__window_update.Enable()
            self.__recordedimpulseresponsepage.SetCursors(cursors=interval)
        else:
            self.__statusbar.SetStatusText("Disabling window")
            self.__signalchain.SetWindow(function=None)
            self.__statusbar.SetStatusText("Updating GUI")
            self.__window_function.Disable()
            self.__window_start.Disable()
            self.__window_stop.Disable()
            self.__window_update.Disable()
            self.__recordedimpulseresponsepage.SetCursors(cursors=[])
        self.__statusbar.SetStatusText("Done")

    def __OnUpdateNormalize(self, event=None):
        self.__statusbar.SetStatusText("Storing configuration")
        sumpf.config.set("normalization", self.__normalize_choice.GetSelection())
        sumpf.config.set("normalize_individually", self.__normalize_individually.GetValue())
        sumpf.config.set("normalization_frequency", self.__normalize_frequency.GetValue())
        self.__statusbar.SetStatusText("Updating GUI")
        if self.__normalize_choice.GetStringSelection() == "Don't normalize":
            self.__normalize_individually.Disable()
            self.__normalize_frequency.Disable()
            self.__statusbar.SetStatusText("Updating normalization")
            self.__signalchain.SetNormalize(normalize=False)
        elif self.__normalize_choice.GetStringSelection() == "to average":
            self.__normalize_individually.Enable()
            self.__normalize_frequency.Disable()
            self.__statusbar.SetStatusText("Updating normalization")
            self.__signalchain.SetNormalize(normalize="average", individual=self.__normalize_individually.GetValue())
        elif self.__normalize_choice.GetStringSelection() == "to frequency":
            self.__normalize_individually.Disable()
            self.__normalize_frequency.Enable()
            self.__statusbar.SetStatusText("Updating normalization")
            self.__signalchain.SetNormalize(normalize="frequency", frequency=self.__normalize_frequency.GetValue())
        self.__statusbar.SetStatusText("Done")

    def __ShowRecent(self, event=None):
        if self.__view_showrecent.GetValue():
            self.__statusbar.SetStatusText("Showing recent")
            self.__signalchain.ShowRecent(True)
        else:
            self.__statusbar.SetStatusText("Hiding recent")
            self.__signalchain.ShowRecent(False)
        self.__statusbar.SetStatusText("Done")

    def __UpdateView(self, event=None):
        x_interval = (self.__view_start.GetValue(), self.__view_stop.GetValue())
        sumpf.config.set("view_start_frequency", x_interval[0])
        sumpf.config.set("view_stop_frequency", x_interval[1])
        self.__recordedtransferfunctionpage.SetXInterval(x_interval)
        self.__processedtransferfunctionpage.SetXInterval(x_interval)

    ################
    # File methods #
    ################

    def __GetTransferFunctionFileDescriptionForSaving(self):
        self.__statusbar.SetStatusText("Asking for a file")
        wildcard = []
        formats = sumpf.modules.SpectrumFile.GetFormats()
        for f in formats:
            wildcard.append("%s (*.%s)|*.%s" % (f.__name__, f.ending, f.ending))
        dlg = wx.FileDialog(parent=self, defaultFile='TransferFunction', wildcard="|".join(wildcard), style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        filename = None
        format = None
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath()
            format = formats[dlg.GetFilterIndex()]
        dlg.Destroy()
        return filename, format

    def __GetImpulseResponseFileDescriptionForSaving(self):
        self.__statusbar.SetStatusText("Asking for a file")
        wildcard = []
        formats = sumpf.modules.SignalFile.GetFormats()
        for f in formats:
            wildcard.append("%s (*.%s)|*.%s" % (f.__name__, f.ending, f.ending))
        dlg = wx.FileDialog(parent=self, defaultFile='ImpulseResponse', wildcard="|".join(wildcard), style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        filename = None
        format = None
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath()
            format = formats[dlg.GetFilterIndex()]
        dlg.Destroy()
        return filename, format

    def __SaveUnprocessedTransferFunction(self, event=None):
        filename, format = self.__GetTransferFunctionFileDescriptionForSaving()
        if filename is not None:
            self.__statusbar.SetStatusText("Saving data")
            self.__signalchain.SaveUnprocessedTransferFunction(filename=filename, format=format)
        self.__statusbar.SetStatusText("Done")

    def __SaveUnprocessedImpulseResponse(self, event=None):
        filename, format = self.__GetImpulseResponseFileDescriptionForSaving()
        if filename is not None:
            self.__statusbar.SetStatusText("Saving data")
            self.__signalchain.SaveUnprocessedImpulseResponse(filename=filename, format=format)
        self.__statusbar.SetStatusText("Done")

    def __SaveProcessedTransferFunction(self, event=None):
        filename, format = self.__GetTransferFunctionFileDescriptionForSaving()
        if filename is not None:
            self.__statusbar.SetStatusText("Saving data")
            self.__signalchain.SaveProcessedTransferFunction(filename=filename, format=format)
        self.__statusbar.SetStatusText("Done")

    def __SaveProcessedImpulseResponse(self, event=None):
        filename, format = self.__GetImpulseResponseFileDescriptionForSaving()
        if filename is not None:
            self.__statusbar.SetStatusText("Saving data")
            self.__signalchain.SaveProcessedImpulseResponse(filename=filename, format=format)
        self.__statusbar.SetStatusText("Done")

    def __LoadFile(self, method):
        self.__statusbar.SetStatusText("Asking for a file")
        dlg = wx.FileDialog(parent=self, style=wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.__statusbar.SetStatusText("Loading data")
            method(filename=dlg.GetPath())
            self.__sweep_duration.Disable()
            self.__sweep_silenceduration.Disable()
            self.__view_showrecent.Enable()
        dlg.Destroy()
        self.__statusbar.SetStatusText("Done")

    def __LoadUnprocessedTransferFunction(self, event=None):
        self.__LoadFile(method=self.__signalchain.LoadUnprocessedTransferFunction)

    def __LoadUnprocessedImpulseResponse(self, event=None):
        self.__LoadFile(method=self.__signalchain.LoadUnprocessedImpulseResponse)

    def __LoadProcessedTransferFunction(self, event=None):
        self.__LoadFile(method=self.__signalchain.LoadProcessedTransferFunction)

    def __LoadProcessedImpulseResponse(self, event=None):
        self.__LoadFile(method=self.__signalchain.LoadProcessedImpulseResponse)

    def __UnloadFiles(self, method, filelist):
        self.__statusbar.SetStatusText("Asking for a file")
        dlg = wx.lib.dialogs.MultipleChoiceDialog(parent=self, msg="Choose a file", title="Unload", lst=filelist)
        if dlg.ShowModal() == wx.ID_OK:
            self.__statusbar.SetStatusText("Unloading data")
            method(filenames=dlg.GetValueString())
            if len(self.__signalchain.GetLoadedUnprocessedTransferFunctions()) == 0 and \
               len(self.__signalchain.GetLoadedUnprocessedImpulseResponses()) == 0 and \
               len(self.__signalchain.GetLoadedProcessedTransferFunctions()) == 0 and \
               len(self.__signalchain.GetLoadedProcessedImpulseResponses()) == 0:
                if not self.__clear.IsEnabled():
                    self.__sweep_duration.Enable()
                    self.__sweep_silenceduration.Enable()
                    self.__view_showrecent.SetValue(True)
                    self.__view_showrecent.Disable()
        dlg.Destroy()
        self.__statusbar.SetStatusText("Done")

    def __UnloadUnprocessedTransferFunction(self, event=None):
        self.__UnloadFiles(method=self.__signalchain.UnloadUnprocessedTransferFunction,
                           filelist=self.__signalchain.GetLoadedUnprocessedTransferFunctions())

    def __UnloadUnprocessedImpulseResponse(self, event=None):
        self.__UnloadFiles(method=self.__signalchain.UnloadUnprocessedImpulseResponse,
                           filelist=self.__signalchain.GetLoadedUnprocessedImpulseResponses())

    def __UnloadProcessedTransferFunction(self, event=None):
        self.__UnloadFiles(method=self.__signalchain.UnloadProcessedTransferFunction,
                           filelist=self.__signalchain.GetLoadedProcessedTransferFunctions())

    def __UnloadProcessedImpulseResponse(self, event=None):
        self.__UnloadFiles(method=self.__signalchain.UnloadProcessedImpulseResponse,
                           filelist=self.__signalchain.GetLoadedProcessedImpulseResponses())

    ######################
    # GUI helper methods #
    ######################

    def __AddMenu(self, parent, title, items):
        menu = wx.Menu()
        for name, function in items:
            item = menu.Append(id=wx.ID_ANY, text=name)
            self.Bind(wx.EVT_MENU, function, item)
        parent.Append(menu, title)

    def __AddStaticBoxSizer(self, parent, sizer, label):
        box = wx.StaticBox(parent=parent, label=label)
        box_sizer = wx.StaticBoxSizer(box=box, orient=wx.VERTICAL)
        sizer.Add(box_sizer, 0, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
        return box_sizer

    def __AddElement(self, parent, sizer, element, label):
        text = wx.StaticText(parent=parent, label=label)
        rowsizer = wx.GridSizer(1, 2, 1, 1)
        rowsizer.Add(text, 0, wx.ALIGN_CENTER_VERTICAL)
        rowsizer.Add(element, 0, wx.EXPAND)
        sizer.Add(rowsizer, 0, wx.EXPAND)

    def __AddButton(self, parent, sizer, label, buttontext, function):
        element = wx.Button(parent=parent, label=buttontext, style=wx.BU_EXACTFIT)
        element.Bind(wx.EVT_BUTTON, function)
        self.__AddElement(parent, sizer, element, label)
        return element

    def __AddChoice(self, parent, sizer, label, choices, function=None):
        element = wx.Choice(parent=parent, choices=choices, size=(100, -1))
        self.__AddElement(parent, sizer, element, label)
        if function is not None:
            self.Bind(wx.EVT_CHOICE, function, element)
        return element

    def __AddIntegerField(self, parent, sizer, label, value, minimum=None, maximum=None):
        element = wx.lib.masked.NumCtrl(parent=parent, fractionWidth=0, value=value)
        if minimum is not None:
            element.SetMin(minimum)
        if maximum is not None:
            element.SetMax(maximum)
        element.SetLimited(limited=True)
        self.__AddElement(parent, sizer, element, label)
        return element

    def __AddFloatField(self, parent, sizer, label, value, minimum=None, maximum=None):
        element = wx.lib.masked.NumCtrl(parent=parent, fractionWidth=4, value=value)
        if minimum is not None:
            element.SetMin(minimum)
        if maximum is not None:
            element.SetMax(maximum)
        element.SetLimited(limited=True)
        self.__AddElement(parent, sizer, element, label)
        return element

    def __AddCheckbox(self, parent, sizer, label, checked, function=None):
        element = wx.CheckBox(parent=parent)
        element_sizer = wx.BoxSizer(wx.HORIZONTAL)
        element_sizer.AddStretchSpacer()
        element_sizer.Add(element, 0, wx.ALIGN_CENTER_HORIZONTAL)
        element_sizer.AddStretchSpacer()
        element.SetValue(checked)
        if function is not None:
            element.Bind(wx.EVT_CHECKBOX, function)
        self.__AddElement(parent, sizer, element_sizer, label)
        return element

    def __AddRadioButtons(self, parent, sizer, labels, selected):
        rowsizer = wx.BoxSizer(wx.HORIZONTAL)
        elements = {}
        elements[labels[0]] = wx.RadioButton(parent=parent, label=labels[0], style=wx.RB_GROUP)
        rowsizer.Add(elements[labels[0]], 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL)
        for i in range(1, len(labels)):
            elements[labels[i]] = wx.RadioButton(parent=parent, label=labels[i])
            rowsizer.AddStretchSpacer()
            rowsizer.Add(elements[labels[i]], 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL)
        elements[selected].SetValue(True)
        sizer.Add(rowsizer, 0, wx.EXPAND)
        return elements

