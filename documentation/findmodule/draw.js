function draw_filters(number){
	number_of_filters = number;
	var src =		"<table>";
	for (var i=0; i<number; i++){
		var disabled = "";
		src +=		"	<tr>" +
					"		<td>";
		if (i != 0){
			disabled = "disabled='disabled'";
			src +=	"			<select id='combination" + i + "' onChange='enable_filter(" + i + ")'>" +
					"				<option value='Nothing' selected='selected'>Nothing</option>" +
					"				<option value='And'>And</option>" +
					"				<option value='Or'>Or</option>" +
					"			</select>";
		}
		src +=		"		</td>" +
					"		<td>" +
					"			<select id='quantifier" + i + "' onChange='show_modules()' " + disabled + ">" +
					"				<option value='Exactly'>Exactly</option>" +
					"				<option value='At least' selected='selected'>At least</option>" +
					"				<option value='At most'>At most</option>" +
					"			</select>" +
					"		</td>" +
					"		<td>" +
					"			<input type='text' id='number" + i + "' value='1' size='4' maxlength='4' onChange='ensure_integer_input(\"number" + i + "\")' " + disabled + " />" +
					"		</td>" +
					"		<td>" +
					"			<select id='datatype" + i + "' onChange='show_modules()' " + disabled + ">" +
					"				<option value='Any' selected='selected'>Any</option>";
		for (var j in data_types){
			src +=	"				<option value='" + j + "'>" + j + "</option>";
		}
		src +=		"			</select>" +
					"		</td>" +
					"		<td>" +
					"			<select id='connector" + i + "' onChange='show_modules()' " + disabled + ">" +
					"				<option value='Any' selected='selected'>any connector</option>" +
					"				<option value='Output'>Output connectors</option>" +
					"				<option value='AnyInput'>Input or Mulitinput connectors</option>" +
					"				<option value='Input'>Input connectors</option>" +
					"				<option value='Mulitinput'>Mulitinput connectors</option>" +
					"				<option value='Trigger'>Trigger connectors</option>" +
					"			</select>";
					"		</td>" +
					"	<tr>";
	}
	src += "</table>";
	document.write(src);
}

function draw_modules(){
	var src = "";
	for (var c in classes)
		src +=	"<div id='class" + c + "'><a href='" + classes[c].doxygen_link + "'>" + c + "</a></div>";
	document.write(src);
	show_modules();
}

