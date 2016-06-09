function addFields(start){
	var i = 0;
	for (i=start; i<start+5; i++){
		document.getElementById("student-"+i).className = "adders";
	}
	console.log(i);
	document.getElementById("btn-"+i).className = "btn";
}
