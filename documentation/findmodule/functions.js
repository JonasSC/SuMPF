var classes = new Object();
var number_of_filters;

function SumpfModule(outputs, inputs, multiinputs, triggers, multitypeconnectors, doxygen_link){
	this.outputs = outputs;
	this.inputs = inputs;
	this.multiinputs = multiinputs;
	this.triggers = triggers;
	this.multitypeconnectors = multitypeconnectors;
	this.doxygen_link = doxygen_link;
}

function enable_filter(index){
	var disable = false;
	if(document.getElementById("combination" + index).value == "Nothing")
		disable = true;
	document.getElementById("quantifier" + index).disabled = disable;
	document.getElementById("number" + index).disabled = disable;
	document.getElementById("datatype" + index).disabled = disable;
	document.getElementById("connector" + index).disabled = disable;
	show_modules();
}

function ensure_integer_input(id){
	var value = parseInt(document.getElementById(id).value);
	document.getElementById(id).value = value;
	show_modules();
}

function show_modules(){
	var found_modules = 0;
	for (var c in classes){
		var show = true;
		var combination = "And";
		for (i=0; i<number_of_filters; i++){
			if (i != 0)
				combination = document.getElementById("combination" + i).value;
			if (combination != "Nothing"){
				check = check_module(classes[c],
				                     document.getElementById("quantifier" + i).value,
				                     document.getElementById("number" + i).value,
				                     document.getElementById("datatype" + i).value,
				                     document.getElementById("connector" + i).value);
				if (combination == "Or")
					show = show || check;
				else
					show = show && check;
			}
		}
		if (show){
			var element = document.getElementById("class" + c);
			element.style.visibility = "visible";
			element.style.position = "static";
			found_modules++;
		}else{
			var element = document.getElementById("class" + c);
			element.style.visibility = "hidden";
			element.style.position = "absolute";
		}
	}
	document.getElementById("found_modules").innerHTML = found_modules + " modules found";
}

function check_module(module, quantifier, number, datatype, connector){
	var count = 0;
	if (connector == "Any" || connector == "Output"){
		for (var t in module.outputs){
			if (check_datatype(t, datatype, false)){
				count += module.outputs[t];
			}
		}
		for (var i=0; i<module.multitypeconnectors[0].length; i++){
			for (var j=0; j<module.multitypeconnectors[0][i].length; j++){
				if (check_datatype(module.multitypeconnectors[0][i][j], datatype, false)){
					count++;
					break;
				}
			}
		}
	}
	if (connector == "Any" || connector == "AnyInput" || connector == "Input"){
		for (var t in module.inputs){
			if (check_datatype(t, datatype, true)){
				count += module.inputs[t];
			}
		}
		for (var i=0; i<module.multitypeconnectors[1].length; i++){
			for (var j=0; j<module.multitypeconnectors[1][i].length; j++){
				if (check_datatype(module.multitypeconnectors[1][i][j], datatype, true)){
					count++;
					break;
				}
			}
		}
	}
	if (connector == "Any" || connector == "AnyInput" || connector == "Mulitinput"){
		for (var t in module.multiinputs){
			if (check_datatype(t, datatype, true)){
				count += module.multiinputs[t];
			}
		}
		for (var i=0; i<module.multitypeconnectors[2].length; i++){
			for (var j=0; j<module.multitypeconnectors[2][i].length; j++){
				if (check_datatype(module.multitypeconnectors[2][i][j], datatype, true)){
					count++;
					break;
				}
			}
		}
	}
	if (connector == "Any" || connector == "Trigger"){
		count += module.triggers;
	}
	if (quantifier == "Exactly" && count == number)
		return true;
	else if (quantifier == "At least" && count >= number)
		return true;
	else if (quantifier == "At most" && count <= number)
		return true;
	else
		return false;
}

function check_datatype(current_type, searched_type, setter){
	if (searched_type == "Any")
		return true;
	else if (current_type == searched_type)
		return true;
	else if (setter){
		for (var i=0; i<data_types[searched_type].length; i++){
			if (data_types[searched_type][i] == current_type)
				return true;
		}
	}else{
		for (var i=0; i<data_types[current_type].length; i++){
			if (data_types[current_type][i] == searched_type)
				return true;
		}
	}
	return false;
}

