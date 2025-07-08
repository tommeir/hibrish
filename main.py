import os
import sys
import requests
import win32api
import win32con
import win32gui
#import win32clipboard  # Unused
import keyboard
from pathlib import Path
from spellchecker import SpellChecker
import json
import threading
import time
import pystray
from PIL import Image, ImageDraw
import html
import re
import ctypes
import win32process
import collections
import functools

VERBOSE = '-v' in sys.argv

def debug_print(*args, **kwargs):
    if VERBOSE:
        print(*args, **kwargs)

# Constants
GITHUB_DICT_BASE = "https://raw.githubusercontent.com/wooorm/dictionaries/main/dictionaries/"
GITHUB_DICT_LIST = "https://api.github.com/repos/wooorm/dictionaries/contents/dictionaries"
DICTIONARY_DIR = Path("dictionaries")
WORD_BUFFER_SIZE = 4  # Always check the last 4 words
MIN_INVALID_WORDS = 3  # Minimum invalid words before suggesting correction
UNDO_HOTKEY = 'ctrl+z'
ADD_WORD_HOTKEY = 'ctrl+shift+a'

# Helper to get installed keyboard layouts
def get_installed_keyboard_layouts():
    layouts = win32api.GetKeyboardLayoutList()
    langs = set()
    for layout in layouts:
        lang_id = f"{layout & 0xFFFF:04x}"
        langs.add(lang_id)
    return list(langs)

# Helper to fetch available dictionary folders from wooorm/dictionaries
def fetch_available_dictionaries():
    try:
        r = requests.get(GITHUB_DICT_LIST)
        if r.status_code == 200:
            data = r.json()
            return set(entry['name'] for entry in data if entry['type'] == 'dir')
        else:
            print(f"Failed to fetch dictionary list: {r.status_code}")
            return set()
    except Exception as e:
        print(f"Error fetching dictionary list: {e}")
        return set()

# Helper to map Windows lang code to dictionary folder
def lang_id_to_dict_folder(lang_id):
    lang_map = {
        '0409': 'en',      # English (United States)
        '0809': 'en-GB',   # English (United Kingdom)
        '0c0a': 'es',      # Spanish (Spain)
        '0410': 'it',      # Italian
        '040c': 'fr',      # French
        '0419': 'ru',      # Russian
        '0407': 'de',      # German
        '040d': 'he',      # Hebrew
        '0413': 'nl',      # Dutch
        '0415': 'pl',      # Polish
        '0416': 'pt',      # Portuguese (Brazil)
        '0816': 'pt-PT',   # Portuguese (Portugal)
        '041e': 'th',      # Thai
        '041f': 'tr',      # Turkish
        '0421': 'id',      # Indonesian
        '0422': 'uk',      # Ukrainian
        '0424': 'sl',      # Slovenian
        '0427': 'lt',      # Lithuanian
        '0429': 'fa',      # Persian
        '042d': 'eu',      # Basque
        '042f': 'mk',      # Macedonian
        '0436': 'af',      # Afrikaans
        '0438': 'fo',      # Faroese
        '0439': 'hi',      # Hindi
        '043a': 'mt',      # Maltese
        '043b': 'se',      # Sami (Northern)
        '043e': 'ms',      # Malay
        '0443': 'uz',      # Uzbek (Latin)
        '0445': 'bn',      # Bengali
        '0446': 'pa',      # Punjabi
        '0447': 'gu',      # Gujarati
        '0449': 'ta',      # Tamil
        '044a': 'te',      # Telugu
        '044b': 'kn',      # Kannada
        '044c': 'ml',      # Malayalam
        '044d': 'as',      # Assamese
        '044e': 'mr',      # Marathi
        '044f': 'sa',      # Sanskrit
        '0450': 'mn',      # Mongolian
        '0456': 'gl',      # Galician
        '0457': 'kok',     # Konkani
        '045a': 'syr',     # Syriac
        '045b': 'si',      # Sinhala
        '045c': 'chr',     # Cherokee
        '045d': 'iu',      # Inuktitut
        '0461': 'ne',      # Nepali
        '0465': 'div',     # Divehi
        '0468': 'ha',      # Hausa
        '046a': 'yo',      # Yoruba
        '046b': 'quz',     # Quechua
        '046c': 'ns',      # Northern Sotho
        '046d': 'ba',      # Bashkir
        '046e': 'lb',      # Luxembourgish
        '046f': 'kl',      # Greenlandic
        '0470': 'ig',      # Igbo
        '0478': 'ii',      # Yi
        '047a': 'arn',     # Mapudungun
        '047c': 'moh',     # Mohawk
        '047e': 'br',      # Breton
        '0480': 'ug',      # Uighur
        '0481': 'mi',      # Maori
        '0482': 'oc',      # Occitan
        '0483': 'co',      # Corsican
        '0484': 'gsw',     # Alsatian
        '0485': 'sah',     # Yakut
        '0486': 'qut',     # K'iche'
        '0487': 'rw',      # Kinyarwanda
        '0488': 'wo',      # Wolof
        '048c': 'prs',     # Dari
    }
    if lang_id in lang_map:
        return lang_map[lang_id]
    fallback = lang_id[-2:]
    return fallback

# Helper to download wordlist from wooorm/dictionaries
def download_wordlist(folder):
    DICTIONARY_DIR.mkdir(exist_ok=True)
    dic_url = f"{GITHUB_DICT_BASE}{folder}/index.dic"
    dic_path = DICTIONARY_DIR / f"{folder}.dic"
    if not dic_path.exists():
        print(f"Downloading {dic_url}...")
        r = requests.get(dic_url)
        if r.status_code == 200:
            with open(dic_path, "wb") as f:
                f.write(r.content)
        else:
            print(f"Failed to download {dic_url}")
    return dic_path.exists()

# Load wordlist into pyspellchecker
def load_spellchecker(folder):
    dic_path = DICTIONARY_DIR / f"{folder}.dic"
    if not dic_path.exists():
        return None
    with open(dic_path, encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
    if lines and lines[0].strip().isdigit():
        lines = lines[1:]
    words = [line.strip().split("/")[0].lower() for line in lines if line.strip() and not line.startswith("#")]
    spell = SpellChecker(language=None)
    spell.word_frequency.load_words(words)
    return spell

def get_foreground_keyboard_layout():
    try:
        hwnd = win32gui.GetForegroundWindow()
        thread_id = win32process.GetWindowThreadProcessId(hwnd)[0]
        layout = win32api.GetKeyboardLayout(thread_id)
        lang_id = f"{layout & 0xFFFF:04x}"
        return lang_id
    except Exception as e:
        debug_print(f"[ERROR] Failed to get foreground keyboard layout: {e}")
        return None

# Helper to switch Windows keyboard layout robustly
def switch_keyboard_layout(lang_id, folder=None):
    try:
        import win32gui
        hwnd = win32gui.GetForegroundWindow()
        # Use full 8-digit HKL string
        hkl_str = f"0000{lang_id}" if len(lang_id) == 4 else lang_id
        hkl = win32api.LoadKeyboardLayout(hkl_str, 0x00000001)  # KLF_ACTIVATE
        debug_print(f"[DEBUG] Switching keyboard layout to lang_id={lang_id}, folder={folder}, hkl_str={hkl_str}, hkl={hkl}")
        win32gui.SendMessage(hwnd, 0x0050, 0, hkl)  # WM_INPUTLANGCHANGEREQUEST
        # Verification: print the current layout after switching
        current_layout = get_foreground_keyboard_layout()
        debug_print(f"[DEBUG] Current layout after switch: {current_layout}")
    except Exception as e:
        debug_print(f"[ERROR] Failed to switch keyboard layout: {e}")

# Helper to replace last N words in the active text field (simulate backspaces and typing)
def replace_last_words(words, replacement_words):
    # Simulate backspaces for each word and space
    for word in words:
        for _ in range(len(word)):
            keyboard.send('backspace')
        keyboard.send('backspace')  # for the space
    # Type replacement words
    for word in replacement_words:
        keyboard.write(word)
        keyboard.write(' ')

def sanitize_word(word):
    # Remove non-printable, control, and suspicious characters (but do not escape to HTML)
    word = re.sub(r'[^\w\u0590-\u05FF\u0600-\u06FF\-\'\".,;!?/\\\[\]]+', '', word)
    return word

# English to Hebrew keyboard mapping (US QWERTY to Hebrew standard, lowercase only)
EN_TO_HE = {
    'a': 'ש', 'b': 'נ', 'c': 'ב', 'd': 'ג', 'e': 'ק', 'f': 'כ', 'g': 'ע', 'h': 'י', 'i': 'ן', 'j': 'ח', 'k': 'ל', 'l': 'ך', 'm': 'צ',
    'n': 'מ', 'o': 'ם', 'p': 'פ', 'q': '/', 'r': 'ר', 's': 'ד', 't': 'א', 'u': 'ו', 'v': 'ה', 'w': '\'', 'x': 'ס', 'y': 'ט', 'z': 'ז',
    '`': ';', '1': '1', '2': '2', '3': '3', '4': '4', '5': '5', '6': '6', '7': '7', '8': '8', '9': '9', '0': '0', '-': '-', '=': '=',
    ',': 'ת', '.': 'ץ', '/': '.', ';': 'ף', '\\': '.', "'": ',', '[': ']', ']': '[',
    # Add more as needed
}
# Reverse mapping for Hebrew to English (lowercase only)
HE_TO_EN = {v: k for k, v in EN_TO_HE.items()}

# Transliterate a word from one layout to another
def transliterate_word(word, from_lang, to_lang):
    # Always use lowercase for mapping unless char is a digit or special
    def map_char(c):
        if c.isalpha():
            return EN_TO_HE.get(c.lower(), c) if from_lang == 'en' and to_lang == 'he' else HE_TO_EN.get(c, c)
        else:
            return EN_TO_HE.get(c, c) if from_lang == 'en' and to_lang == 'he' else HE_TO_EN.get(c, c)
    if from_lang == 'en' and to_lang == 'he':
        return ''.join(map_char(c) for c in word)
    elif from_lang == 'he' and to_lang == 'en':
        return ''.join(map_char(c) for c in word)
    else:
        return word  # No mapping available

def debug_transliteration(word, from_lang, to_lang):
    print(f"Debugging transliteration for '{word}' from {from_lang} to {to_lang}:")
    if from_lang == 'en' and to_lang == 'he':
        for c in word:
            mapped = EN_TO_HE.get(c, None)
            print(f"  '{c}' -> '{mapped}'")
    elif from_lang == 'he' and to_lang == 'en':
        for c in word:
            mapped = HE_TO_EN.get(c, None)
            print(f"  '{c}' -> '{mapped}'")
    else:
        print("  No mapping available.")

# System tray icon setup
def create_tray_icon():
    # Simple black/white icon
    image = Image.new('RGB', (64, 64), color='white')
    d = ImageDraw.Draw(image)
    d.rectangle([16, 16, 48, 48], fill='black')
    return image

def show_notification(msg):
    print(f"[NOTIFY] {msg}")
    # For real notifications, use win10toast or similar

# Main word detection and correction logic
def detect_and_correct_words(spellcheckers, lang_ids, lang_id_to_folder):
    word_buffer = collections.deque(maxlen=WORD_BUFFER_SIZE)
    word_lang_buffer = collections.deque(maxlen=WORD_BUFFER_SIZE)
    current_word = ''
    last_correction = None
    current_lang_id = lang_ids[0]
    current_lang = lang_id_to_folder[current_lang_id]
    debug_print("\n[Typing monitor started. Type words, press space to finish a word. Press ESC to exit.")
    exit_flag = threading.Event()

    # Add LRU cache for word validity checks
    @functools.lru_cache(maxsize=256)
    def is_valid_word(word, lang):
        return word in spellcheckers[lang]

    def on_key(event):
        nonlocal current_word, word_buffer, word_lang_buffer, last_correction, current_lang_id, current_lang
        # Always detect the real current keyboard layout
        detected_lang_id = get_foreground_keyboard_layout()
        if detected_lang_id in lang_id_to_folder:
            current_lang_id = detected_lang_id
            current_lang = lang_id_to_folder[detected_lang_id]
        if event.event_type == 'down':
            if event.name == 'space' or event.name == 'enter':
                if current_word:
                    safe_word = sanitize_word(current_word)
                    word_buffer.append(safe_word)
                    word_lang_buffer.append(current_lang_id)
                    if len(word_buffer) > WORD_BUFFER_SIZE:
                        word_buffer.pop(0)
                        word_lang_buffer.pop(0)
                    buffer_words = [w.lower() for w in list(word_buffer)]
                    spell_set = set(spellcheckers[current_lang].word_frequency._dictionary.keys())
                    valid_words = set(buffer_words) & spell_set
                    valid_in_current = len(valid_words)
                    invalid_count = len(buffer_words) - valid_in_current
                    debug_print(f"[DEBUG] Buffer: {buffer_words}")
                    debug_print(f"[DEBUG] Invalid words in current lang ({current_lang}): {invalid_count} / {WORD_BUFFER_SIZE}")
                    debug_print(f"[DEBUG] Valid in current lang ({current_lang}): {valid_in_current}")
                    if invalid_count >= 3:
                        # Try other languages
                        for lang, spell in spellcheckers.items():
                            if lang == current_lang:
                                continue
                            transliterated = [transliterate_word(w.lower(), current_lang, lang) for w in word_buffer]
                            spell_set_other = set(spellcheckers[lang].word_frequency._dictionary.keys())
                            valid_words_other = set(transliterated) & spell_set_other
                            valid_in_other = len(valid_words_other)
                            debug_print(f"[DEBUG] Checking {lang}: transliterated={transliterated}, valid_in_{lang}={valid_in_other}, valid_in_current={valid_in_current}")
                            if valid_in_other > valid_in_current and valid_in_other >= 3:
                                show_notification(f"Auto-correcting to {lang} and switching keyboard layout. Replacing: {list(word_buffer)} -> {transliterated}")
                                # Find lang_id for this lang
                                for lid, folder in lang_id_to_folder.items():
                                    if folder == lang:
                                        debug_print(f"[DEBUG] Switching layout to {lang} (lang_id={lid}) after correction.")
                                        current_lang_id = lid
                                        current_lang = lang
                                        switch_keyboard_layout(lid, folder)
                                        break
                                # Replace the entire buffer
                                replace_last_words(list(word_buffer), transliterated)
                                last_correction = (list(word_buffer), current_lang_id)
                                # Clear the buffer after correction
                                word_buffer.clear()
                                word_lang_buffer.clear()
                                break
                current_word = ''
            elif event.name == 'backspace':
                current_word = current_word[:-1]
            elif len(event.name) == 1:
                current_word += event.name
            elif event.name == 'esc':
                exit_flag.set()
        # Undo hotkey
        if event.name == 'z' and keyboard.is_pressed('ctrl'):
            if last_correction:
                words, prev_lang_id = last_correction
                show_notification("Undoing last correction.")
                switch_keyboard_layout(prev_lang_id, lang_id_to_folder.get(prev_lang_id))
                replace_last_words(words, words)
                last_correction = None
        # Add word hotkey
        if event.name == 'a' and keyboard.is_pressed('ctrl') and keyboard.is_pressed('shift'):
            if word_buffer:
                word = word_buffer[-1]
                show_notification(f"Adding '{word}' to dictionary for {current_lang}.")
                spellcheckers[current_lang].word_frequency.add(word)

    keyboard.hook(on_key)
    while not exit_flag.is_set():
        time.sleep(0.1)
    keyboard.unhook_all()

def test_transliteration():
    # Test 1: 'akuo' -> 'שלום'
    test1 = 'akuo'
    expected1 = 'שלום'
    result1 = transliterate_word(test1, 'en', 'he')
    print(f"Test 1: '{test1}' -> '{result1}' (expected: '{expected1}') {'PASS' if result1 == expected1 else 'FAIL'}")
    debug_transliteration(test1, 'en', 'he')
    print()

    # Test 2: 'akuo akuo akuo akuo' -> 'שלום שלום שלום שלום'
    test2 = 'akuo akuo akuo akuo'
    expected2 = 'שלום שלום שלום שלום'
    result2 = ' '.join([transliterate_word(w, 'en', 'he') for w in test2.split()])
    print(f"Test 2: '{test2}' -> '{result2}' (expected: '{expected2}') {'PASS' if result2 == expected2 else 'FAIL'}")
    for w in test2.split():
        debug_transliteration(w, 'en', 'he')
    print()

    # Test 3: 'tbh kt nchi knv' -> 'אני לא מבין למה'
    test3 = 'tbh kt nchi knv'
    expected3 = 'אני לא מבין למה'
    result3 = ' '.join([transliterate_word(w, 'en', 'he') for w in test3.split()])
    print(f"Test 3: '{test3}' -> '{result3}' (expected: '{expected3}') {'PASS' if result3 == expected3 else 'FAIL'}")
    for w in test3.split():
        debug_transliteration(w, 'en', 'he')
    print()

    # Test 4: 'ןד' -> 'kt' (hebrew to english)
    test4 = 'ןד'
    expected4 = 'kt'
    result4 = transliterate_word(test4, 'he', 'en')
    print(f"Test 4: '{test4}' -> '{result4}' (expected: '{expected4}') {'PASS' if result4 == expected4 else 'FAIL'}")
    debug_transliteration(test4, 'he', 'en')
    print()

    # Test 5: 'ןד ןד ןד ןד' -> 'kt kt kt kt'
    test5 = 'ןד ןד ןד ןד'
    expected5 = 'kt kt kt kt'
    result5 = ' '.join([transliterate_word(w, 'he', 'en') for w in test5.split()])
    print(f"Test 5: '{test5}' -> '{result5}' (expected: '{expected5}') {'PASS' if result5 == expected5 else 'FAIL'}")
    for w in test5.split():
        debug_transliteration(w, 'he', 'en')
    print()

    # Test 6: 'אני לא מבין למה' -> 'tbh kt nchi knv'
    test6 = 'אני לא מבין למה'
    expected6 = 'tbh kt nchi knv'
    result6 = ' '.join([transliterate_word(w, 'he', 'en') for w in test6.split()])
    print(f"Test 6: '{test6}' -> '{result6}' (expected: '{expected6}') {'PASS' if result6 == expected6 else 'FAIL'}")
    for w in test6.split():
        debug_transliteration(w, 'he', 'en')
    print()

if __name__ == "__main__":
    test_transliteration()
    print("Fetching available dictionaries from repo...")
    available_dicts = fetch_available_dictionaries()
    print(f"Available dictionaries: {sorted(available_dicts)}")

    print("Detecting installed keyboard layouts...")
    layouts = get_installed_keyboard_layouts()
    print(f"Found layouts: {layouts}")
    found_langs = []
    spellcheckers = {}
    lang_id_to_folder = {}
    for lang_id in layouts:
        folder = lang_id_to_dict_folder(lang_id)
        if folder in available_dicts:
            print(f"Preparing wordlist for {folder}...")
            if download_wordlist(folder):
                spell = load_spellchecker(folder)
                if spell:
                    print(f"Wordlist for {folder} ready.")
                    found_langs.append(folder)
                    spellcheckers[folder] = spell
                    lang_id_to_folder[lang_id] = folder
                else:
                    print(f"Could not load wordlist for {folder}.")
            else:
                print(f"Could not prepare wordlist for {folder}.")
        else:
            print(f"No dictionary available for language id {lang_id} (mapped to {folder})")
    if not found_langs:
        print("No supported wordlists found. Exiting.")
        sys.exit(1)
    print(f"Ready with wordlists: {found_langs}")

    # System tray icon
    icon = pystray.Icon("LangSwitch", create_tray_icon(), "LangSwitch")
    tray_thread = threading.Thread(target=icon.run, daemon=True)
    tray_thread.start()

    # Start word detection and correction logic if at least 2 languages are loaded
    if len(spellcheckers) >= 2:
        detect_and_correct_words(spellcheckers, list(lang_id_to_folder.keys()), lang_id_to_folder)
    else:
        print("Not enough languages loaded for correction logic demo.") 

# --- Performance improvement suggestions for production readiness ---
# 1. Use a compiled C extension or optimized library for spellchecking (e.g., native Hunspell bindings).
# 2. Minimize per-keystroke processing; debounce or batch word checks.
# 3. Use a ring buffer or deque for word_buffer for O(1) pops/appends.
# 4. Avoid global interpreter lock (GIL) issues by offloading heavy work to a background thread or process.
# 5. Profile and optimize transliteration and dictionary lookups (e.g., use tries or sets).
# 6. Use native Windows hooks for more efficient keyboard event handling.
# 7. Add error handling/logging for all Windows API calls.
# 8. Consider packaging as a compiled executable for faster startup and lower memory usage. 