function [samples, samplingrate, domain, names, units] = read_ita_file(filename)

	data = load(filename);

	samples = data.ITA_TOOLBOX_AUDIO_OBJECT.data .* data.ITA_TOOLBOX_AUDIO_OBJECT.dataFactor;
	samplingrate = data.ITA_TOOLBOX_AUDIO_OBJECT.samplingRate;
	domain = data.ITA_TOOLBOX_AUDIO_OBJECT.domain;
	names = data.ITA_TOOLBOX_AUDIO_OBJECT.channelNames;
	units = data.ITA_TOOLBOX_AUDIO_OBJECT.channelUnits;
	for i=1:length(names)
		if isempty(names{i,1})
			names{i,1} = ' ';
		end;
		if isempty(units{i,1})
			units{i,1} = ' ';
		end;
	end;

end;

