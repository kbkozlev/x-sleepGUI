import time
import re
import sys
import multiprocess
import webbrowser
import PySimpleGUI as sg
import pyautogui as pag
import keyboard
import logging
from functions import get_latest_version, create_process, countdown, graceful_exit, get_hotkey, correct_key, \
    is_capslock_on
from threading import Thread, Event
from mouse_jiggler import jiggler
from configurator import Configurator

logging.basicConfig(filename='log.log', encoding='utf-8', level=logging.INFO,
                    format='%(asctime)s | %(message)s', datefmt='%Y/%m/%d %I:%M:%S %p')


def about_window():
    layout = [[sg.Push(), sg.T(str(WINDOW_TITLE), font=(FONT_FAMILY, 12, "bold")), sg.Push()],
              [sg.T()],
              [sg.Push(), sg.T(github_url['name'], enable_events=True, font=(FONT_FAMILY, 10, "underline"),
                               justification='l', text_color='#0066CC',
                               auto_size_text=True, key='-LINK-'), sg.Push()],
              [sg.Push(), sg.T("License: GPL-3.0", justification='c'), sg.Push()],
              [sg.T()],
              [sg.Push(), sg.T("Copyright © 2023 Kaloian Kozlev", text_color='light grey'), sg.Push()]]

    window = sg.Window("About", layout, icon=ICON)

    while True:
        event, values = window.read()

        match event:
            case sg.WIN_CLOSED:
                break

            case '-LINK-':
                webbrowser.open(github_url['url'])
                window.close()


def new_version(current_release, latest_release, download_url):
    global update_check
    layout = [[sg.Push(), sg.T('New Version Available', font=(FONT_FAMILY, 12, 'bold'), justification='c'), sg.Push()],
              [sg.T(s=30)],
              [sg.T('Current Version:', s=13, justification='r'), sg.T(f'{current_release}',
                                                                       font=(FONT_FAMILY, 10, 'bold'))],
              [sg.T(f'Latest Version:', s=13, justification='r'), sg.T(f'{latest_release}',
                                                                       font=(FONT_FAMILY, 10, 'bold'))],
              [sg.T()],
              [sg.Push(), sg.B('Download', key='-DOWNLOAD-', s=8, button_color='#93b7a6'), sg.B('Cancel',
                                                                                                key='-EXIT-', s=8,
                                                                                                button_color='#db5656'),
               sg.Push()]]

    window = sg.Window("New Version Available", layout, icon=ICON, keep_on_top=True)

    while True:
        event, values = window.read()

        match event:
            case sg.WIN_CLOSED:
                break

            case '-DOWNLOAD-':
                if latest_release is not None:
                    current_release = re.sub(r'[^0-9]', '', current_release)
                    latest_release = re.sub(r'[^0-9]', '', latest_release)

                    if int(latest_release) > int(current_release):
                        webbrowser.open(download_url)
                        window.close()

            case '-EXIT-':
                window.close()

    update_check = False


def updates_window(current_release):
    latest_release, download_url = get_latest_version()
    layout = [[sg.Push(), sg.T('Version Info', font=(FONT_FAMILY, 12, 'bold'), justification='c'), sg.Push()],
              [sg.T(s=30)],
              [sg.T('Current Version:', s=13, justification='r'), sg.T(f'{current_release}',
                                                                       font=(FONT_FAMILY, 10, 'bold'))],
              [sg.T(f'Latest Version:', s=13, justification='r'), sg.T(f'{latest_release}',
                                                                       font=(FONT_FAMILY, 10, 'bold'))],
              [sg.Push(), sg.T(justification="c", key="-INFO-"), sg.Push()],
              [sg.Push(), sg.B('Download', key='-DOWNLOAD-', s=8, button_color='#93b7a6'), sg.Push()]]

    window = sg.Window("Check for Updates", layout, icon=ICON)

    while True:
        event, values = window.read()

        match event:
            case sg.WIN_CLOSED:
                break

            case '-DOWNLOAD-':
                if latest_release is not None:
                    current_release = re.sub(r'[^0-9]', '', current_release)
                    latest_release = re.sub(r'[^0-9]', '', latest_release)

                    if int(latest_release) > int(current_release):
                        webbrowser.open(download_url)
                        window.close()

                    else:
                        window['-INFO-'].update("You have the latest version", text_color='green')

                else:
                    window['-INFO-'].update("Cannot fetch version data", text_color='red')

        window.refresh()
        time.sleep(1)
        window["-INFO-"].update(" ")


def main_window():
    global hot_key, bgp, update_check

    app_menu = [['Help', ['About', 'Check for Updates']]]

    layout = [[sg.Menubar(app_menu)],
              [sg.Frame('Hotkey',
                        [[sg.I(disabled=True, default_text=hot_key, justification='c',
                               disabled_readonly_text_color='grey', disabled_readonly_background_color='#dae0e6',
                               key='-HT_KEY-', tooltip="ALT, CTRL, SHIFT, WINDOWS, A-Z, 0-9, F1-F12")],
                         [sg.Checkbox('Change', key='-CHANGE-', enable_events=True), sg.Push(),
                          sg.B('Reset', size=8, key='-RESET-'),
                          sg.B('Apply', size=8, disabled=True, disabled_button_color='light grey', key='-APPLY-')]
                         ], expand_x=True)],
              [sg.Frame('Timer',
                        [[sg.T('Hours:'), sg.DropDown(HOURS, default_value=0, key='-H-', disabled=True,
                                                      readonly=True, button_background_color='#93b7a6'),
                          sg.T('Minutes:'), sg.DropDown(MINUTES, default_value=0, key='-M-', disabled=True,
                                                        readonly=True, button_background_color='#93b7a6'),
                          sg.T('Seconds:'), sg.DropDown(SECONDS, default_value=0, key='-S-', disabled=True,
                                                        readonly=True, button_background_color='#93b7a6')
                          ],
                         [sg.Radio('Off', 'timer', default=True, enable_events=True, key='-OFF-'),
                          sg.Radio('On', 'timer', enable_events=True, key='-ON-'), sg.Push(),
                          sg.I(background_color='#dae0e6', size=8, key='-LOG_TIME-', justification='c',
                               default_text='00:00:00', disabled=True, disabled_readonly_text_color='grey',
                               disabled_readonly_background_color='#dae0e6', readonly=True)]
                         ], expand_x=True)],
              [sg.Frame('Log',
                        [[sg.Input(background_color='#dae0e6', size=45, key='-LOG-', justification='c',
                                   text_color='white')]], expand_x=True)],
              [sg.Button('Start', size=8, button_color='#93b7a6', disabled_button_color='light grey',
                         key='-START-'),
               sg.Button('Stop', size=8, button_color='#ffcf61', disabled=True,
                         disabled_button_color='light grey', key='-STOP-'),
               sg.Button('Exit', size=8, button_color='#db5656')]
              ]

    window = sg.Window(WINDOW_TITLE, layout, keep_on_top=False)

    while True:
        event, values = window.read(timeout=10)

        if update_check:
            new_version(RELEASE, latest_release_name, download_url)

        keyboard.add_hotkey(hot_key, lambda: graceful_exit(thread_event, window, pag))

        if event in ('Exit', sg.WIN_CLOSED):
            break

        if event == '-START-':
            window['-STOP-'].update(disabled=False)
            window['-STOP-'].update(button_color='#ffcf61')
            window['-START-'].update(disabled=True)

            bgp = create_process(jiggler, pag)
            bgp.daemon = True

            if values['-ON-'] and values['-H-'] == 0 and values['-M-'] == 0 and values['-S-'] == 0:
                window.write_event_value('-OFF-', True)
                window['-OFF-'].update(True)
            elif values['-ON-'] and (values['-H-'] != 0 or values['-M-'] != 0 or values['-S-'] != 0):
                Thread(target=countdown,
                       args=(values['-H-'], values['-M-'], values['-S-'], window, thread_event, bgp),
                       daemon=True).start()

            bgp.start()
            window['-LOG-'].update('Application running', background_color='#5fad65')

        elif event == '-STOP-':
            is_capslock_on(pag)

            if values['-ON-'] and values['-LOG_TIME-'] != '00:00:00':
                thread_event.set()

            else:
                try:
                    bgp.terminate()
                except Exception as e:
                    logging.error(e)

            window['-LOG-'].update('Application terminated', background_color='#ffcf61')
            window.refresh()
            time.sleep(1)
            window['-LOG-'].update('', background_color='#dae0e6')
            window['-STOP-'].update(disabled=True)
            window['-START-'].update(disabled=False)

        # Events for Frame - Hotkey
        if values['-CHANGE-']:
            window['-HT_KEY-'].update(disabled=False)
            window['-HT_KEY-'].update(text_color='black')
            window['-APPLY-'].update(disabled=False)
            window['-APPLY-'].update(button_color='#93b7a6')

        else:
            window['-HT_KEY-'].update(disabled=True)
            window['-HT_KEY-'].update(text_color='grey')
            window['-APPLY-'].update(disabled=True)

        if event == '-APPLY-':
            wrong_values, format_str = correct_key(text=values['-HT_KEY-'])
            if not wrong_values:
                conf.hot_key_state = True
                hot_key = conf.cust_hot_key = format_str
                conf.save_config_file()
                window['-HT_KEY-'].update(format_str)
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
            window['-H-'].update(disabled=True, value=0)
            window['-M-'].update(disabled=True, value=0)
            window['-S-'].update(disabled=True, value=0)
            window['-LOG_TIME-'].update(disabled=True, text_color='grey')

        # Events for menubar
        if event == 'About':
            about_window()

        if event == 'Check for Updates':
            updates_window(RELEASE)

    graceful_exit(thread_event, window, pag)


if __name__ == '__main__':
    if sys.platform.startswith('win'):
        multiprocess.freeze_support()

    RELEASE = '2.0.0'
    WINDOW_TITLE = "X-Sleep"
    FONT_FAMILY = "Arial"
    HOURS = list(range(0, 24))
    MINUTES = list(range(0, 60))
    SECONDS = list(range(0, 60))
    ICON = 'media/x-sleep.ico'

    github_url = {'name': 'Official GitHub Page',
                  'url': 'https://github.com/kbkozlev/x-sleepGUI'}

    sg.theme("Reddit")
    sg.set_options(force_modal_windows=True, dpi_awareness=True, use_ttk_buttons=True, icon=ICON)

    thread_event = Event()
    conf = Configurator()
    conf.create_on_start()
    hot_key = get_hotkey(conf)
    update_check = False

    try:
        latest_release_name, download_url = get_latest_version()
        if latest_release_name is not None:
            current_release = re.sub(r'[^0-9]', '', RELEASE)
            latest_release = re.sub(r'[^0-9]', '', latest_release_name)
            if int(latest_release) > int(current_release):
                update_check = True
    except Exception as e:
        logging.error(e)

    main_window()
