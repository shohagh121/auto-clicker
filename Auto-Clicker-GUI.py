import tkinter as tk
from tkinter import ttk, messagebox
import pyautogui
import threading
import time
from pynput import keyboard # Changed from 'mouse' to 'keyboard'
import sys

# --- CONFIGURATION & GLOBAL VARIABLES ---
CLICKER_THREAD = None
IS_CLICKING = False
KEYBOARD_LISTENER = None
WIDGET_TO_UPDATE = None

position_widgets = [] # Will be populated dynamically

# --- DPI AWARENESS (FOR WINDOWS DISPLAY SCALING) ---
# This is the key fix for clicks being in the wrong place on scaled displays.
def make_dpi_aware():
    """Makes the application DPI aware on Windows."""
    try:
        if sys.platform == "win32":
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
            print("DPI awareness set for Windows. Coordinates should now be accurate.")
    except Exception as e:
        print(f"Could not set DPI awareness: {e} (This is normal on non-Windows OS)")


# --- AUTO-CLICKER CORE LOGIC ---

def start_clicker_thread(positions, interval):
    """Initializes and starts the auto-clicking thread."""
    global CLICKER_THREAD, IS_CLICKING
    if not positions:
        messagebox.showwarning("No Positions Set", "Please set at least one click position before starting.")
        return

    IS_CLICKING = True
    CLICKER_THREAD = threading.Thread(target=clicker_loop, args=(positions, interval), daemon=True)
    CLICKER_THREAD.start()
    update_status("Clicking started... Press 'Stop' to end.")
    # Disable start button, enable stop button
    start_button.config(state=tk.DISABLED)
    stop_button.config(state=tk.NORMAL)
    num_positions_dropdown.config(state=tk.DISABLED)
    # Disable position setting while clicking
    for pos_item in position_widgets:
        pos_item["set_button"].config(state=tk.DISABLED)
        pos_item["clear_button"].config(state=tk.DISABLED)

def stop_clicker_thread():
    """Stops the auto-clicking thread."""
    global IS_CLICKING
    if IS_CLICKING:
        IS_CLICKING = False
        update_status("Stopped. Ready to start again.")
        # Enable start button, disable stop button
        start_button.config(state=tk.NORMAL)
        stop_button.config(state=tk.DISABLED)
        num_positions_dropdown.config(state=tk.NORMAL)
        # Re-enable position setting
        for pos_item in position_widgets:
            pos_item["set_button"].config(state=tk.NORMAL)
            pos_item["clear_button"].config(state=tk.NORMAL)

def clicker_loop(positions, interval):
    """The main loop for the auto-clicker."""
    while IS_CLICKING:
        for pos in positions:
            if not IS_CLICKING:
                break
            try:
                x, y = pos
                pyautogui.moveTo(x, y, duration=0.2)
                pyautogui.click()
                print(f"Clicked at {pos}")
                for _ in range(int(interval * 20)):
                    if not IS_CLICKING:
                        break
                    time.sleep(0.05)
            except Exception as e:
                print(f"Error during click: {e}")
                pass
    print("Clicker thread finished.")

# --- MOUSE POSITION CAPTURE LOGIC (NOW USING KEYBOARD) ---

def on_hotkey_press(key):
    """Callback for the keyboard listener to capture position with F9."""
    global WIDGET_TO_UPDATE, KEYBOARD_LISTENER
    
    # Check if the F9 key was pressed
    if key == keyboard.Key.f9:
        x, y = pyautogui.position() # Use pyautogui to get position for consistency
        
        if WIDGET_TO_UPDATE:
            # Safely schedule the GUI update on the main thread
            app.after(0, update_entry_widget, WIDGET_TO_UPDATE, f"{x}, {y}")
        
        # Restore the main window
        app.after(0, app.deiconify)
        app.after(0, update_status, f"Set position to ({x}, {y}). Ready.")
        
        # Stop and clean up the listener
        if KEYBOARD_LISTENER:
            KEYBOARD_LISTENER.stop()
            KEYBOARD_LISTENER = None
        return False # This stops the listener thread
    return True

def update_entry_widget(entry_widget, text):
    """Helper function to update a widget from any thread."""
    entry_widget.config(state=tk.NORMAL)
    entry_widget.delete(0, tk.END)
    entry_widget.insert(0, text)
    entry_widget.config(state='readonly')


def capture_position(button_widget):
    """Hides the window and starts listening for the F9 key."""
    global WIDGET_TO_UPDATE, KEYBOARD_LISTENER
    
    # Store the entry widget that needs to be updated
    WIDGET_TO_UPDATE = button_widget.master.children['!entry']
    
    update_status("Move mouse to position and press F9 to capture...")
    app.iconify()  # Hide the main window
    
    # Using a short delay to ensure window is hidden before listener starts
    # Start the listener in a non-daemon thread to ensure it's handled cleanly
    def start_listener():
        global KEYBOARD_LISTENER
        KEYBOARD_LISTENER = keyboard.Listener(on_press=on_hotkey_press)
        KEYBOARD_LISTENER.start()
        KEYBOARD_LISTENER.join() # Wait for the listener to stop

    threading.Thread(target=start_listener).start()


def clear_position(entry_widget):
    """Clears a single position entry."""
    entry_widget.config(state=tk.NORMAL)
    entry_widget.delete(0, tk.END)
    entry_widget.insert(0, "Not Set")
    entry_widget.config(state='readonly')

# --- DYNAMIC GUI LOGIC ---

def update_position_fields(event=None):
    """Clear and recreate the position entry fields based on dropdown selection."""
    for widget in positions_frame.winfo_children():
        widget.destroy()
    position_widgets.clear()
    
    try:
        num_to_create = int(num_positions_var.get())
    except (ValueError, tk.TclError):
        num_to_create = 0
        
    for i in range(num_to_create):
        pos_frame = ttk.Frame(positions_frame)
        pos_frame.pack(fill=tk.X, pady=3)
        
        label = ttk.Label(pos_frame, text=f"Pos {i+1}:", width=7)
        label.pack(side=tk.LEFT)
        
        entry = ttk.Entry(pos_frame, width=15, name='!entry')
        entry.insert(0, "Not Set")
        entry.config(state='readonly')
        entry.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

        set_button = ttk.Button(pos_frame, text="Set")
        set_button.config(command=lambda b=set_button: capture_position(b))
        set_button.pack(side=tk.LEFT, padx=(0,5))
        
        clear_button = ttk.Button(pos_frame, text="Clear", width=5)
        clear_button.config(command=lambda e=entry: clear_position(e))
        clear_button.pack(side=tk.LEFT)
        
        position_widgets.append({
            "label": label, "entry": entry, 
            "set_button": set_button, "clear_button": clear_button
        })


# --- GUI SETUP ---
def create_gui():
    global app, start_button, stop_button, interval_entry, status_label
    global positions_frame, num_positions_var, num_positions_dropdown

    app = tk.Tk()
    app.title("Auto-Clicker")
    app.geometry("450x450")
    app.resizable(False, False)

    style = ttk.Style(app)
    style.theme_use('clam') 

    main_frame = ttk.Frame(app, padding="10")
    main_frame.pack(fill=tk.BOTH, expand=True)

    clicker_frame = ttk.LabelFrame(main_frame, text="Clicker Controls", padding="10")
    clicker_frame.pack(fill=tk.X)
    
    top_controls_frame = ttk.Frame(clicker_frame)
    top_controls_frame.pack(fill=tk.X, pady=5)

    ttk.Label(top_controls_frame, text="Interval (s):").pack(side=tk.LEFT)
    interval_entry = ttk.Entry(top_controls_frame, width=5, justify='center')
    interval_entry.insert(0, "3")
    interval_entry.pack(side=tk.LEFT, padx=(5, 20))

    ttk.Label(top_controls_frame, text="Number of Positions:").pack(side=tk.LEFT)
    num_positions_var = tk.StringVar()
    num_positions_dropdown = ttk.Combobox(
        top_controls_frame, textvariable=num_positions_var, 
        values=[str(i) for i in range(1, 11)], state="readonly", width=4
    )
    num_positions_dropdown.pack(side=tk.LEFT, padx=5)
    num_positions_dropdown.set("2")
    num_positions_dropdown.bind("<<ComboboxSelected>>", update_position_fields)

    positions_frame = ttk.LabelFrame(clicker_frame, text="Click Positions", padding="10")
    positions_frame.pack(fill=tk.X, pady=10)

    update_position_fields()

    controls_frame = ttk.Frame(clicker_frame)
    controls_frame.pack(fill=tk.X, pady=(10,0))

    start_button = ttk.Button(controls_frame, text="Start Clicking", command=lambda: start_clicker_thread(
        get_active_positions(), float(interval_entry.get() or 1)
    ))
    start_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0,5))

    stop_button = ttk.Button(controls_frame, text="Stop Clicking", command=stop_clicker_thread, state=tk.DISABLED)
    stop_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(5,0))
    
    status_label = ttk.Label(main_frame, text="Ready. Click 'Set' to capture a mouse position.", relief=tk.SUNKEN, anchor=tk.W, padding=5)
    status_label.pack(side=tk.BOTTOM, fill=tk.X, pady=(10,0), ipady=2)
    
    app.protocol("WM_DELETE_WINDOW", on_closing)
    app.mainloop()

def on_closing():
    global IS_CLICKING
    if IS_CLICKING:
        IS_CLICKING = False
        time.sleep(0.1)
    app.destroy()

def get_active_positions():
    positions = []
    for item in position_widgets:
        coords_str = item["entry"].get()
        if "Not Set" not in coords_str:
            try:
                x_str, y_str = coords_str.split(',')
                positions.append((int(x_str.strip()), int(y_str.strip())))
            except ValueError:
                print(f"Skipping invalid coordinate entry: {coords_str}")
    return positions

def update_status(text):
    status_label.config(text=text)
    app.update_idletasks()


if __name__ == "__main__":
    make_dpi_aware()
    create_gui()
