var data_types = {'NoneType': ['object'],
                  'bool': ['int', 'object'],
                  'float': ['object'],
                  'function': ['object'],
                  'int': ['object'],
                  'str': ['basestring', 'object'],
                  'tuple': ['object'],
                  'collections.Callable': ['object'],
                  'collections.Iterable': ['object'],
                  'collections.Mapping': ['collections.Sized', 'collections.Iterable', 'collections.Container', 'object'],
                  'collections.Sequence': ['collections.Sized', 'collections.Iterable', 'collections.Container', 'object'],
                  'sumpf.SampleInterval': ['object'],
                  'sumpf.Signal': ['_sumpf._data.channeldata.ChannelData', 'object'],
                  'sumpf.Spectrum': ['_sumpf._data.channeldata.ChannelData', 'object'],
                  'sumpf.ThieleSmallParameters': ['object'],
                  '_sumpf._data.channeldata.ChannelData': ['object'],
                  '_sumpf._modules._generators._signal.noisegenerator.Distribution': ['object'],
                  '_sumpf._modules._generators._signal.sweepgenerator.SweepFunction': ['object'],
                  '_sumpf._modules._generators._signal.windowgenerator.WindowFunction': ['object'],
                  '_sumpf._modules._generators._spectrum.filtergenerator.FilterFunction': ['object'],
                  '_sumpf._modules._io._fileio.fileformat.FileFormat': ['object']};


classes["Add"] = new SumpfModule({'None': 1},
                                 {'None': 2},
                                 {},
                                 0,
                                 [[], [], []],
                                 "../doxygen/html/class__sumpf_1_1__modules_1_1__math_1_1algebra_1_1Add.html");

classes["AdjustSamplingRate"] = new SumpfModule({'sumpf.Signal': 1},
                                                {'float': 1, 'sumpf.Signal': 1},
                                                {},
                                                0,
                                                [[], [], []],
                                                "../doxygen/html/class__sumpf_1_1__modules_1_1__metadata_1_1adjustsamplingrate_1_1AdjustSamplingRate.html");

classes["ApplyFunction"] = new SumpfModule({'None': 1},
                                           {'None': 1, 'collections.Callable': 1},
                                           {},
                                           0,
                                           [[], [], []],
                                           "../doxygen/html/class__sumpf_1_1__modules_1_1__other_1_1applyfunction_1_1ApplyFunction.html");

classes["ArbitrarySignalGenerator"] = new SumpfModule({'sumpf.Signal': 1},
                                                      {'float': 1, 'int': 1, 'collections.Callable': 1, 'str': 1},
                                                      {},
                                                      0,
                                                      [[], [], []],
                                                      "../doxygen/html/class__sumpf_1_1__modules_1_1__generators_1_1__signal_1_1arbitrarysignalgenerator_1_1ArbitrarySignalGenerator.html");

classes["AverageSignals"] = new SumpfModule({'int': 1, 'sumpf.Signal': 1},
                                            {'int': 2, 'sumpf.Signal': 1},
                                            {},
                                            2,
                                            [[], [], []],
                                            "../doxygen/html/class__sumpf_1_1__modules_1_1__math_1_1average_1_1AverageSignals.html");

classes["AverageSpectrums"] = new SumpfModule({'int': 1, 'sumpf.Spectrum': 1},
                                              {'int': 2, 'sumpf.Spectrum': 1},
                                              {},
                                              2,
                                              [[], [], []],
                                              "../doxygen/html/class__sumpf_1_1__modules_1_1__math_1_1average_1_1AverageSpectrums.html");

classes["ChannelDataProperties"] = new SumpfModule({'int': 2, 'float': 2},
                                                   {'int': 2, 'sumpf.Signal': 1, 'float': 2, 'sumpf.Spectrum': 1},
                                                   {},
                                                   0,
                                                   [[], [], []],
                                                   "../doxygen/html/class__sumpf_1_1__modules_1_1__metadata_1_1channeldataproperties_1_1ChannelDataProperties.html");

classes["ClipSignal"] = new SumpfModule({'sumpf.Signal': 1},
                                        {'collections.Iterable': 1, 'sumpf.Signal': 1},
                                        {},
                                        0,
                                        [[], [], []],
                                        "../doxygen/html/class__sumpf_1_1__modules_1_1__normalize_1_1clipsignal_1_1ClipSignal.html");

classes["CompareSignals"] = new SumpfModule({'sumpf.Signal': 1},
                                            {'sumpf.Signal': 2},
                                            {},
                                            0,
                                            [[], [], []],
                                            "../doxygen/html/class__sumpf_1_1__modules_1_1__math_1_1comparesignals_1_1CompareSignals.html");

classes["ConcatenateSignals"] = new SumpfModule({'int': 1, 'sumpf.Signal': 1},
                                                {'sumpf.Signal': 2},
                                                {},
                                                0,
                                                [[], [], []],
                                                "../doxygen/html/class__sumpf_1_1__modules_1_1__channels_1_1concatenatesignals_1_1ConcatenateSignals.html");

classes["ConjugateSpectrum"] = new SumpfModule({'sumpf.Spectrum': 1},
                                               {'sumpf.Spectrum': 1},
                                               {},
                                               0,
                                               [[], [], []],
                                               "../doxygen/html/class__sumpf_1_1__modules_1_1__math_1_1conjugatespectrum_1_1ConjugateSpectrum.html");

classes["ConstantSignalGenerator"] = new SumpfModule({'sumpf.Signal': 1},
                                                     {'int': 1, 'float': 2},
                                                     {},
                                                     0,
                                                     [[], [], []],
                                                     "../doxygen/html/class__sumpf_1_1__modules_1_1__generators_1_1__signal_1_1constantsignalgenerator_1_1ConstantSignalGenerator.html");

classes["ConstantSpectrumGenerator"] = new SumpfModule({'sumpf.Spectrum': 1},
                                                       {'int': 1, 'float': 3},
                                                       {},
                                                       0,
                                                       [[], [], []],
                                                       "../doxygen/html/class__sumpf_1_1__modules_1_1__generators_1_1__spectrum_1_1constantspectrum_1_1ConstantSpectrumGenerator.html");

classes["ConvolveSignals"] = new SumpfModule({'sumpf.Signal': 1},
                                             {'sumpf.Signal': 2, 'str': 1},
                                             {},
                                             0,
                                             [[], [], []],
                                             "../doxygen/html/class__sumpf_1_1__modules_1_1__math_1_1convolvesignals_1_1ConvolveSignals.html");

classes["CopyLabelsToSignal"] = new SumpfModule({'sumpf.Signal': 1},
                                                {'sumpf.Signal': 1, '_sumpf._data.channeldata.ChannelData': 1},
                                                {},
                                                0,
                                                [[], [], []],
                                                "../doxygen/html/class__sumpf_1_1__modules_1_1__metadata_1_1copylabels_1_1CopyLabelsToSignal.html");

classes["CopyLabelsToSpectrum"] = new SumpfModule({'sumpf.Spectrum': 1},
                                                  {'sumpf.Spectrum': 1, '_sumpf._data.channeldata.ChannelData': 1},
                                                  {},
                                                  0,
                                                  [[], [], []],
                                                  "../doxygen/html/class__sumpf_1_1__modules_1_1__metadata_1_1copylabels_1_1CopyLabelsToSpectrum.html");

classes["CopySignalChannels"] = new SumpfModule({'sumpf.Signal': 1},
                                                {'sumpf.Signal': 1},
                                                {},
                                                0,
                                                [[], [['int', '_sumpf._data.channeldata.ChannelData']], []],
                                                "../doxygen/html/class__sumpf_1_1__modules_1_1__channels_1_1copychannels_1_1CopySignalChannels.html");

classes["CopySpectrumChannels"] = new SumpfModule({'sumpf.Spectrum': 1},
                                                  {'sumpf.Spectrum': 1},
                                                  {},
                                                  0,
                                                  [[], [['int', '_sumpf._data.channeldata.ChannelData']], []],
                                                  "../doxygen/html/class__sumpf_1_1__modules_1_1__channels_1_1copychannels_1_1CopySpectrumChannels.html");

classes["CorrelateSignals"] = new SumpfModule({'sumpf.Signal': 1},
                                              {'sumpf.Signal': 2, 'bool': 1, 'str': 1},
                                              {},
                                              0,
                                              [[], [], []],
                                              "../doxygen/html/class__sumpf_1_1__modules_1_1__math_1_1correlatesignals_1_1CorrelateSignals.html");

classes["CreateSampleInterval"] = new SumpfModule({'sumpf.SampleInterval': 1},
                                                  {'bool': 2},
                                                  {},
                                                  0,
                                                  [[], [['int', 'float'], ['int', 'float']], []],
                                                  "../doxygen/html/class__sumpf_1_1__modules_1_1__generators_1_1interval_1_1CreateSampleInterval.html");

classes["CutSignal"] = new SumpfModule({'int': 1, 'sumpf.Signal': 1},
                                       {'int': 1, 'sumpf.SampleInterval': 1, 'sumpf.Signal': 1},
                                       {},
                                       0,
                                       [[], [], []],
                                       "../doxygen/html/class__sumpf_1_1__modules_1_1__channels_1_1cutsignal_1_1CutSignal.html");

classes["DelayFilterGenerator"] = new SumpfModule({'sumpf.Spectrum': 1},
                                                  {'int': 1, 'float': 3},
                                                  {},
                                                  0,
                                                  [[], [], []],
                                                  "../doxygen/html/class__sumpf_1_1__modules_1_1__generators_1_1__spectrum_1_1delayfilter_1_1DelayFilterGenerator.html");

classes["DerivativeSpectrumGenerator"] = new SumpfModule({'sumpf.Spectrum': 1},
                                                         {'int': 1, 'float': 2},
                                                         {},
                                                         0,
                                                         [[], [], []],
                                                         "../doxygen/html/class__sumpf_1_1__modules_1_1__generators_1_1__spectrum_1_1derivativespectrum_1_1DerivativeSpectrumGenerator.html");

classes["DifferentiateSignal"] = new SumpfModule({'sumpf.Signal': 1},
                                                 {'sumpf.Signal': 1, 'collections.Callable': 1},
                                                 {},
                                                 0,
                                                 [[], [], []],
                                                 "../doxygen/html/class__sumpf_1_1__modules_1_1__math_1_1differentiatesignal_1_1DifferentiateSignal.html");

classes["Divide"] = new SumpfModule({'None': 1},
                                    {'None': 2},
                                    {},
                                    0,
                                    [[], [], []],
                                    "../doxygen/html/class__sumpf_1_1__modules_1_1__math_1_1algebra_1_1Divide.html");

classes["DurationToLength"] = new SumpfModule({'int': 1},
                                              {'float': 2, 'bool': 1},
                                              {},
                                              0,
                                              [[], [], []],
                                              "../doxygen/html/class__sumpf_1_1__modules_1_1__metadata_1_1durationtolength_1_1DurationToLength.html");

classes["EnergyDecayCurveFromImpulseResponse"] = new SumpfModule({'sumpf.Signal': 1},
                                                                 {'sumpf.Signal': 1},
                                                                 {},
                                                                 0,
                                                                 [[], [], []],
                                                                 "../doxygen/html/class__sumpf_1_1__modules_1_1__interpretations_1_1energydecaycurvefromimpulseresponse_1_1EnergyDecayCurveFromImpulseResponse.html");

classes["FilterGenerator"] = new SumpfModule({'sumpf.Spectrum': 1},
                                             {'int': 1, '_sumpf._modules._generators._spectrum.filtergenerator.FilterFunction': 1, 'float': 3, 'bool': 1},
                                             {},
                                             0,
                                             [[], [], []],
                                             "../doxygen/html/class__sumpf_1_1__modules_1_1__generators_1_1__spectrum_1_1filtergenerator_1_1FilterGenerator.html");

classes["FindHarmonicImpulseResponse"] = new SumpfModule({'sumpf.Signal': 1},
                                                         {'int': 1, 'sumpf.Signal': 1, 'float': 3},
                                                         {},
                                                         0,
                                                         [[], [], []],
                                                         "../doxygen/html/class__sumpf_1_1__modules_1_1__interpretations_1_1findharmonicimpulseresponse_1_1FindHarmonicImpulseResponse.html");

classes["FindSignalValues"] = new SumpfModule({'tuple': 1},
                                              {'sumpf.SampleInterval': 1, 'sumpf.Signal': 1, 'collections.Callable': 1},
                                              {},
                                              0,
                                              [[], [['collections.Iterable', 'float', 'int']], []],
                                              "../doxygen/html/class__sumpf_1_1__modules_1_1__interpretations_1_1findsignalvalues_1_1FindSignalValues.html");

classes["FourierTransform"] = new SumpfModule({'sumpf.Spectrum': 1},
                                              {'sumpf.Signal': 1},
                                              {},
                                              0,
                                              [[], [], []],
                                              "../doxygen/html/class__sumpf_1_1__modules_1_1__math_1_1fouriertransform_1_1FourierTransform.html");

classes["GetItem"] = new SumpfModule({'None': 1},
                                     {'None': 1},
                                     {},
                                     0,
                                     [[], [['collections.Sequence', 'collections.Mapping']], []],
                                     "../doxygen/html/class__sumpf_1_1__modules_1_1__other_1_1getitem_1_1GetItem.html");

classes["ImpulseGenerator"] = new SumpfModule({'sumpf.Signal': 1},
                                              {'int': 1, 'float': 3},
                                              {},
                                              0,
                                              [[], [], []],
                                              "../doxygen/html/class__sumpf_1_1__modules_1_1__generators_1_1__signal_1_1impulsegenerator_1_1ImpulseGenerator.html");

classes["IntegrateSignal"] = new SumpfModule({'sumpf.Signal': 1},
                                             {'float': 1, 'sumpf.Signal': 1},
                                             {},
                                             0,
                                             [[], [], []],
                                             "../doxygen/html/class__sumpf_1_1__modules_1_1__math_1_1integratesignal_1_1IntegrateSignal.html");

classes["InverseFourierTransform"] = new SumpfModule({'sumpf.Signal': 1},
                                                     {'sumpf.Spectrum': 1},
                                                     {},
                                                     0,
                                                     [[], [], []],
                                                     "../doxygen/html/class__sumpf_1_1__modules_1_1__math_1_1fouriertransform_1_1InverseFourierTransform.html");

classes["LaguerreFilterGenerator"] = new SumpfModule({'sumpf.Spectrum': 1},
                                                     {'int': 2, 'float': 3},
                                                     {},
                                                     0,
                                                     [[], [], []],
                                                     "../doxygen/html/class__sumpf_1_1__modules_1_1__generators_1_1__spectrum_1_1laguerrefilter_1_1LaguerreFilterGenerator.html");

classes["LaguerreFunctionGenerator"] = new SumpfModule({'sumpf.Signal': 1},
                                                       {'int': 3, 'float': 2},
                                                       {},
                                                       0,
                                                       [[], [], []],
                                                       "../doxygen/html/class__sumpf_1_1__modules_1_1__generators_1_1__signal_1_1laguerrefunctiongenerator_1_1LaguerreFunctionGenerator.html");

classes["Level"] = new SumpfModule({'tuple': 1},
                                   {'float': 2, 'sumpf.Signal': 1},
                                   {},
                                   0,
                                   [[], [], []],
                                   "../doxygen/html/class__sumpf_1_1__modules_1_1__math_1_1level_1_1Level.html");

classes["LoadSignal"] = new SumpfModule({'sumpf.Signal': 1, 'bool': 1},
                                        {'bool': 1, 'str': 1},
                                        {},
                                        0,
                                        [[], [], []],
                                        "../doxygen/html/class__sumpf_1_1__modules_1_1__io_1_1__fileio_1_1load_1_1LoadSignal.html");

classes["LoadSpectrum"] = new SumpfModule({'bool': 1, 'sumpf.Spectrum': 1},
                                          {'bool': 1, 'str': 1},
                                          {},
                                          0,
                                          [[], [], []],
                                          "../doxygen/html/class__sumpf_1_1__modules_1_1__io_1_1__fileio_1_1load_1_1LoadSpectrum.html");

classes["LogarithmSignal"] = new SumpfModule({'sumpf.Signal': 1},
                                             {'sumpf.Signal': 1, 'float': 1},
                                             {},
                                             0,
                                             [[], [], []],
                                             "../doxygen/html/class__sumpf_1_1__modules_1_1__math_1_1logarithmsignal_1_1LogarithmSignal.html");

classes["MergeSignals"] = new SumpfModule({'int': 1, 'sumpf.Signal': 1},
                                          {'function': 1, 'int': 1},
                                          {'sumpf.Signal': 1},
                                          1,
                                          [[], [], []],
                                          "../doxygen/html/class__sumpf_1_1__modules_1_1__channels_1_1merge_1_1MergeSignals.html");

classes["MergeSpectrums"] = new SumpfModule({'int': 1, 'sumpf.Spectrum': 1},
                                            {'function': 1, 'int': 1},
                                            {'sumpf.Spectrum': 1},
                                            1,
                                            [[], [], []],
                                            "../doxygen/html/class__sumpf_1_1__modules_1_1__channels_1_1merge_1_1MergeSpectrums.html");

classes["Modulo"] = new SumpfModule({'None': 1},
                                    {'None': 2},
                                    {},
                                    0,
                                    [[], [], []],
                                    "../doxygen/html/class__sumpf_1_1__modules_1_1__math_1_1algebra_1_1Modulo.html");

classes["Multiply"] = new SumpfModule({'None': 1},
                                      {'None': 2},
                                      {},
                                      0,
                                      [[], [], []],
                                      "../doxygen/html/class__sumpf_1_1__modules_1_1__math_1_1algebra_1_1Multipl.html");

classes["NoiseGenerator"] = new SumpfModule({'sumpf.Signal': 1},
                                            {'int': 1, '_sumpf._modules._generators._signal.noisegenerator.Distribution': 1, 'float': 1, 'None': 1},
                                            {},
                                            1,
                                            [[], [], []],
                                            "../doxygen/html/class__sumpf_1_1__modules_1_1__generators_1_1__signal_1_1noisegenerator_1_1NoiseGenerator.html");

classes["NormalizeSignal"] = new SumpfModule({'sumpf.Signal': 1},
                                             {'sumpf.Signal': 1, 'bool': 1},
                                             {},
                                             0,
                                             [[], [], []],
                                             "../doxygen/html/class__sumpf_1_1__modules_1_1__normalize_1_1normalizesignal_1_1NormalizeSignal.html");

classes["NormalizeSpectrumToAverage"] = new SumpfModule({'sumpf.Spectrum': 1},
                                                        {'collections.Iterable': 1, 'float': 1, 'sumpf.Spectrum': 1, 'bool': 1},
                                                        {},
                                                        0,
                                                        [[], [], []],
                                                        "../doxygen/html/class__sumpf_1_1__modules_1_1__normalize_1_1normalizespectrumtoaverage_1_1NormalizeSpectrumToAverage.html");

classes["NormalizeSpectrumToFrequency"] = new SumpfModule({'sumpf.Spectrum': 1},
                                                          {'float': 1, 'sumpf.Spectrum': 1},
                                                          {},
                                                          0,
                                                          [[], [], []],
                                                          "../doxygen/html/class__sumpf_1_1__modules_1_1__normalize_1_1normalizespectrumtofrequency_1_1NormalizeSpectrumToFrequenc.html");

classes["PassThroughSignal"] = new SumpfModule({'sumpf.Signal': 1},
                                               {'sumpf.Signal': 1},
                                               {},
                                               0,
                                               [[], [], []],
                                               "../doxygen/html/class__sumpf_1_1__modules_1_1__routing_1_1passthrough_1_1PassThroughSignal.html");

classes["PassThroughSpectrum"] = new SumpfModule({'sumpf.Spectrum': 1},
                                                 {'sumpf.Spectrum': 1},
                                                 {},
                                                 0,
                                                 [[], [], []],
                                                 "../doxygen/html/class__sumpf_1_1__modules_1_1__routing_1_1passthrough_1_1PassThroughSpectrum.html");

classes["Power"] = new SumpfModule({'None': 1},
                                   {'None': 2},
                                   {},
                                   0,
                                   [[], [], []],
                                   "../doxygen/html/class__sumpf_1_1__modules_1_1__math_1_1algebra_1_1Power.html");

classes["RectangleFilterGenerator"] = new SumpfModule({'sumpf.Spectrum': 1},
                                                      {'int': 1, 'float': 4, 'bool': 1},
                                                      {},
                                                      0,
                                                      [[], [], []],
                                                      "../doxygen/html/class__sumpf_1_1__modules_1_1__generators_1_1__spectrum_1_1rectanglefilter_1_1RectangleFilterGenerator.html");

classes["RectifySignal"] = new SumpfModule({'sumpf.Signal': 1},
                                           {'sumpf.Signal': 1},
                                           {},
                                           0,
                                           [[], [], []],
                                           "../doxygen/html/class__sumpf_1_1__modules_1_1__math_1_1rectifysignal_1_1RectifySignal.html");

classes["RegularizedSpectrumInversion"] = new SumpfModule({'sumpf.Spectrum': 1},
                                                          {'int': 1, 'float': 3, 'sumpf.Spectrum': 1},
                                                          {},
                                                          0,
                                                          [[], [], []],
                                                          "../doxygen/html/class__sumpf_1_1__modules_1_1__interpretations_1_1regularizedspectruminversion_1_1RegularizedSpectrumInversion.html");

classes["RelabelSignal"] = new SumpfModule({'sumpf.Signal': 1},
                                           {'collections.Iterable': 1, 'sumpf.Signal': 1},
                                           {},
                                           0,
                                           [[], [], []],
                                           "../doxygen/html/class__sumpf_1_1__modules_1_1__metadata_1_1relabel_1_1RelabelSignal.html");

classes["RelabelSpectrum"] = new SumpfModule({'sumpf.Spectrum': 1},
                                             {'collections.Iterable': 1, 'sumpf.Spectrum': 1},
                                             {},
                                             0,
                                             [[], [], []],
                                             "../doxygen/html/class__sumpf_1_1__modules_1_1__metadata_1_1relabel_1_1RelabelSpectrum.html");

classes["RepeatSignal"] = new SumpfModule({'sumpf.Signal': 1},
                                          {'int': 1, 'sumpf.Signal': 1},
                                          {},
                                          0,
                                          [[], [], []],
                                          "../doxygen/html/class__sumpf_1_1__modules_1_1__channels_1_1repeatsignal_1_1RepeatSignal.html");

classes["ResampleSignal"] = new SumpfModule({'sumpf.Signal': 1},
                                            {'int': 1, 'float': 1, 'sumpf.Signal': 1},
                                            {},
                                            0,
                                            [[], [], []],
                                            "../doxygen/html/class__sumpf_1_1__modules_1_1__math_1_1resamplesignal_1_1ResampleSignal.html");

classes["ReverseSignal"] = new SumpfModule({'sumpf.Signal': 1},
                                           {'sumpf.Signal': 1},
                                           {},
                                           0,
                                           [[], [], []],
                                           "../doxygen/html/class__sumpf_1_1__modules_1_1__channels_1_1reversesignal_1_1ReverseSignal.html");

classes["RootMeanSquare"] = new SumpfModule({'sumpf.Signal': 1},
                                            {'sumpf.Signal': 1, 'float': 1},
                                            {},
                                            0,
                                            [[], [], []],
                                            "../doxygen/html/class__sumpf_1_1__modules_1_1__math_1_1rootmeansquare_1_1RootMeanSquare.html");

classes["RudinShapiroNoiseGenerator"] = new SumpfModule({'int': 1, 'sumpf.Signal': 1},
                                                        {'int': 1, 'float': 2},
                                                        {},
                                                        0,
                                                        [[], [['float', 'NoneType']], []],
                                                        "../doxygen/html/class__sumpf_1_1__modules_1_1__generators_1_1__signal_1_1rudinshapiro_noisegenerator_1_1RudinShapiroNoiseGenerator.html");

classes["SaveSignal"] = new SumpfModule({},
                                        {'_sumpf._modules._io._fileio.fileformat.FileFormat': 1, 'sumpf.Signal': 1, 'str': 1},
                                        {},
                                        0,
                                        [[], [], []],
                                        "../doxygen/html/class__sumpf_1_1__modules_1_1__io_1_1__fileio_1_1save_1_1SaveSignal.html");

classes["SaveSpectrum"] = new SumpfModule({},
                                          {'_sumpf._modules._io._fileio.fileformat.FileFormat': 1, 'sumpf.Spectrum': 1, 'str': 1},
                                          {},
                                          0,
                                          [[], [], []],
                                          "../doxygen/html/class__sumpf_1_1__modules_1_1__io_1_1__fileio_1_1save_1_1SaveSpectrum.html");

classes["SelectSignal"] = new SumpfModule({'sumpf.Signal': 1},
                                          {'int': 1, 'sumpf.Signal': 2},
                                          {},
                                          0,
                                          [[], [], []],
                                          "../doxygen/html/class__sumpf_1_1__modules_1_1__routing_1_1select_1_1SelectSignal.html");

classes["SelectSpectrum"] = new SumpfModule({'sumpf.Spectrum': 1},
                                            {'int': 1, 'sumpf.Spectrum': 2},
                                            {},
                                            0,
                                            [[], [], []],
                                            "../doxygen/html/class__sumpf_1_1__modules_1_1__routing_1_1select_1_1SelectSpectrum.html");

classes["ShiftSignal"] = new SumpfModule({'sumpf.Signal': 1},
                                         {'int': 1, 'sumpf.Signal': 1, 'bool': 1},
                                         {},
                                         0,
                                         [[], [], []],
                                         "../doxygen/html/class__sumpf_1_1__modules_1_1__channels_1_1shiftsignal_1_1ShiftSignal.html");

classes["ShortFourierTransform"] = new SumpfModule({'sumpf.Spectrum': 1},
                                                   {'sumpf.Signal': 2},
                                                   {},
                                                   0,
                                                   [[], [['int', 'float']], []],
                                                   "../doxygen/html/class__sumpf_1_1__modules_1_1__math_1_1shortfouriertransform_1_1ShortFourierTransform.html");

classes["SignalEnvelope"] = new SumpfModule({'sumpf.Signal': 1},
                                            {'float': 2, 'int': 1, 'sumpf.Signal': 1},
                                            {},
                                            0,
                                            [[], [], []],
                                            "../doxygen/html/class__sumpf_1_1__modules_1_1__interpretations_1_1signalenvelope_1_1SignalEnvelope.html");

classes["SignalMaximum"] = new SumpfModule({'float': 1, 'tuple': 1},
                                           {'sumpf.Signal': 1},
                                           {},
                                           0,
                                           [[], [], []],
                                           "../doxygen/html/class__sumpf_1_1__modules_1_1__interpretations_1_1minmax_1_1SignalMaximum.html");

classes["SignalMaximumChannel"] = new SumpfModule({'sumpf.Signal': 1},
                                                  {'sumpf.Signal': 1},
                                                  {},
                                                  0,
                                                  [[], [], []],
                                                  "../doxygen/html/class__sumpf_1_1__modules_1_1__interpretations_1_1signal_minmax_channel_1_1SignalMaximumChannel.html");

classes["SignalMean"] = new SumpfModule({'tuple': 1},
                                        {'sumpf.Signal': 1},
                                        {},
                                        0,
                                        [[], [], []],
                                        "../doxygen/html/class__sumpf_1_1__modules_1_1__math_1_1__statistics_1_1mean_1_1SignalMean.html");

classes["SignalMinimum"] = new SumpfModule({'float': 1, 'tuple': 1},
                                           {'sumpf.Signal': 1},
                                           {},
                                           0,
                                           [[], [], []],
                                           "../doxygen/html/class__sumpf_1_1__modules_1_1__interpretations_1_1minmax_1_1SignalMinimum.html");

classes["SignalMinimumChannel"] = new SumpfModule({'sumpf.Signal': 1},
                                                  {'sumpf.Signal': 1},
                                                  {},
                                                  0,
                                                  [[], [], []],
                                                  "../doxygen/html/class__sumpf_1_1__modules_1_1__interpretations_1_1signal_minmax_channel_1_1SignalMinimumChannel.html");

classes["SignalVariance"] = new SumpfModule({'tuple': 1},
                                            {'sumpf.Signal': 1},
                                            {},
                                            0,
                                            [[], [], []],
                                            "../doxygen/html/class__sumpf_1_1__modules_1_1__math_1_1__statistics_1_1signalvariance_1_1SignalVariance.html");

classes["SineWaveGenerator"] = new SumpfModule({'sumpf.Signal': 1},
                                               {'int': 1, 'float': 4},
                                               {},
                                               0,
                                               [[], [], []],
                                               "../doxygen/html/class__sumpf_1_1__modules_1_1__generators_1_1__signal_1_1sinewavegenerator_1_1SineWaveGenerator.html");

classes["SlopeSpectrumGenerator"] = new SumpfModule({'sumpf.Spectrum': 1},
                                                    {'int': 1, 'float': 4},
                                                    {},
                                                    0,
                                                    [[], [], []],
                                                    "../doxygen/html/class__sumpf_1_1__modules_1_1__generators_1_1__spectrum_1_1slopespectrum_1_1SlopeSpectrumGenerator.html");

classes["SpectrumAsSignal"] = new SumpfModule({'sumpf.Signal': 1},
                                              {'int': 1, 'sumpf.Spectrum': 1},
                                              {},
                                              0,
                                              [[], [], []],
                                              "../doxygen/html/class__sumpf_1_1__modules_1_1__other_1_1spectrumassignal_1_1SpectrumAsSignal.html");

classes["SpectrumMaximum"] = new SumpfModule({'float': 1, 'tuple': 1},
                                             {'int': 1, 'sumpf.Spectrum': 1},
                                             {},
                                             0,
                                             [[], [], []],
                                             "../doxygen/html/class__sumpf_1_1__modules_1_1__interpretations_1_1minmax_1_1SpectrumMaximum.html");

classes["SpectrumMaximumChannel"] = new SumpfModule({'sumpf.Spectrum': 1},
                                                    {'int': 1, 'sumpf.Spectrum': 1},
                                                    {},
                                                    0,
                                                    [[], [], []],
                                                    "../doxygen/html/class__sumpf_1_1__modules_1_1__interpretations_1_1spectrum_minmax_channel_1_1SpectrumMaximumChannel.html");

classes["SpectrumMean"] = new SumpfModule({'tuple': 1},
                                          {'sumpf.Spectrum': 1},
                                          {},
                                          0,
                                          [[], [], []],
                                          "../doxygen/html/class__sumpf_1_1__modules_1_1__math_1_1__statistics_1_1mean_1_1SpectrumMean.html");

classes["SpectrumMinimum"] = new SumpfModule({'float': 1, 'tuple': 1},
                                             {'int': 1, 'sumpf.Spectrum': 1},
                                             {},
                                             0,
                                             [[], [], []],
                                             "../doxygen/html/class__sumpf_1_1__modules_1_1__interpretations_1_1minmax_1_1SpectrumMinimum.html");

classes["SpectrumMinimumChannel"] = new SumpfModule({'sumpf.Spectrum': 1},
                                                    {'int': 1, 'sumpf.Spectrum': 1},
                                                    {},
                                                    0,
                                                    [[], [], []],
                                                    "../doxygen/html/class__sumpf_1_1__modules_1_1__interpretations_1_1spectrum_minmax_channel_1_1SpectrumMinimumChannel.html");

classes["SpectrumVariance"] = new SumpfModule({'tuple': 1},
                                              {'sumpf.Spectrum': 1},
                                              {},
                                              0,
                                              [[], [], []],
                                              "../doxygen/html/class__sumpf_1_1__modules_1_1__math_1_1__statistics_1_1spectrumvariance_1_1SpectrumVariance.html");

classes["SplitSignal"] = new SumpfModule({'int': 1, 'sumpf.Signal': 1},
                                         {'int': 1, 'sumpf.Signal': 1, 'tuple': 1},
                                         {},
                                         1,
                                         [[], [], []],
                                         "../doxygen/html/class__sumpf_1_1__modules_1_1__channels_1_1split_1_1SplitSignal.html");

classes["SplitSpectrum"] = new SumpfModule({'int': 1, 'sumpf.Spectrum': 1},
                                           {'int': 1, 'sumpf.Spectrum': 1, 'tuple': 1},
                                           {},
                                           1,
                                           [[], [], []],
                                           "../doxygen/html/class__sumpf_1_1__modules_1_1__channels_1_1split_1_1SplitSpectrum.html");

classes["SquareWaveGenerator"] = new SumpfModule({'sumpf.Signal': 1},
                                                 {'int': 1, 'float': 5},
                                                 {},
                                                 0,
                                                 [[], [], []],
                                                 "../doxygen/html/class__sumpf_1_1__modules_1_1__generators_1_1__signal_1_1squarewavegenerator_1_1SquareWaveGenerator.html");

classes["Subtract"] = new SumpfModule({'None': 1},
                                      {'None': 2},
                                      {},
                                      0,
                                      [[], [], []],
                                      "../doxygen/html/class__sumpf_1_1__modules_1_1__math_1_1algebra_1_1Subtract.html");

classes["SumSignals"] = new SumpfModule({'sumpf.Signal': 1},
                                        {'int': 1},
                                        {'sumpf.Signal': 1},
                                        1,
                                        [[], [], []],
                                        "../doxygen/html/class__sumpf_1_1__modules_1_1__math_1_1sumchanneldata_1_1SumSignals.html");

classes["SumSpectrums"] = new SumpfModule({'sumpf.Spectrum': 1},
                                          {'int': 1},
                                          {'sumpf.Spectrum': 1},
                                          1,
                                          [[], [], []],
                                          "../doxygen/html/class__sumpf_1_1__modules_1_1__math_1_1sumchanneldata_1_1SumSpectrums.html");

classes["SweepGenerator"] = new SumpfModule({'sumpf.Signal': 1},
                                            {'float': 3, 'int': 1, 'sumpf.SampleInterval': 1, '_sumpf._modules._generators._signal.sweepgenerator.SweepFunction': 1},
                                            {},
                                            0,
                                            [[], [], []],
                                            "../doxygen/html/class__sumpf_1_1__modules_1_1__generators_1_1__signal_1_1sweepgenerator_1_1SweepGenerator.html");

classes["ThieleSmallParameterAuralizationLinear"] = new SumpfModule({'sumpf.Signal': 5},
                                                                    {'sumpf.Signal': 1, 'float': 2, 'sumpf.ThieleSmallParameters': 1},
                                                                    {},
                                                                    0,
                                                                    [[], [], []],
                                                                    "../doxygen/html/class__sumpf_1_1__modules_1_1__models_1_1__thielesmallparameters_1_1auralization_linear_1_1ThieleSmallParameterAuralizationLinear.html");

classes["ThieleSmallParameterAuralizationNonlinear"] = new SumpfModule({'sumpf.Signal': 5},
                                                                       {'sumpf.Signal': 1, 'float': 4, 'bool': 2, 'sumpf.ThieleSmallParameters': 1},
                                                                       {},
                                                                       1,
                                                                       [[], [], []],
                                                                       "../doxygen/html/class__sumpf_1_1__modules_1_1__models_1_1__thielesmallparameters_1_1auralization_nonlinear_1_1ThieleSmallParameterAuralizationNonlinear.html");

classes["ThieleSmallParameterInterpretation"] = new SumpfModule({'float': 16, 'sumpf.ThieleSmallParameters': 1},
                                                                {'float': 18, 'sumpf.ThieleSmallParameters': 1},
                                                                {},
                                                                0,
                                                                [[], [], []],
                                                                "../doxygen/html/class__sumpf_1_1__modules_1_1__models_1_1__thielesmallparameters_1_1interpretation_1_1ThieleSmallParameterInterpretation.html");

classes["TriangleWaveGenerator"] = new SumpfModule({'sumpf.Signal': 1},
                                                   {'int': 1, 'float': 5},
                                                   {},
                                                   0,
                                                   [[], [], []],
                                                   "../doxygen/html/class__sumpf_1_1__modules_1_1__generators_1_1__signal_1_1trianglewavegenerator_1_1TriangleWaveGenerator.html");

classes["WeightingFilterGenerator"] = new SumpfModule({'sumpf.Spectrum': 1},
                                                      {'float': 2, 'int': 1, 'collections.Callable': 1},
                                                      {},
                                                      0,
                                                      [[], [], []],
                                                      "../doxygen/html/class__sumpf_1_1__modules_1_1__generators_1_1__spectrum_1_1weightingfilter_1_1WeightingFilterGenerator.html");

classes["WindowGenerator"] = new SumpfModule({'sumpf.Signal': 1},
                                             {'float': 1, 'int': 1, 'sumpf.SampleInterval': 2, '_sumpf._modules._generators._signal.windowgenerator.WindowFunction': 1},
                                             {},
                                             0,
                                             [[], [], []],
                                             "../doxygen/html/class__sumpf_1_1__modules_1_1__generators_1_1__signal_1_1windowgenerator_1_1WindowGenerator.html");

classes["audioio.DummyIO"] = new SumpfModule({'sumpf.Signal': 1, 'float': 1},
                                             {'int': 1, 'sumpf.Signal': 1, 'float': 1},
                                             {},
                                             1,
                                             [[], [], []],
                                             "../doxygen/html/class__sumpf_1_1__modules_1_1__io_1_1__audioio_1_1dummyio_1_1DummyIO.html");
