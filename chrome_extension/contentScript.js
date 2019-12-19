//
// global variable init
//
var api_url_base = 'https://api.plickers.com/';


// CSV 
var csvData = [];
var csvFilename = '';
var isImportToSet = false;

//for plicerks API
var folderId =  0;
var currentTime = '';

var csv_import_column_number = [];

//service.product : free / plus

if(!localStorage['csv_import_column_number']) {
	csv_import_column_number = [3, 4, 5, 6, 7, 8];
	localStorage['csv_import_column_number'] = JSON.stringify({csv_import_column_number:csv_import_column_number});
} else {
	csv_import_column_number = JSON.parse(localStorage['csv_import_column_number'])['csv_import_column_number'];
}	


// add zero to the number less than 10
prefix_zero = function(n) {
	return parseInt(n) <9 ? '0'+n : n;
}

// unique id generator
// source : 
//   https://www.w3resource.com/javascript-exercises/javascript-math-exercise-23.php
//
get_random_id = function(){
    var dt = new Date().getTime();
    //var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
	var uuid = 'xxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = (dt + Math.random()*16)%16 | 0;
        dt = Math.floor(dt/16);
        return (c=='x' ? r :(r&0x3|0x8)).toString(16);
    });
    return uuid;
}

//convert answer to digit
answer_convert_to_digit = function(s) {
	var ans = 0;
	if ( s=='1' || s=='A' || s=='a' || s=='ㄅ' || s=='甲' || s=='１' || s=='Ａ' || s=='一' ) 
		ans = 1;
	else if ( s=='2' || s=='B' || s=='b' || s=='ㄆ' || s=='乙' || s=='２' || s=='Ｂ' || s=='二' )
		ans = 2;
	else if ( s=='3' || s=='C' || s=='c' || s=='ㄇ' || s=='丙' || s=='３'  || s=='Ｃ' || s=='三' )
		ans = 3;
	else if ( s=='4' || s=='D' || s=='d' || s=='ㄈ' || s=='丁' || s=='４'  || s=='Ｄ' || s=='四' )
		ans = 4;
	return ans
}

//------------------------------------
// parseCSV 
//------------------------------------
// get source from:
//   https://stackoverflow.com/questions/1293147/javascript-code-to-parse-csv-data
//
parseCSV = function(str) {
    var arr = [];
    var quote = false;  // true means we're inside a quoted field

    // iterate over each character, keep track of current row and column (of the returned array)
    for (var row = 0, col = 0, c = 0; c < str.length; c++) {
        var cc = str[c], nc = str[c+1];        // current character, next character
        arr[row] = arr[row] || [];             // create a new row if necessary
        arr[row][col] = arr[row][col] || '';   // create a new column (start with empty string) if necessary

        // If the current character is a quotation mark, and we're inside a
        // quoted field, and the next character is also a quotation mark,
        // add a quotation mark to the current column and skip the next character
        if (cc == '"' && quote && nc == '"') { arr[row][col] += cc; ++c; continue; }  

        // If it's just one quotation mark, begin/end quoted field
        if (cc == '"') { quote = !quote; continue; }

        // If it's a comma and we're not in a quoted field, move on to the next column
        if (cc == ',' && !quote) { ++col; continue; }

        // If it's a newline (CRLF) and we're not in a quoted field, skip the next character
        // and move on to the next row and move to column 0 of that new row
        if (cc == '\r' && nc == '\n' && !quote) { ++row; col = 0; ++c; continue; }

        // If it's a newline (LF or CR) and we're not in a quoted field,
        // move on to the next row and move to column 0 of that new row
        if (cc == '\n' && !quote) { ++row; col = 0; continue; }
        if (cc == '\r' && !quote) { ++row; col = 0; continue; }

        // Otherwise, append the current character to the current column
        arr[row][col] += cc;
    }
    return arr;
}

popupInit = function() {
	var popup1 = document.getElementById('popup1');
	if( !popup1 ) {
		var popup1 = document.createElement('div');
		popup1.setAttribute('id', 'popup1');
		popup1.setAttribute('class', 'overlay');
		popup1.innerHTML = '<div class="popup"><h2>Plickers Import</h2><div id="popup-close" class="close">&times;</div><div id="popup-content" class="content"></div></div>';
		document.body.appendChild(popup1);
		
		
		//popup close button
		if( (/(ipod|iphone|ipad|android)/i).test(navigator.userAgent) ) {
			var eventType = 'touchend';
		} else {
			var eventType = 'click';
		}		
		document.getElementById('popup-close').addEventListener(eventType, function() {
			showMessage();
		});		
	}
	//console.log(popup1);
}

//顯示訊息
showMessage = function(msg, delay, callback) {      
	popupInit();
	var popup1 = document.getElementById('popup1');
	if( typeof(msg) == 'undefined' ) {
	  popup1.style.visibility = 'hidden';
	  popup1.style.opacity = 0;
	} else {
	  //document.getElementById('popup-content').textContent = msg;
	  document.getElementById('popup-content').innerHTML = msg;
	  popup1.style.visibility = 'visible';
	  popup1.style.opacity = 1;
	  
	  if(typeof(delay) != 'undefined') {
		setTimeout( function() {            
		  popup1.style.visibility = 'hidden';
		  popup1.style.opacity = 0;
		  if( typeof(callback)=='function' ) {
			callback();
		  }			
		}, delay);
	  } else {
		  if( typeof(callback)=='function' ) {
			callback();
		  }
	  }
	}        
}

	
getToken = function() {
	if(typeof(localStorage["ls.session"]) != 'undefined') {
		token = JSON.parse(localStorage["ls.session"]).token;
	}
	if(typeof(token) != 'undefined' && token != null) {
		return token;
	} else {
		showMessage(chrome.i18n.getMessage('sign_in_first'), 5000);
		
		return null;
	}
}

sendRequest = function(request_url, request_type, headers, content, callback, argument ) {
	if (window.XMLHttpRequest) {     
      req = new XMLHttpRequest(); 
	}     
	else if (window.ActiveXObject) {     
      req = new ActiveXObject("Microsoft.XMLHTTP");     
	}     

	req.open(request_type, request_url);
	
	for(let key in headers){
      req.setRequestHeader(key, headers[key]) 
    }
	
	req.onreadystatechange = function() {     
   		if (req.readyState == 4) {
			//200 : OK
			//201 : Created
			//404 : Not Found
			if(req.status == 200 || req.status == 201) {
				if( typeof(callback) == 'function' ) {
					if(argument) {
						callback(req.responseText, argument);
					} else {
						callback(req.responseText);
					}
				} 
			} else {
				//console.log(req);
				if( typeof(callback) == 'function' ) {
					if(argument) {
						callback(-1, argument);
					} else {
						callback(-1);
					}
				}
			}
		}
	}
	try {
		//req.send(null);
		req.send(content);		
	} catch(e) {
		//alert(e);
	}
}

//get currentTime
get_currentTime = function(callback) {
	//var currentTime = '';		
	var headers = { 'x-auth-token' : token };
	var url = api_url_base+'current-time';	
	sendRequest(url, 'GET', headers, null, function(response) {	
		currentTime = JSON.parse(response)['currentTime'];
		if( typeof(callback) == 'function' ) {
			callback(currentTime);
			//callback();
		}
	});
	//console.log(currentTime);
}

get_newFolderId = function(folder_name, callback) {
	var token = getToken();
	var headers = { 
		'x-auth-token' : token,
		'content-type' : 'application/json; charset=utf-8'
	};
	var url = api_url_base+'folders';
	
	get_currentTime( function(current_time) {
		var content = {
			"name":folder_name,
			"parent":null,
			"clientModified":current_time,
			"userCreated":current_time,
			"archived":false
		}
		//console.log(headers);
		//console.log(content);
		sendRequest(url, 'POST', headers, JSON.stringify(content), function(response) {	
			folderId = JSON.parse(response)['id'];
			if( typeof(callback) == 'function' ) {
				callback(folderId);
			}
		});
	});
}

get_choices = function(data, isAt) {
	//isAt : [question, answer, op1, op2, op3, op4]
	var answer = data[isAt[1]];
	var choices = [];
	for(c=0; c<4; c++) {
		if( isAt[2+c] >= 0 && isAt[2+c] < data.length) {
			var body = data[isAt[2+c]];
			if( body != '' ) {
				if( (c+1) == answer_convert_to_digit(answer) ) {
					var correct = true;
				} else {
					var correct = false;
				}
				var choice = { 'body':body, 'correct':correct };
				choices.push(choice);
			}
		}
	}
	return choices;
}
new_set = function(name, csvData, isAt, current_time, callback) {
	if( typeof(folderId) == 'undefined' ) {
		var folderId = null;
	}
	var import_total = 0
	var failure_total = 0
	
	var token = getToken();
	var headers = { 
		'x-auth-token' : token,
		'content-type' : 'application/json; charset=utf-8'
	};

	var questions = [];
	for(var i=1, len=csvData.length; i<len; i++) {
		//free plan, can import  5 questions from csv file
		if( localStorage['service.product'] &&  JSON.parse(localStorage['service.product']) == 'free' && i>5 && (name.toLowerCase()).indexOf('-enable-plus') < 0 ) {
			break;
		}
		var question = {
			"xLayout":{"bodyFS":64,"choiceFS":38,"bodyH":365,"version":2},
			"template":"standard",
			"image":""
		}
		question.questionId = get_random_id();
		question.body = csvData[i][isAt[0]];
		question.choices = get_choices(csvData[i], isAt);
		questions.push(question);
	}
	var content = {
		"folder":null,
		"archived":false,
		"repo":null,
		"name":name,
		"description":"Empty description",
		"clientModified":current_time,
		"userCreated":current_time,
		"lastEditedAt":current_time		
	}		
	content.questions = questions;
		
	var url = api_url_base+'sets';
	sendRequest(url, 'POST', headers, JSON.stringify(content), function(response) {	
		var id = JSON.parse(response)['id'];
		if( typeof(callback) == 'function' ) {
			callback(id);
		}
	});
	
}
new_questions = function(folderId, csvData, isAt, current_time, callback) {
	if( typeof(folderId) == 'undefined' ) {
		var folderId = null;
	}
	var import_total = 0
	var failure_total = 0
	
	var token = getToken();
	var headers = { 
		'x-auth-token' : token,
		'content-type' : 'application/json; charset=utf-8'
	};

	for(var i=1, len=csvData.length; i<len; i++) {			
		var question_body = csvData[i][isAt[0]];
		
		//new question data
		var content = {
			"body":question_body,
			"xLayout":{"bodyFS":64,"choiceFS":38,"bodyH":365,"version":2},
			"template":"standard",
			"image":"",
			"folder":folderId,
			"repo":null,
			"archived":false,
			"createdOnMobile":false,
			"version":0,
			"clientModified":current_time,
			"userCreated":current_time,
			"lastEditedAt":current_time
		}
		content.choices = get_choices(csvData[i], isAt);
				
		var url = api_url_base+'questions';
		sendRequest(url, 'POST', headers, JSON.stringify(content), function(response) {	
			var id = JSON.parse(response)['id'];
			if( typeof(callback) == 'function' ) {
				callback(id);
			}
		});
	}
	
}

get_csv_file = function(callback) {	
	var inputFile = document.getElementById('csvfile');
	if ( inputFile == null ) {	
		//console.log('create file element');
		var inputFile = document.createElement('input'); //, {'id':'csvfile', 'type':'file', 'accept':'.csv', 'style':'display:none;'})
		inputFile.setAttribute('type', 'file');
		inputFile.setAttribute('accept', '.csv');
		inputFile.setAttribute('id', 'csvfile');
		inputFile.style['display'] = 'none';		
		document.body.appendChild(inputFile);		
	}
	//var inputFile = document.getElementById('csvfile');
	//console.log(inputFile);
		
	inputFile.addEventListener('change', file_handler = function(evt) {      
		//importCSVquestions();
		var files = evt.target.files;
		// FileList object
		if( files.length > 0 ) {
			var file = files[0];
			
			csvFilename = file['name'];
			
			var reader = new FileReader();
			
			// Closure to capture the file information.
			reader.onload = ( function(theFile) {
				return function(e) {
					var textString = e.target.result;
					if( typeof(textString) != 'undefined' ) {
						//console.log(textString);
						//alert((textString))
					} else {
						textString = null;
						alert(chrome.i18n.getMessage('file_read_error'));
					}
					if(typeof(callback) == 'function') {
						callback(csvFilename, textString);
					}
					delete reader;
					delete file;
					delete files;
				}
			})(file);

			// Read CSV file as text
			reader.readAsText(file, csv_file_encode);						
		}
		try {
			inputFile.removeEventListener('change', file_handler, false);
		} catch(e) { };
		try {			
			document.body.removeChild(inputFile);
		} catch(e) { };
		delete inputFile;
		inputFile = null;
	}, false);

	inputFile.click();

}

      
getOptionsAndSaveToLocalStorage = function() {
	var importButton = document.getElementById('importButton');
	try {
		importButton.removeEventListener('click', getOptionsAndSaveToLocalStorage, false);
	} catch(e) { };
		
	for(var i=0; i<=6; i++) {
		var radios = document.getElementsByName('csv_import_at['+i+']');
		for (var r=0,length=radios.length; r<length; r++) {
			if (radios[r].checked) {
				csv_import_column_number[i] = parseInt(radios[r].value);
				break;
			}
		}
	}
	//save value to localStorage
	localStorage['csv_import_column_number'] = JSON.stringify({csv_import_column_number:csv_import_column_number});
	//console.log(csv_import_column_number);
	
	isImportToSet = document.getElementsByName('isImportToSet')[0].checked;
	//close diallog frame
	showMessage();
	return [csv_import_column_number, isImportToSet];
}

setImportColumnsAndWaitToSubmit = function(csvFilename, textString) {
	//var captions = ['題幹', '答案', '選項1', '選項2', '選項3', '選項4'];
	var captions = [chrome.i18n.getMessage('columns_name0'), chrome.i18n.getMessage('columns_name1'), chrome.i18n.getMessage('columns_name2'), chrome.i18n.getMessage('columns_name3'), chrome.i18n.getMessage('columns_name4'), chrome.i18n.getMessage('columns_name5') ];
	
	//var html = '<h3>['+csvFilename+']設定匯出哪些欄位</h3>';
	var html = '<h3>['+csvFilename+'] '+chrome.i18n.getMessage('columns_config')+'</h3>';
	
	html += '<table  width="95%">';
	
	//showMessage(textString);
	var csvData = parseCSV(textString);
	
	var rowTotal = csvData.length;
	var colTotal = csvData[0].length;
	
	var r= 0;
	html += '<tr><td>&nbsp;</td>';
	html += '<td>'+chrome.i18n.getMessage('columns_disable')+'</td>';
	for(var c=0; c<colTotal; c++) {
		html += '<td>'+(c+1)+'<br />'+csvData[r][c]+'</td>';
	}
	
	html += '</tr>';
	for(var r=0; r<6; r++) {
		//html += '<td>'+captions[r]+'由哪一欄匯出:'+'</td>';
		html += '<th align="right" nowrap>'+captions[r]+chrome.i18n.getMessage('columns_import_from')+'</th>';
		var valueSaved = parseInt(csv_import_column_number[r]);
		if( valueSaved < 0 || valueSaved > colTotal-1 ) {
			valueSaved = -1;
		}
		if(valueSaved < 0) {
			html += '<td><input type="radio" name="csv_import_at['+r+']" value="-1" checked></td>';
		} else {
			html += '<td><input type="radio" name="csv_import_at['+r+']" value="-1"></td>';
		}
		for(var c=0; c<colTotal; c++) {
			var checked = '';
			if(c == valueSaved) {
				checked = 'checked';
			}
			html += '<td><input type="radio" name="csv_import_at['+r+']" value="'+c+'" '+checked+'></td>';
		}
		html += '</tr>';
	}
	html += '</table>';
	//html += '<p><input type="checkbox" id="isImportToSet" name="isImportToSet">所有題目變成一個 SET</p>';
	//html += '<p><center><input type="button" id="importButton" value="開始匯出"></center></p>';
	html += '<p><input type="checkbox" id="isImportToSet" name="isImportToSet"> '+chrome.i18n.getMessage('set_checkbox_caption')+'</p>';
	html += '<p><center><input type="button" id="importButton" value="'+chrome.i18n.getMessage('submit_button_caption')+'"></center></p>';

	//console.log(html);
	showMessage(html);
	
	isImportToSet = false;
	
	//set the submit button listener
	var importButton = document.getElementById('importButton');
	importButton.addEventListener('click', function() {
		importCSVdataToPlickers(csvFilename, csvData);
	});
	//console.log();
}


importCSVdataToPlickers = function(csvFilename, csvData) {
	//options : isAt , isSet
	[isAt, isSet] = getOptionsAndSaveToLocalStorage();
	//console.log(csvFilename);
	//console.log(csvData);
	//console.log(isImportToSet);
	get_currentTime( function(current_time) {
		if(isSet) {
			new_set(csvFilename, csvData, isAt, current_time, function() {
				//showMessage('已經將 CSV 檔案('+csvFilename+')中的題目<p>新增至命名為「'+csvFilename+'」的 SET 中了。</p>5秒後自動重新整理畫面後查看結果。<p>&nbsp;</p><p>&nbsp;</p><p>&nbsp;</p>', 5000);
				showMessage(chrome.i18n.getMessage('imported_to_set')+csvFilename+'</p>'+chrome.i18n.getMessage('page_reload')+'<p>&nbsp;</p><p>&nbsp;</p><p>&nbsp;</p>', 5000);
				setTimeout( function() {
					location.reload(true);
				}, 5000);				
			});
		} else {
			get_newFolderId(csvFilename, function(folderId) {
				new_questions(folderId, csvData, isAt, current_time, function() {
					//showMessage('已經將 CSV 檔案('+csvFilename+')中的題目<p>新增至資料夾「'+csvFilename+'」中了。</p>5秒後自動重新整理畫面後查看結果。<p>&nbsp;</p><p>&nbsp;</p><p>&nbsp;</p>', 5000);
					showMessage(chrome.i18n.getMessage('imported_to_folder')+csvFilename+'</p>'+chrome.i18n.getMessage('page_reload')+'<p>&nbsp;</p><p>&nbsp;</p><p>&nbsp;</p>', 5000);
					setTimeout( function() {
						location.reload(true);
					}, 5000);
				});
			});
		}
	});
}

//get the csv_file_encode from popup page selected
var csv_file_encode = 'utf-8';
chrome.storage.local.get('csv_file_encode', function(value) {
	csv_file_encode = value['csv_file_encode'];
});

if( token = getToken() ) {
	get_csv_file(setImportColumnsAndWaitToSubmit);
}

