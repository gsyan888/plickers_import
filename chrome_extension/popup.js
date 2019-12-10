'use strict';

let popup_caption = document.getElementById('popup_caption');
popup_caption.innerHTML = chrome.i18n.getMessage('popup_caption');

let importCSVbutton = document.getElementById('importCSVbutton');
importCSVbutton.innerHTML = chrome.i18n.getMessage('importCSVbutton_caption');

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

