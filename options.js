document.addEventListener("DOMContentLoaded", function(e) {
    localizeHtmlPage();
});

function localizeHtmlPage() {
    var html = document.getElementsByTagName('html')[0];
    var valStrH = html.innerHTML.toString();
    var valNewH = valStrH.replace(/__MSG_(\w+)__/g, function(match, v1) {
        return v1 ? chrome.i18n.getMessage(v1) : "";
    });
    if(valNewH != valStrH) html.innerHTML = valNewH;
}

    
// feedback when user changes settings
var messageTimers = {};
var showMessage = function (elementId, text) {
        var element = document.getElementById(elementId);
        if (text) element.innerText = text;
        element.style.display = '';
        if (messageTimers[elementId]) clearInterval(messageTimers[elementId]);
        messageTimers[elementId] = setTimeout(function () { element.style.display = 'none'; }, 2500);

};