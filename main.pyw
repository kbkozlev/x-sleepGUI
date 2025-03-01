import time
import multiprocess
import webbrowser
import PySimpleGUI as Sg
import pyautogui as pag
import keyboard
import logging
from app.settings.helpers.functions import (get_latest_version, create_process, countdown, graceful_exit, get_hotkey,
                                            correct_key,
                                            is_capslock_on, terminate, os_check)
from threading import Thread, Event
from app.settings.helpers.mouse_jiggler import jiggler
from app.settings.helpers.configurator import Configurator

logging.basicConfig(filename='app/settings/helpers/log.log', encoding='utf-8', level=logging.INFO,
                    format='%(asctime)s | %(message)s', datefmt='%Y/%m/%d %I:%M:%S %p')


def about_window():
    layout = [[Sg.T(s=40)],
              [Sg.Push(), Sg.T(str(WINDOW_TITLE), font=(FONT_FAMILY, 12, "bold")), Sg.Push()],
              [Sg.Push(), Sg.T("Prevent your PC from sleeping with - 'Don't sleep' \nor X-Sleep for short.",
                               font=(FONT_FAMILY, 9, "italic"), justification='c', text_color='grey'), Sg.Push()],
              [Sg.T()],
              [Sg.Push(), Sg.T(github_url['name'], enable_events=True, font=(FONT_FAMILY, 10, "underline"),
                               justification='l', text_color='#0066CC',
                               auto_size_text=True, key='-LINK-'), Sg.Push()],
              [Sg.Push(), Sg.T("License: GPL-3.0", justification='c'), Sg.Push()],
              [Sg.T()],
              [Sg.Push(), Sg.T("Copyright © 2023 Kaloian Kozlev", text_color='light grey'), Sg.Push()]]

    window = Sg.Window("About", layout, icon=ICON)

    while True:
        event, values = window.read()

        match event:
            case Sg.WIN_CLOSED:
                break

            case '-LINK-':
                webbrowser.open(github_url['url'])
                window.close()
                break


def new_version_window(c_release, c_release_name, l_release, l_release_name, down_url):
    global update_check
    layout = [[Sg.T(s=40)],
              [Sg.T(font=(FONT_FAMILY, 10), justification='l', key="-INFO-")],
              [Sg.T()],
              [Sg.T('Current Version is  :', justification='l', font=(FONT_FAMILY, 10)),
               Sg.T(f'{c_release_name}', font=(FONT_FAMILY, 10))],
              [Sg.T('Available Version is:', justification='l', font=(FONT_FAMILY, 10)),
               Sg.T(f'{l_release_name}', font=(FONT_FAMILY, 10))],
              [Sg.T()],
              [Sg.Push(),
               Sg.B('Yes', key='-DOWNLOAD-', s=8, button_color='#93b7a6'),
               Sg.B(key='-EXIT-', s=8, button_color='#db5656'),
               Sg.Push()]]

    window = Sg.Window("Update Available", layout, icon=ICON, keep_on_top=True, finalize=True)

    if l_release is None:
        message = "Cannot fetch version data! \nPlease check your network connection."
        title = "Error"
        download_enabled = False
        exit_text = "Exit"
    elif l_release <= c_release:
        message = "You have the latest version!"
        title = "No update available"
        download_enabled = False
        exit_text = "Exit"
    else:
        message = "An update is available, do you want to download it?"
        title = "Update available"
        download_enabled = True
        exit_text = "No"

    window['-INFO-'].update(message)
    window.set_title(title)
    window['-DOWNLOAD-'].update(visible=download_enabled)
    window['-EXIT-'].update(exit_text)

    while True:
        event, values = window.read()

        match event:
            case Sg.WIN_CLOSED:
                break

            case '-DOWNLOAD-':
                webbrowser.open(down_url)
                window.close()

            case '-EXIT-':
                window.close()

    update_check = False


def main_window():
    global hot_key, update_check, bgp

    app_menu = [['Help', ['About', 'Check for Updates']]]

    layout = [[Sg.Menubar(app_menu)],
              [Sg.Frame('Hotkey',
                        [[Sg.I(disabled=True, default_text=hot_key, justification='c',
                               disabled_readonly_text_color='grey', disabled_readonly_background_color='#dae0e6',
                               key='-HT_KEY-', tooltip="ALT, CTRL, SHIFT, WINDOWS, A-Z, 0-9, F1-F12")],
                         [Sg.Checkbox('Change', key='-CHANGE-', enable_events=True, disabled=True), Sg.Push(),
                          Sg.B('Reset', size=8, key='-RESET-', disabled_button_color='light grey', disabled=True),
                          Sg.B('Apply', size=8, disabled=True, disabled_button_color='light grey', key='-APPLY-')]
                         ], expand_x=True)],
              [Sg.Frame('Timer',
                        [[Sg.T('Hours:'), Sg.DropDown(HOURS, default_value=' 00', key='-H-', disabled=True,
                                                      readonly=True, button_background_color='#93b7a6', s=(3, 1)),
                          Sg.T('Minutes:'), Sg.DropDown(MINUTES, default_value=' 00', key='-M-', disabled=True,
                                                        readonly=True, button_background_color='#93b7a6', s=(3, 1)),
                          Sg.T('Seconds:'), Sg.DropDown(SECONDS, default_value=' 00', key='-S-', disabled=True,
                                                        readonly=True, button_background_color='#93b7a6', s=(3, 1))
                          ],
                         [Sg.Radio('Off', 'timer', default=True, enable_events=True, key='-OFF-'),
                          Sg.Radio('On', 'timer', enable_events=True, key='-ON-'), Sg.Push(),
                          Sg.I(background_color='#dae0e6', size=8, key='-LOG_TIME-', justification='c',
                               default_text='00:00:00', disabled=True, disabled_readonly_text_color='grey',
                               disabled_readonly_background_color='#dae0e6', readonly=True)]
                         ], expand_x=True)],
              [Sg.Frame('Log',
                        [[Sg.Input(background_color='#dae0e6', size=45, key='-LOG-', justification='c',
                                   text_color='white')]], expand_x=True)],
              [Sg.Button('Start', size=8, button_color='#93b7a6', disabled_button_color='light grey',
                         key='-START-'),
               Sg.Button('Stop', size=8, button_color='#ffcf61', disabled=True,
                         disabled_button_color='light grey', key='-STOP-'),
               Sg.Button('Exit', size=8, button_color='#db5656')]
              ]

    window = Sg.Window(WINDOW_TITLE, layout, keep_on_top=False, finalize=True)

    if os_name == "windows":
        window['-CHANGE-'].update(disabled=False)
        window['-RESET-'].update(disabled=False)

    if update_check:
        new_version_window(RELEASE, RELEASE_NAME, latest_release, latest_release_name, download_url)

    while True:
        event, values = window.read(timeout=10)

        if hot_key_active:
            keyboard.add_hotkey(hot_key, lambda: graceful_exit(thread_event, window, pag))

        if event in ('Exit', Sg.WIN_CLOSED):
            break

        if event == '-START-':
            window['-STOP-'].update(disabled=False)
            window['-STOP-'].update(button_color='#ffcf61')
            window['-START-'].update(disabled=True)

            bgp = create_process(jiggler, pag)
            bgp.daemon = True

            if values['-ON-'] and values['-H-'] == ' 00' and values['-M-'] == ' 00' and values['-S-'] == ' 00':
                window.write_event_value('-OFF-', True)
                window['-OFF-'].update(True)
            elif values['-ON-'] and (values['-H-'] != ' 00' or values['-M-'] != ' 00' or values['-S-'] != ' 00'):
                Thread(target=countdown,
                       args=(values['-H-'], values['-M-'], values['-S-'], window, thread_event, bgp),
                       daemon=True).start()

            bgp.start()
            window['-LOG-'].update('Application running', background_color='#5fad65')

        elif event == '-STOP-':
            is_capslock_on(pag, os_name=os_name)

            if values['-ON-'] and values['-LOG_TIME-'] != '00:00:00':
                thread_event.set()

            if not hot_key_active: # Linux version has issue with Wayland protocol, where app cannot continue, so it quits the app instead.
                break

            else:
                terminate(window, bgp)

        # Events for Frame - Hotkey
        if values['-CHANGE-']:
            window['-HT_KEY-'].update(disabled=False)
            window['-HT_KEY-'].update(text_color='black')
            window['-APPLY-'].update(disabled=False)
            window['-APPLY-'].update(button_color='#93b7a6')

        else:
            window['-HT_KEY-'].update(hot_key)
            window['-HT_KEY-'].update(disabled=True)
            window['-HT_KEY-'].update(text_color='grey')
            window['-APPLY-'].update(disabled=True)

        if event == '-APPLY-':
            wrong_values, format_str = correct_key(text=values['-HT_KEY-'])
            if not wrong_values:
                conf.hot_key_state = True
                hot_key = conf.cust_hot_key = format_str
                conf.save_config_file()
                window['-CHANGE-'].update(False)
            else:
                window['-LOG-'].update(
                    f'{wrong_values} {"key is" if len(wrong_values) == 1 else "keys are"} not valid!',
                    background_color='#db5656')
                window.refresh()
                time.sleep(2)
                window['-LOG-'].update('', background_color='#dae0e6')

        if event == '-RESET-':
            conf.hot_key_state = False
            conf.cust_hot_key = ''
            conf.save_config_file()
            hot_key = get_hotkey(conf)
            window['-HT_KEY-'].update(hot_key)
            window['-CHANGE-'].update(False)

        # Events for Frame - Timer
        if event == '-ON-':
            window['-H-'].update(disabled=False)
            window['-M-'].update(disabled=False)
            window['-S-'].update(disabled=False)
            window['-LOG_TIME-'].update(disabled=False, text_color='black')

        elif event == '-OFF-':
            window['-H-'].update(disabled=True, value=' 00')
            window['-M-'].update(disabled=True, value=' 00')
            window['-S-'].update(disabled=True, value=' 00')
            window['-LOG_TIME-'].update(disabled=True, text_color='grey')

        # Events for menubar
        if event == 'About':
            about_window()

        if event == 'Check for Updates':
            new_version_window(RELEASE, RELEASE_NAME, latest_release, latest_release_name, download_url)

    graceful_exit(thread_event, window, pag)


if __name__ == '__main__':
    hot_key_active = False
    thread_event = Event()
    conf = Configurator()
    conf.create_on_start()
    hot_key = get_hotkey(conf)
    update_check = False
    bgp = None
    os_name = os_check()

    if os_name == "windows":
        multiprocess.freeze_support()
        hot_key_active = True
    else:
        hot_key = 'Not Supported on this platform'

    RELEASE_NAME = '3.0.1'
    RELEASE = int(''.join(filter(lambda x: x.isdigit(), RELEASE_NAME)))
    WINDOW_TITLE = "X-Sleep"
    FONT_FAMILY = "Arial"
    HOURS = [f" {i:02}" for i in range(24)]
    MINUTES = [f" {i:02}" for i in range(60)]
    SECONDS = [f" {i:02}" for i in range(60)]
    ICON = 'app/media/x-sleep.ico'

    github_url = {'name': 'Official GitHub Page',
                  'url': 'https://github.com/kbkozlev/x-sleepGUI'}

    Sg.theme("Reddit")
    Sg.set_options(force_modal_windows=True, dpi_awareness=True, use_ttk_buttons=True, icon=ICON)

    latest_release, latest_release_name, download_url = get_latest_version()
    if latest_release is not None and latest_release > RELEASE:
        update_check = True

    main_window()
