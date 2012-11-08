function DrawHeader(){
	function Link(name, link){
		this.name = name;
		this.link = link;
	}
	links = new Array();
	links.push(new Link("About", "index.htm"));
	links.push(new Link("To do's", "todo.htm"));
	links.push(new Link("Documentation", "documentation.htm"));
	links.push(new Link("Installation", "installation.htm"));

	styles = new Object();
	styles["maintable"] = "width: 80%;" +
	                      "margin-left: auto;" +
	                      "margin-right: auto;";
	styles["headline"] = "font-size: xx-large;" +
	                     "background: #6080FF;";
	styles["motto"] = "text-align: center;" +
	                  "font-size: larger;" +
	                  "background: #C8E0FF;";
	styles["link"] = "width: " + 100.0/links.length + "%;" +
	                 "text-align: center;" +
	                 "font-size: larger;" +
	                 "background: #E0F0FF;";

	go_back = true;
	try{
		if (dont_go_back==true)
			go_back = false;
	}
	catch(e){}

	source = "<table style='" + styles["maintable"] + "'>" +
	         "	<tr>" +
	         "		<th colspan='" + links.length + "' style='" + styles["headline"] + "'>SuMPF</th>" +
	         "	</tr>" +
	         "	<tr>" +
	         "		<td colspan='" + links.length + "' style='" + styles["motto"] + "'>Sound using a Monkeyforest-like processing framework</td>" +
	         "	</tr>" +
	         "	<tr>";
	for(i=0; i<links.length; i++){
		link = links[i].link;
		if (go_back == true)
			link = "../" + link
		source += "	<td style='" + styles["link"] + "'><a href='" + link + "'>" + links[i].name + "</a></td>";
	}
	source += "	</tr>" +
	         "	<tr>" +
	         "		<td colspan='" + links.length + "' style='" + styles["link"] + "'>&nbsp;</td>" +
	         "	</tr>" +
	          "</table>";

	document.write(source);
}

DrawHeader();

