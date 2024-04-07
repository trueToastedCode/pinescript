from pynput import keyboard
import threading
import pyperclip

from bracket_formatter import format_text

pressed = []
shortcut = [keyboard.Key.shift, keyboard.Key.cmd, keyboard.KeyCode.from_vk(24)]


def background_task():
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()


def on_press(key):
    global pressed
    pressed.append(key)
    if all(x in pressed for x in shortcut):
        on_shortcut()


def on_release(key):
    global pressed
    try:
        pressed.remove(key)
    except ValueError:
        pass


def on_shortcut():
    try:
        text = pyperclip.paste()
        text = format_text(text)
        pyperclip.copy(text)
    except:
        pass


if __name__ == "__main__":
    background_thread = threading.Thread(target=background_task)
    background_thread.start()
