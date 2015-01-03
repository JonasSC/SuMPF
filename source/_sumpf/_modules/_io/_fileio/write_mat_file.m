function write_mat_file(filename, channels, samplingrate, resolution, labels)
	disp('Octave here');
	disp(labels);
	disp('Octave out');
	if samplingrate ~= 0
		save(filename, 'channels', 'samplingrate', 'labels');
	else
		save(filename, 'channels', 'resolution', 'labels');
	end;
end;
