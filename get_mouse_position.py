# get_mouse_position.py
from pynput import mouse, keyboard

print("Click on the screen to get mouse position. Press 'q' or Ctrl-C to quit.")

def on_click(x, y, button, pressed):
    """Callback function to handle mouse click events."""
    if pressed:  # Action on mouse button press
        positionStr = f'X: {str(x).rjust(4)} Y: {str(y).rjust(4)}'
        print(positionStr)

def on_key_press(key, mouse_listener_instance):
    """Callback function to handle key press events."""
    try:
        if key.char == 'q':
            print("\n'q' pressed, stopping listeners...")
            if mouse_listener_instance:
                mouse_listener_instance.stop()  # Stop the mouse listener
            return False  # Stop the keyboard listener itself
    except AttributeError:
        # This is a special key (e.g. shift, ctrl, alt), not 'q'.
        pass

try:
    # Set up listeners for mouse and keyboard events
    # The 'with' statements ensure listeners are properly managed (started and stopped)
    with mouse.Listener(on_click=on_click) as m_listener:
        # Create a lambda function for the keyboard callback.
        # This lambda takes the key event (and any other potential args from pynput via *other_args)
        # and calls on_key_press with the key and the m_listener instance.
        keyboard_event_handler = lambda key_arg, *other_args: on_key_press(key_arg, m_listener)
        
        with keyboard.Listener(on_press=keyboard_event_handler) as k_listener:
            # Both listeners are now running.
            # Keep the script running by joining the mouse listener.
            # If 'q' is pressed, m_listener.stop() is called, and m_listener.join() will return.
            # k_listener is stopped by on_key_press returning False.
            m_listener.join()
except KeyboardInterrupt:
    print('\nDone.')
    # Listeners are stopped automatically by their 'with' statement's __exit__ method
    # when a KeyboardInterrupt occurs or the block finishes normally.