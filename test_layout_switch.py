import sys
import time
import win32api
import win32con
import win32gui
import win32process
import ctypes
import os
import threading
import pystray
import webbrowser
from PIL import Image, ImageDraw

# English and Hebrew full HKL strings (US English: 00000409, Hebrew: 0000040d)
EN_HKL = '00000409'
HE_HKL = '0000040d'
EN_ID = '0409'
HE_ID = '040d'

# Helper to get the current keyboard layout
def get_foreground_keyboard_layout():
    hwnd = win32gui.GetForegroundWindow()
    thread_id = win32process.GetWindowThreadProcessId(hwnd)[0]
    layout = win32api.GetKeyboardLayout(thread_id)
    lang_id = f"{layout & 0xFFFF:04x}"
    return lang_id

def print_current_layout():
    current = get_foreground_keyboard_layout()
    print(f"[INFO] Current layout: {current}")

def method1_activate_keyboard_layout_full_hkl(hkl_str):
    print(f"[TEST] Method 1: ctypes.windll.user32.ActivateKeyboardLayout(full HKL {hkl_str}) with KLF_ACTIVATE")
    hkl = win32api.LoadKeyboardLayout(hkl_str, 0x00000001)  # KLF_ACTIVATE
    result = ctypes.windll.user32.ActivateKeyboardLayout(hkl, 0x00000001)  # KLF_ACTIVATE
    print(f"[DEBUG] Loaded HKL: {hkl}, Activate result: {result}")
    time.sleep(0.5)
    print_current_layout()

def method2_send_message_full_hkl(hkl_str):
    print(f"[TEST] Method 2: win32gui.SendMessage(WM_INPUTLANGCHANGEREQUEST, 0, full HKL {hkl_str})")
    hwnd = win32gui.GetForegroundWindow()
    hkl = win32api.LoadKeyboardLayout(hkl_str, 0x00000001)
    win32gui.SendMessage(hwnd, 0x0050, 0, hkl)  # WM_INPUTLANGCHANGEREQUEST
    print(f"[DEBUG] Loaded HKL: {hkl}")
    time.sleep(0.5)
    print_current_layout()

def method3_post_message_w_full_hkl(hkl_str):
    print(f"[TEST] Method 3: ctypes.windll.user32.PostMessageW(WM_INPUTLANGCHANGEREQUEST, 0, full HKL {hkl_str})")
    hwnd = win32gui.GetForegroundWindow()
    hkl = win32api.LoadKeyboardLayout(hkl_str, 0x00000001)
    ctypes.windll.user32.PostMessageW(hwnd, 0x0050, 0, hkl)
    print(f"[DEBUG] Loaded HKL: {hkl}")
    time.sleep(0.5)
    print_current_layout()

def create_tray_icon(on_details_callback, on_quit_callback):
    # Simple black/white icon
    image = Image.new('RGB', (64, 64), color='white')
    d = ImageDraw.Draw(image)
    d.rectangle([16, 16, 48, 48], fill='black')

    def open_coffee(icon, item):
        webbrowser.open(COFFEE_LINK)

    menu = (
        item('Details', on_details_callback),
        item('Buy me a coffee', open_coffee),
        item('Quit', on_quit_callback),
    )
    return image, menu

def main():
    if len(sys.argv) != 2 or sys.argv[1] not in {'1', '2', '3'}:
        print("Usage: python test_layout_switch.py [method]  # method = 1, 2, or 3")
        print("  1: ActivateKeyboardLayout (ctypes)")
        print("  2: SendMessage (win32gui)")
        print("  3: PostMessageW (ctypes)")
        sys.exit(1)
    method = sys.argv[1]
    print("[INFO] Initial layout:")
    print_current_layout()
    input(f"\nPress Enter to switch to Hebrew using method {method}...\n")
    print(f"\n--- Switching to Hebrew (0000040d) using method {method} ---\n")
    if method == '1':
        method1_activate_keyboard_layout_full_hkl(HE_HKL)
    elif method == '2':
        method2_send_message_full_hkl(HE_HKL)
    elif method == '3':
        method3_post_message_w_full_hkl(HE_HKL)
    input(f"\nPress Enter to switch to English using method {method}...\n")
    print(f"\n--- Switching to English (00000409) using method {method} ---\n")
    if method == '1':
        method1_activate_keyboard_layout_full_hkl(EN_HKL)
    elif method == '2':
        method2_send_message_full_hkl(EN_HKL)
    elif method == '3':
        method3_post_message_w_full_hkl(EN_HKL)
    print("\n[INFO] Test complete. Please report which method worked.")

if __name__ == "__main__":
    # System tray icon with Details and Quit option
    tray_quit = lambda icon, item: os._exit(0)
    tray_image, tray_menu = create_tray_icon(on_details, tray_quit)
    icon = pystray.Icon("LangSwitch", tray_image, "LangSwitch", tray_menu)
    tray_thread = threading.Thread(target=icon.run, daemon=True)
    tray_thread.start()
    main() 