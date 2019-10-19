function a(){document.removeEventListener("input",a);chrome.runtime.sendMessage({load:1})}document.addEventListener("input",a)
// fixme: temporary fix to avoid the lag caused when compiling the regex when the user starts typing
/*const handler = () => {
	if (document.visibilityState == 'visible') {
		chrome.runtime.sendMessage({load:1});
		document.removeEventListener("visibilitychange", handler);
	}
};
if (document.visibilityState == 'visible') chrome.runtime.sendMessage({load:1});
else document.addEventListener("visibilitychange", handler);*/