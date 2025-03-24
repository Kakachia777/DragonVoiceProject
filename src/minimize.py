import os
import time

try:
    import win32gui
    import win32con
    PYWIN32_AVAILABLE = True
except ImportError:
    PYWIN32_AVAILABLE = False
    print("pywin32 is not installed. Please install it: pip install pywin32")

def minimize_vscode_windows(title_pattern="Cursor", specific_title="windows.py - DragonVoiceProject - Cursor"):
    """Minimizes VS Code windows using pywin32."""

    print(f"Attempting to minimize VS Code windows...")

    if not PYWIN32_AVAILABLE:
        print("pywin32 is not available. Cannot minimize windows.")
        return

    def window_enum_handler(hwnd, result_list):
        """Callback function for EnumWindows."""
        title = win32gui.GetWindowText(hwnd)
        if title_pattern in title or specific_title in title:
            result_list.append((hwnd, title))

    try:
        print("Trying pywin32 method...")
        windows = []
        win32gui.EnumWindows(window_enum_handler, windows)

        if windows:
            for hwnd, title in windows:
                print(f"Minimizing window: '{title}' (HWND: {hwnd})")
                win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
            print(f"Minimized {len(windows)} VS Code window(s) using pywin32.")
        else:
            print("No VS Code windows found with pywin32.")

    except Exception as e:
        print(f"Error using pywin32: {e}")

if __name__ == "__main__":
    minimize_vscode_windows()
    input("Press Enter to exit...")