// Copyright 2018 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

'use strict';

chrome.runtime.onInstalled.addListener(function() {
  /* actions is default disable */
  chrome.action.disable();
  
  /* add allow rule for plickers */
  chrome.declarativeContent.onPageChanged.removeRules(undefined, function() {
    chrome.declarativeContent.onPageChanged.addRules([{
      conditions: [new chrome.declarativeContent.PageStateMatcher({
		pageUrl: {hostEquals: 'www.plickers.com'},
      })],
      actions: [new chrome.declarativeContent.ShowAction()]
    }]);
  });
});

/* actions: [new chrome.declarativeContent.ShowPageAction()] */