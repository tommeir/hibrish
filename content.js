(function () {
	'use strict';
	localStorage.setItem('debug', true);
	var log = localStorage.getItem('debug') ? console.log.bind(console) : function () {};

	log('Loading content script...');

	var lastReplace = null;
	var lastCheck = null;
	var tm_dicLoading = false;
	var tm_dicLoading2 = false;
	var tm_hibrishDictionary_he = [];
	var tm_hibrishDictionary_en = [];
	var isDisabled = true;
	var languageInput = null;
	var languagePage = null;
	var lastLanguage = null;
	var heb2engOn = false;
	var eng2hebOn = false;


	// load Hibrish hebrew dictionary
	var tm_loadHibDic = function () {
		if (tm_dicLoading)
			return;
		tm_dicLoading = true;
		log('Loading tm_hibrishDictionary_he dic...');

		var init = Date.now();
		var xhr = new XMLHttpRequest();
		xhr.open('GET', chrome.extension.getURL('hibrish_engheb.json'), true);
		xhr.onreadystatechange = function () {
			if (xhr.readyState == XMLHttpRequest.DONE && xhr.status == 200) {
				var tm_data = JSON.parse(xhr.responseText);
				for (var i in tm_data) {
					tm_hibrishDictionary_he[tm_data[i][1]] = tm_data[i][0];	
				}
				log('tm_hibrishDictionary_he',tm_hibrishDictionary_he);
				
			}
			tm_dicLoading = false;
		}
		xhr.send();
	};
	// load Hibrish English dictionary
	var tm_loadEngDic = function () {
		if (tm_dicLoading2)
			return; 
		tm_dicLoading2 = true;
		log('Loading tm_hibrishDictionary_en dic...');

		var init = Date.now();
		var xhr = new XMLHttpRequest();
		xhr.open('GET', chrome.extension.getURL('hibrish_hebeng2.json'), true);
		xhr.onreadystatechange = function () {
			if (xhr.readyState == XMLHttpRequest.DONE && xhr.status == 200) {
				var tm_data = JSON.parse(xhr.responseText);
				for (var i in tm_data) {
					tm_hibrishDictionary_en['\''+tm_data[i][1].toString().toLowerCase()+'\''] = tm_data[i][0];	
				}	

				log('tm_hibrishDictionary_en',tm_hibrishDictionary_en);				
			}
			tm_dicLoading2 = false;
		}
		xhr.send();
	};

	// send message to background page
	var sendMessage = function (message, cb) {
		log('sending message:', message);
		chrome.runtime.sendMessage(message, function (response) {
			if (response)
				handleMessage(response);
			if (cb)
				cb(response);
		});
	};

	// handle messages from background page
	var handleMessage = function (message, sender) {
		log('Message received from:', sender, ':', message);
		if ('isDisabled' in message) {
			isDisabled = message.isDisabled;
			log('Is disabled:', isDisabled);
		}
		if (message.language) {
			log('Page language:', message.language);
			languagePage = message.language == 'pt' || (/^und?$/.test(message.language) && null); // true if pt, null if undetermined, false otherwise
			languageUpdated();
		}
		// send to the background the current detected language
		if ('tabActivated' in message) {
			sendMessage({
				isPortuguese: lastLanguage
			});
		}if('lineChange' in message) {

		}
		else {
			log('unhandled message',[message,sender]);
		}
		return ;
	};

	// update browser action badge color when detected language changes
	var languageUpdated = function () {
		var currentLanguage =
			languageInput === null ?
			(lastLanguage === null ?
				// default to portuguese in the first 15 minutes after installing the extension to avoid complaints about it not working
				 languagePage : lastLanguage) : languageInput;
		log('currentLanguage:', currentLanguage, 'lastLanguage:', lastLanguage, 'languageInput:', languageInput, 'languagePage:', languagePage);
		if (currentLanguage != lastLanguage) {
			sendMessage({
				isPortuguese: currentLanguage
			});
			lastLanguage = currentLanguage;
		}
	};


function convertHeb2Eng(hebtxt)
{
 
	var heb2eng=new Array();
		heb2eng[0]=116; 
		heb2eng[1]=99; 
		heb2eng[2]=100; 
		heb2eng[3]=115; 
		heb2eng[4]=118; 
		heb2eng[5]=117;
		heb2eng[6]=122;
		heb2eng[7]=106;
		heb2eng[8]=121;
		heb2eng[9]=104;
		heb2eng[10]=108;
		heb2eng[11]=102;
		heb2eng[12]=107;
		heb2eng[13]=111;
		heb2eng[14]=110;
		heb2eng[15]=105;
		heb2eng[16]=98;
		heb2eng[17]=120;
		heb2eng[18]=103;
		heb2eng[19]=59;
		heb2eng[20]=112;
		heb2eng[21]=46;
		heb2eng[22]=109;
		heb2eng[23]=101;
		heb2eng[24]=114;
		heb2eng[25]=97;
		heb2eng[26]=44; 
		heb2eng[47]=113;
		heb2eng[39]=119;
		heb2eng[44]=39;
		heb2eng[46]=47;


		var engtxt = new Array();
		var i=0;
		for(i=0; i<hebtxt.length; i++)
		{
			if(hebtxt.charCodeAt(i) < 1488 || hebtxt.charCodeAt(i) > 1514)
			{
				if(heb2eng[hebtxt.charCodeAt(i)] == null)
				{	
					engtxt[i] = hebtxt[i];
				}
				else
				{
					engtxt[i] = String.fromCharCode(heb2eng[hebtxt.charCodeAt(i)]);
				}
			}
			else
			{
				engtxt[i] = String.fromCharCode(heb2eng[hebtxt.charCodeAt(i)-1488]);
			}
			
			if(hebtxt[i] == "(")
			{
				engtxt[i] = ")";
			}
			else if(hebtxt[i] == ")")
			{
				engtxt[i] = "(";
			}
		}
		
		return engtxt.join("");
}

function convertEng2Heb(engtxt)
{
	var eng2Heb=new Array();
		eng2Heb[0]=1513; //a
		eng2Heb[1]=1504; //b
		eng2Heb[2]=1489; //c
		eng2Heb[3]=1490; //d
		eng2Heb[4]=1511; //e
		eng2Heb[5]=1499;//f
		eng2Heb[6]=1506;//g
		eng2Heb[7]=1497;//h
		eng2Heb[8]=1503;//i
		eng2Heb[9]=1495;//j
		eng2Heb[10]=1500;//k
		eng2Heb[11]=1498;//l
		eng2Heb[12]=1510;//m
		eng2Heb[13]=1502;//n
		eng2Heb[14]=1501;//o
		eng2Heb[15]=1508;//p
		eng2Heb[16]=8260;//q
		eng2Heb[17]=1512;//r
		eng2Heb[18]=1491;//s
		eng2Heb[19]=1488;//t
		eng2Heb[20]=1493;//u
		eng2Heb[21]=1492;//v
		eng2Heb[22]=39;//w
		eng2Heb[23]=1505;//x
		eng2Heb[24]=1496;//y
		eng2Heb[25]=1494;//z
		eng2Heb[59]=1507; //;
		eng2Heb[39]=44;//'
		eng2Heb[44]=1514; //,
		eng2Heb[46]=1509;//.
		eng2Heb[47]=46;//   /
		eng2Heb[96]=59; //`

		var hebtxt = new Array();
		var i=0;
		for(i=0; i<engtxt.length; i++)
		{
			if(engtxt.charCodeAt(i) < 97 || engtxt.charCodeAt(i) > 122)
			{
				if(eng2Heb[engtxt.charCodeAt(i)] == null)
				{	
					hebtxt[i] = engtxt[i];
				}
				else
				{
					hebtxt[i] = String.fromCharCode(eng2Heb[engtxt.charCodeAt(i)]);
				}
			}
			else
			{
				hebtxt[i] = String.fromCharCode(eng2Heb[engtxt.charCodeAt(i)-97]);
			}
			
			if(engtxt[i] == "(")
			{
				hebtxt[i] = ")";
			}
			else if(engtxt[i] == ")")
			{
				hebtxt[i] = "(";
			}
		}
		
		return hebtxt.join("");	
}

var check_engHib = function(wordEng) {
	
	if(tm_hibrishDictionary_en[wordEng])
		return tm_hibrishDictionary_en[wordEng];
	
	log('english word was not direct simple hebrew word');
	
	return ;
	
}

	var InputData = function (input) {
		if ('value' in input) {
			this.getText = function () {
				return input.value;
			};
			this.setText = function (text) {
				input.value = text;
			};
			this.getCursorPosition = function () {
				return input.selectionEnd;
			};
			this.setCursorPosition = function (position) {
				input.selectionEnd = position;
			};
		} else {
			var selection = input.ownerDocument.getSelection();
			var range = selection.getRangeAt(0);
			this.range = {
				startContainer: range.startContainer,
				startOffset: range.startOffset,
				endContainer: range.endContainer,
				endOffset: range.endOffset
			};

			this.getText = function () {
				return this.range.endContainer.nodeValue || '';
			};
			this.setText = function (text) {
				this.range.endContainer.nodeValue = text;
			};
			this.getCursorPosition = function () {
				return this.range.endOffset;
			};
			this.setCursorPosition = function (position) {
				var selection = input.ownerDocument.getSelection();
				selection.removeAllRanges();
				var newRange = document.createRange();
				newRange.setStart(this.range.startContainer, position);
				newRange.setEnd(this.range.endContainer, position);
				selection.addRange(newRange);
			};
		}
		this.text = this.getText();
		this.cursorPosition = this.getCursorPosition();
		this.left = this.text.substr(0, this.cursorPosition);
		this.right = this.text.substring(this.cursorPosition, this.text.length);
	};

	var spellCheck = function (left) {
		 //log('spellcheck: "' + left + '"');
		
		 // if (/[a-zA-ZàáâãéêíóôõúüçÀÁÂÃÉÊÍÓÔÕÚÜÇ\-]$/.test(left)) return; // we're in the middle of a word
		if (!/([,;:\)\[\]*!?…\s\n]|\.\.+)$/.test(left))
			return; // we're in the middle of a word ([ and * mark the end of word in bbcode and markdown contexts)

		var leftLines = left.match(/.+(\n+|$)/g); // lines before current line
		var line = leftLines.pop(); // current line FIXME: error when using delete with cursor at 0

		if (/^ *>/.test(line))
			return; // quote
		if (/https?:\/\/[^ \)\]]+\.?[^]$/i.test(line))
			return; // url
		if (/www\.[\w-]+\.[\w-]+[^ \)\]]+\.?[^]$/i.test(line))
			return; // url
		if (/[\w.+-]+@[a-z0-9-]+(\.[a-z0-9-]+)+\.?[^]$/i.test(line))
			return; // email
		if (/[ru]\/[a-zA-ZàáâãéêíóôõúüçÀÁÂÃÉÊÍÓÔÕÚÜÇ0-9_-]+\.?[^]$/i.test(line))
			return; // users/subs
		if (/«[^»]*$/.test(line))
			return; // quote
		if (/^[^"]*"[^"]*([^"]*"[^"]*"[^"]*)*\.?[^]$/.test(line))
			return; // quote
		if (/^[^*]*\*[^*]*([^*]*\*[^*]*\*[^*]*)*\.?[^]$/.test(line.replace(/\*\*.+?\*\*/g, '')))
			return; // italic

		//if (!checkLanguage(left))
		//	return;


		var onlywordsarray = line.split(/(?:,| )+/);
		while(onlywordsarray[onlywordsarray.length-1] == "") 
			onlywordsarray.pop(); //remove empty last words 
		log(onlywordsarray);
		
		//skeleton call to bg page to do the spell checking instead. 
		//todo: maybe delete this call  and rebuild with proper promise pattern?
		sendMessage({
			checkLine: onlywordsarray
		});		
		//back to real-time spagetti:
		
		var result_array_heb = new Array();
		var result_array_eng = new Array();
		
		//check if last 3 input words are in english after switching from hebrew to english
		if (tm_hibrishDictionary_he[onlywordsarray[onlywordsarray.length - 1]] && tm_hibrishDictionary_he[onlywordsarray[onlywordsarray.length - 2]] && tm_hibrishDictionary_he[onlywordsarray[onlywordsarray.length - 3]]) {
			
			
			result_array_heb =  onlywordsarray.slice(0,  -3 );
			var trans_array = onlywordsarray.slice(-3);
			trans_array = trans_array.map(function(word) {
				return convertHeb2Eng(word)
				});
			//log('trans_array', trans_array);
			
			result_array_heb = result_array_heb.concat(onlywordsarray.slice(-3).map(function(word) {
				return convertHeb2Eng(word)
			}));
					
			log("detected last 3 words are hebrish, switching text for you..."); //todo: make this configurable from options page
			//log("onlywordsarray",onlywordsarray);
			heb2engOn = true; //flag start transliterating letter by letter
			//log("result_array_heb",result_array_heb);

			result_array_heb =  result_array_heb.join(" ");
			result_array_heb = result_array_heb + ' ';
			//console.log("result_array_heb",result_array_heb);
			leftLines.push(result_array_heb.toString());
			left = leftLines.join('');
			return  left;
			return result_array_heb;
		}
		//log('tm_hibrishDictionary_he',tm_hibrishDictionary_he);
		//log('tm_hibrishDictionary_en',tm_hibrishDictionary_en);
		//log('onlywordsarray',onlywordsarray);
		//log('onlywordsarray[onlywordsarray.length - 1]',onlywordsarray[onlywordsarray.length - 1]);
		//log('tm_hibrishDictionary_en[onlywordsarray[onlywordsarray.length - 1]]',tm_hibrishDictionary_en[onlywordsarray[onlywordsarray.length - 1]]);
		
		//from here we check if typing 3 words in hebrew using the english keyboard:
		if (tm_hibrishDictionary_en['\''+onlywordsarray[onlywordsarray.length - 1]+'\''] && 
			tm_hibrishDictionary_en['\''+onlywordsarray[onlywordsarray.length - 2]+'\''] && 
			tm_hibrishDictionary_en['\''+onlywordsarray[onlywordsarray.length - 3]+'\'']) {
			

			result_array_eng =  onlywordsarray.slice(0,  -3 );
			var trans_array = onlywordsarray.slice(-3);
			trans_array = trans_array.map(function(word) {
				return convertEng2Heb(word)
				});
			result_array_eng = result_array_eng.concat(trans_array);
			
			log("last 3 words are hebrish eng");
			eng2hebOn = true; //flag start transliterating letter by letter

			result_array_eng =  result_array_eng.join(" ");
			result_array_eng = result_array_eng + ' ';

			leftLines.push(result_array_eng.toString());
			left = leftLines.join('');
			return  left;
		}
	};


	// INIT START
	// retrieve rules and options from storage
	chrome.storage.local.get(['rules', 'options', 'customDictionary'], function (items) {
		log("Retrieved from storage:", items);

		// load dic (after loading custom dictionary)
		//loadDic();
		tm_loadHibDic();
		tm_loadEngDic();

	});
	// retrieve language and disabled state from the background page
	sendMessage({
		detectLanguage: null,
		isDisabled: /^https?/.test(location.href) ? location.href : parent.location.href
	});
	// INIT END

	// listen for messages from the background page
	chrome.runtime.onMessage.addListener(handleMessage);

	// on input event
	document.addEventListener('input', function (e) {
		// log('input', e, e.target._spellcheck);
		if (isDisabled || (!e.target._spellcheck &&
				(e.target._spellcheck === false ||
					!(e.target._spellcheck = e.target.tagName != 'INPUT' || e.target.type == 'text'))))
			return;
		var input = e.target;
		var inputData = new InputData(input);
		// log('text.length:', inputData.text.length);
		if (!inputData.text)
			return; // no text

		lastCheck = Date.now(); // prevent cleanup (do before loading dic)
		//if (!dic)
			//return loadDic(); // dic was unloaded meanwhile
		
		if(heb2engOn) {
			var left = inputData.left;
			
			left = left.replace(/.$/,convertHeb2Eng(left[left.length-1])); // translitirate last char in string to english
			
		}else if(eng2hebOn)	{
			var left = inputData.left;
			
			left = left.replace(/.$/,convertEng2Heb(left[left.length-1])); // translitirate last char in string to english
		
		}else{
			var left = spellCheck(inputData.left);
			//add async function version for spellcheck done on the background page?
		}	
		if (left) {
			lastReplace = {
				left: left,
				initialLeft: inputData.left,
				initialText: inputData.text,
				initialCursorPosition: inputData.cursorPosition,
				time: Date.now()
			};
			inputData.setText(left + inputData.right);
			inputData.setCursorPosition(left.length);
		}
	}, true);

	// ctrl+z or backspace
	document.addEventListener('keydown', function (e) {
		// log('keydown', e);
		if (e.ctrlKey ? e.keyCode == 90 : e.keyCode == 8) { // ctrl+z || backspace
			if (lastReplace) {
				if (lastReplace.time < Date.now() - 5000) {
					log("Ignoring undo: last correction was too long ago.");
					lastReplace = null;
				} else {
					var inputData = new InputData(e.target);
					var undo = function (text, cursorPosition) {
						log('Undoing: "' + inputData.text + '" -> "' + text + '".');
						inputData.setText(text);
						inputData.setCursorPosition(cursorPosition);
						lastReplace = null;
						e.preventDefault();
					};
					if (e.ctrlKey)
						undo(lastReplace.initialText, lastReplace.initialCursorPosition);
					else if (lastReplace.left == inputData.left) {
						undo(lastReplace.initialLeft.slice(0, -1) + inputData.right, lastReplace.initialCursorPosition - 1);
					}
				}
			}
		}
		//todo: also disable transliteration flags when losing and gettign focus of textarea or tab
		if(e.altKey && e.shiftKey) {
			if (heb2engOn || eng2hebOn) {
				heb2engOn = false;
				eng2hebOn = false;
				log('detected alt+shift, cancelling auto hibrish.');
			}
		}
	});

})();
