import typing as tp
import time
import threading
import sys
from PyQt6 import QtCore as qtc, QtWidgets as qtw, QtGui as qtg

AlignFlag = qtc.Qt.AlignmentFlag
flag = False
alt_pressed = False


def get_pynput():
    from pynput.mouse import Button, Controller
    from pynput import keyboard as kb

    return Button, Controller, kb


def start_clicking() -> tp.NoReturn:
    global flag
    if flag:
        return
    flag = True

    invoke_gui_in_another_thread(status_text, "setText", str, "🟢 Clicking...")
    invoke_gui_in_another_thread(
        status_text, "setStyleSheet", str, "color: #4CAF50; font-weight: bold;"
    )
    button = Button.left if button_selection.currentIndex() == 0 else Button.right
    interval_text = click_interval.text()

    try:
        interval_value = float(interval_text)
    except ValueError:
        interval_value = None

    if interval_value is not None and interval_value > 0:
        is_milliseconds = interval_type.currentIndex() != 0
        interval = interval_value / 1000 if is_milliseconds else interval_value
        interval = max(0.001, interval)
        while flag:
            mouse.click(button)
            time.sleep(interval)
    else:
        flag = False
        invoke_gui_in_another_thread(
            status_text,
            "setText",
            str,
            "⚠️ Error: Invalid interval value, enter a positive non-zero number.",
        )
        update_buttons()


def stop_clicking() -> tp.NoReturn:
    global flag
    flag = False
    invoke_gui_in_another_thread(status_text, "setText", str, "🔴 Stopped")
    invoke_gui_in_another_thread(
        status_text, "setStyleSheet", str, "color: #E53935; font-weight: bold;"
    )


def invoke_gui_in_another_thread(
    widget: qtc.QObject, method: str, arg_type: tp.Any, arg_data: tp.Any
) -> tp.NoReturn:
    qtc.QMetaObject.invokeMethod(widget, method, qtc.Q_ARG(arg_type, arg_data))


def toggle_click() -> tp.NoReturn:
    global flag
    if flag:
        stop_clicking()
    else:
        threading.Thread(target=start_clicking, daemon=True).start()
    update_buttons()


def update_buttons() -> tp.NoReturn:
    if flag:
        start_button.setEnabled(False)
        stop_button.setEnabled(True)
    else:
        start_button.setEnabled(True)
        stop_button.setEnabled(False)


def on_press(key) -> tp.NoReturn:
    global alt_pressed
    if key == kb.Key.alt_l:
        alt_pressed = True
    try:
        if alt_pressed and key.char == "s":
            toggle_click()
    except AttributeError:
        pass


def on_release(key) -> tp.NoReturn:
    global alt_pressed
    if key == kb.Key.alt_l:
        alt_pressed = False


if __name__ == "__main__":
    app = qtw.QApplication(sys.argv)

    Button, Controller, kb = get_pynput()
    mouse = Controller()

    window = qtw.QWidget()
    window.setWindowTitle("⚡ Otoklikor")
    window.setFixedSize(720, 480)
    window.setStyleSheet(
        """
        QPushButton {
            padding: 10px;
        }
        QPushButton:hover {
            background-color: #3E3E42;
        }
        """
    )

    root_layout = qtw.QVBoxLayout()
    head_layout = qtw.QVBoxLayout()

    interval_layout = qtw.QHBoxLayout()
    button_selection_layout = qtw.QHBoxLayout()

    interval_label = qtw.QLabel("Click Interval:")
    interval_label.setStyleSheet("font-weight: bold;")

    interval_type = qtw.QComboBox()
    interval_type.addItems(["Seconds (s)", "Milliseconds (ms)"])

    click_interval = qtw.QLineEdit()
    click_interval.setPlaceholderText("Click speed. (lesser = faster)")
    click_interval.setFixedWidth(300)
    click_interval.setValidator(qtg.QDoubleValidator())

    interval_layout.addWidget(interval_label)
    interval_layout.addWidget(interval_type)
    interval_layout.addWidget(click_interval)
    interval_layout.setAlignment(interval_label, AlignFlag.AlignLeft)
    interval_layout.setAlignment(click_interval, AlignFlag.AlignRight)

    button_selection_label = qtw.QLabel("Mouse Button:")
    button_selection_label.setStyleSheet("font-weight: bold;")

    button_selection = qtw.QComboBox()
    button_selection.addItems(["Left (LMB)", "Right (RMB)"])

    button_selection_layout.addWidget(button_selection_label)
    button_selection_layout.addWidget(button_selection)

    head_layout.setContentsMargins(0, 15, 0, 0)
    head_layout.addLayout(interval_layout)
    head_layout.setSpacing(15)
    head_layout.addLayout(button_selection_layout)

    body_layout = qtw.QVBoxLayout()

    status_label = qtw.QLabel("Status:")
    status_label.setStyleSheet("font-weight: bold;")
    status_label.setAlignment(AlignFlag.AlignCenter)

    status_text = qtw.QLabel("🔴 Stopped")
    status_text.setStyleSheet("color: #E53935; font-weight: bold;")
    status_text.setAlignment(AlignFlag.AlignCenter)

    body_layout.addWidget(status_label)
    body_layout.addWidget(status_text)
    body_layout.setAlignment(AlignFlag.AlignCenter)

    footer_layout = qtw.QHBoxLayout()
    start_button = qtw.QPushButton("Start (Alt + S)")
    start_button.clicked.connect(toggle_click)

    stop_button = qtw.QPushButton("Stop (Alt + S)")
    stop_button.clicked.connect(toggle_click)
    stop_button.setEnabled(False)
    footer_layout.addWidget(start_button)
    footer_layout.addWidget(stop_button)

    root_layout.addLayout(head_layout)
    root_layout.addLayout(body_layout)
    root_layout.addSpacing(50)
    root_layout.addLayout(footer_layout)

    window.setLayout(root_layout)
    window.show()
    kb.Listener(on_press=on_press, on_release=on_release).start()
    sys.exit(app.exec())
