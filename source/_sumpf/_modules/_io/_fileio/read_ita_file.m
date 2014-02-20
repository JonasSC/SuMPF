function [samples, samplingrate, domain, names, units] = read_ita_file(filename)

	data = load(filename);

	samples = data.ITA_TOOLBOX_AUDIO_OBJECT.data .* data.ITA_TOOLBOX_AUDIO_OBJECT.dataFactor;
	samplingrate = data.ITA_TOOLBOX_AUDIO_OBJECT.samplingRate;
	domain = data.ITA_TOOLBOX_AUDIO_OBJECT.domain;
	names = data.ITA_TOOLBOX_AUDIO_OBJECT.channelNames;
	units = data.ITA_TOOLBOX_AUDIO_OBJECT.channelUnits;

end;

