'use strict';

let popup_caption = document.getElementById('popup_caption');
popup_caption.innerHTML = chrome.i18n.getMessage('popup_caption');

let importCSVbutton = document.getElementById('importCSVbutton');
importCSVbutton.innerHTML = chrome.i18n.getMessage('importCSVbutton_caption');


importCSVbutton.onclick = function(element) {
  let file_encode = document.getElementsByName('file_encode');
  let encode = 'utf-8';
  for(var i=0, n=file_encode.length; i<n ; i++) {
    if(file_encode[i].checked) {
		encode = file_encode[i].value;
		break;
	}
  }
  
  chrome.storage.local.set({csv_file_encode:encode});
  
  chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
	var activeTab = tabs[0];
	
	chrome.scripting.insertCSS({
		target: { tabId: activeTab.id },
		files: ["plickersImport.css"]
	});
	
	chrome.scripting.executeScript({
		target: { tabId: activeTab.id },
		files: ["contentScript.js"]
	});
  });
};

