# auto_clicker.py
import time
import threading
import pyautogui
from pynput.keyboard import Listener, Key

# --- CONFIGURATION: SET YOUR COORDINATES HERE ---
# Replace (x, y) with the coordinates you found using get_mouse_position.py
POSITION_1 = (4523, 643)   # First click position (x1, y1)
POSITION_2 = (4471, 941)  # Second click position (x2, y2)
CLICK_INTERVAL = 2       # Time in seconds between clicks

# --- SCRIPT LOGIC ---
# This flag will be used to stop the clicking thread
clicking_enabled = True

def clicker():
    """The main clicking function, runs in a separate thread."""
    print("Starting the auto-clicker. Press 'Esc' to stop.")
    while clicking_enabled:
        # Click at the first position
        pyautogui.moveTo(POSITION_1, duration=0.2)
        pyautogui.click()
        print(f"Clicked at Position 1: {POSITION_1}")
        
        # Wait for the interval, but check frequently if we need to stop
        for _ in range(int(CLICK_INTERVAL * 10)):
            if not clicking_enabled:
                break
            time.sleep(0.1)
        if not clicking_enabled:
            break

        # Click at the second position
        pyautogui.moveTo(POSITION_2, duration=0.2)
        pyautogui.click()
        print(f"Clicked at Position 2: {POSITION_2}")

        # Wait again
        for _ in range(int(CLICK_INTERVAL * 10)):
            if not clicking_enabled:
                break
            time.sleep(0.1)

    print("Auto-clicker thread has stopped.")

def on_press(key):
    """Listens for the 'Esc' key to stop the script."""
    global clicking_enabled
    if key == Key.esc:
        print("'Esc' key pressed. Stopping auto-clicker...")
        clicking_enabled = False
        # Stop the listener
        return False

def main():
    # Start the key listener in a separate thread
    listener = Listener(on_press=on_press)
    listener.start()

    # Start the clicking function in another thread
    click_thread = threading.Thread(target=clicker)
    click_thread.start()

    # Wait for the threads to complete
    click_thread.join()
    listener.join()

    print("Script has finished.")

if __name__ == "__main__":
    # Add a small delay before starting to give the user time to prepare
    print("Auto-clicker will start in 3 seconds. You can stop it by pressing 'Esc'.")
    time.sleep(3)
    main()