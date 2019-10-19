// initial values
var disabled = {domains: {}, pages: {}}; // settings for disabled domains and pages

// log
var log = console.log.bind(console);

log('Loading background page.');

// update Dictionaries
var updateDictionaries = function () {
    log("Updating Dictionaries.");
    var xhr = new XMLHttpRequest();
    xhr.open('GET', 'https://pathtodictionaries.php', true);
    xhr.onreadystatechange = function () {
        if (xhr.readyState == XMLHttpRequest.DONE && xhr.status == 200) {
            var data = JSON.parse(xhr.responseText);
            var updatedRules = {
                rulesTime: Date.now(),
                updateInterval: Math.min(604800, data.updateInterval),
                tm_heb: data.tm_heb,
                tm_eng: data.tm_eng
            };
        }
    };
    xhr.send();        
};

// on instaled or updated
(function (cb) {
    if (chrome.runtime.onInstalled) chrome.runtime.onInstalled.addListener(cb);
    else cb();
})(function () {
    log('Extension installed, loading default values.');
    var defaults = {
        options: {
            language: navigator.languages[navigator.languages.length-1],
            spelling: 0,
            dictionary: true,
            accentuation: true,
            abbreviations: true,
            capitalization: true,
            installDate: Date.now()
        }
    };
        // callback to save defaults
        var saveDefaults = function () {
            chrome.storage.local.set(defaults, function () {
                log('Default values saved:', defaults);
                loadScripts();
            });
        };
        // load scripts
        var loadScripts = function () {
            log('Loading script in open tabs.');
            chrome.tabs.query({}, function (tabs) {
                for (tab of tabs) {
                    console.log(tab);
                    chrome.tabs.executeScript(tab.id, {file: "browser-polyfill.js", allFrames: true, matchAboutBlank: true});
                    chrome.tabs.executeScript(tab.id, {file: "check.js"});
                }
            });
        };

        saveDefaults();

});

// message handler
chrome.runtime.onMessage.addListener(function(message, sender, sendResponse) {
    log('Message received from:', sender , ':', message);
    var response = {};
    if ('load' in message) {
        chrome.tabs.executeScript(sender.tab.id, {file: "content.js", frameId: sender.frameId, matchAboutBlank: true});
    }    
    if ('updateRules' in message) updateRules();
    if ('isDisabled' in message) {
        response.isDisabled = isDisabledUrl(message.isDisabled) || false;
    }
    if('checkLine' in message) {
        response.lineChange = 'test';
    }
    if ('isPortuguese' in message) {
        updateBadgeBackground(message.isPortuguese, sender.tab.id);
    }
    if ('detectLanguage' in message) {
        chrome.tabs.detectLanguage(sender.tab.id, function (language) {
            chrome.tabs.sendMessage(sender.tab.id, {language: language});
        });
    }
    if (Object.keys(response).length) {
        log('Sending response:', response);
        sendResponse(response);
    }
});

// load disabled sites settings
chrome.storage.local.get('disabled', function (items) {
    log("Retrieved from storage:", items);
    // disabled
    if (items.disabled) disabled = items.disabled;
    getActiveTab(updateUI);
});

// BROWSER ACTION

// retrieve active tab and run callback
var getActiveTab = function (cb) {
    chrome.tabs.query({active: true}, function (tabs) { if (tabs) cb(tabs[0]); });
};

// update button
var updateUI = function (tab) {
    log('Updating UI for: ', tab);
    if (isDisabledUrl(tab.url)) {
        chrome.browserAction.setBadgeText({tabId: tab.id, text: ''});
        chrome.browserAction.setTitle({tabId: tab.id, title: 'Disable on this page.'});
        // chrome.browserAction.disable(tab.id);
    }
    else {
        chrome.browserAction.setBadgeText({tabId: tab.id, text: '✓'});
        chrome.browserAction.setBadgeBackgroundColor({tabId: tab.id, color: '#4286f4'});
        chrome.browserAction.setTitle({tabId: tab.id, title: 'Enble on this page.'});
        // chrome.browserAction.enable(tab.id);
    }
};

// update button and tab
var updateTabAndUI = function (tab) {
    updateUI(tab);
    chrome.tabs.sendMessage(tab.id, {isDisabled: isDisabledUrl(tab.url) || false, tabActivated: true})
};

// update bagde background
var updateBadgeBackground = function (isPortuguese, tabId) {
    if (isPortuguese) {
        chrome.browserAction.setBadgeText({tabId: tabId, text: '✓'});
        chrome.browserAction.setBadgeBackgroundColor({tabId: tabId, color: '#248c23'});
        chrome.browserAction.setTitle({tabId: tabId, title: 'I am able to update text on this tab'})        
    }
    else {
        chrome.browserAction.setBadgeText({tabId: tabId, text: '🗴'});
        chrome.browserAction.setBadgeBackgroundColor({tabId: tabId, color: '#f45f42'});
        chrome.browserAction.setTitle({tabId: tabId, title: 'Unable to update input text.'})        
    }
}

// returns true if url is disabled in the settings
var isDisabledUrl = function (url) {
    var match = url.match(/^https?:\/\/(.+?)(\/.*)|^chrome-extension:\/\/.+\/test\.html$/i);
    return !match || disabled.global || disabled.domains[match[1]] || (disabled.pages[match[1]] && disabled.pages[match[1]][match[2]]);
};

// observe disabled sites settings changes
chrome.storage.onChanged.addListener(function (changes, areaName) {
    console.log('storage change:', areaName, changes);
    if (areaName == 'local') {
        if (changes.disabled) {
            disabled = changes.disabled.newValue;
            getActiveTab(updateTabAndUI);
        }
    }
});

// TABS

// update the button and the tab when the active tab changes
// the tab has to be updated because global or domain might have been changed in another tab
chrome.tabs.onActivated.addListener(function (activeInfo) {
    log('onActivated', activeInfo);
    getActiveTab(updateTabAndUI); 
});

// update the button when the page loads
// todo: webNavigation.onCompleted 
chrome.tabs.onUpdated.addListener(function (tabId, changeInfo, tab) {
    if (changeInfo.status == 'loading' && changeInfo.active) {
        log('onUpdated', changeInfo, tab);
        updateUI(tab);
    }
});

log('Background page loaded.');
