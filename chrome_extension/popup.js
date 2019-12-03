'use strict';

let importCSVbutton = document.getElementById('importCSVbutton');

importCSVbutton.onclick = function(element) {	
  chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
    chrome.tabs.insertCSS(
        tabs[0].id,
		{file: 'plickersImport.css'}
	);
    chrome.tabs.executeScript(
        tabs[0].id,
		{file: 'contentScript.js'}
	);
  });
};

