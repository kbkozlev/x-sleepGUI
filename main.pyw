import random
import time
import re
import webbrowser
import PySimpleGUI as sg
import pyautogui as pag
import keyboard
import fuckit
import logging
from functions import get_latest_version, create_process, countdown, graceful_exit
from threading import Thread, Event
from mouse_jiggler import jiggler
from configurator import Configurator

logging.basicConfig(filename='log.log', encoding='utf-8', level=logging.INFO,
                    format='%(asctime)s %(message)s', datefmt='%Y/%m/%d %I:%M:%S %p')


def about_window():
    layout = [[sg.Push(), sg.T(str(WINDOW_TITLE), font=(FONT_FAMILY, 12, "bold")), sg.Push()],
              [sg.T()],
              [sg.Push(), sg.T(github_url['name'], enable_events=True, font=(FONT_FAMILY, 10, "underline"),
                               justification='l', text_color='#0066CC',
                               auto_size_text=True, key='download'), sg.Push()],
              [sg.Push(), sg.T("License: GPL-3.0", justification='c'), sg.Push()],
              [sg.T()],
              [sg.Push(), sg.T("Copyright © 2023 Kaloian Kozlev", text_color='light grey'), sg.Push()]]

    window = sg.Window("About", layout, icon=ICON, size=(480, 220))

    while True:
        event, values = window.read()

        match event:

            case sg.WIN_CLOSED:
                break

            case 'download':
                webbrowser.open(github_url['url'])
                window.close()


def updates_window(current_release):
    latest_release, download_url = get_latest_version()
    layout = [[sg.Push(), sg.T('Version Info', font=(FONT_FAMILY, 12, 'bold')), sg.Push()],
              [sg.T()],
              [sg.T('Current Version:', s=13), sg.T(f'{current_release}', font=(FONT_FAMILY, 10, 'bold'))],
              [sg.T(f'Latest Version:', s=13), sg.T(f'{latest_release}', font=(FONT_FAMILY, 10, 'bold'))],
              [sg.Push(), sg.T(justification="c", key="-INFO-"), sg.Push()],
              [sg.Push(), sg.B('Download', key='download', s=8, button_color='#93b7a6'), sg.Push()]]

    window = sg.Window("Check for Updates", layout, icon=ICON, size=(480, 220))

    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED:
            break

        match event:

            case 'download':
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
    app_menu = [['Help', ['About', 'Check for Updates']]]

    layout = [[sg.Menubar(app_menu)],
              [sg.Frame('Hotkey',
                        [[sg.I(disabled=True, default_text=conf.get_value('hot_key'), justification='c',
                               disabled_readonly_text_color='grey', disabled_readonly_background_color='#dae0e6',
                               key='-HT_KEY-')],
                         [sg.Radio('Default', 'sel', default=True, enable_events=True, key='-DEF-'),
                          sg.Radio('Custom', 'sel', enable_events=True, key='-CUST-'), sg.Push(),
                          sg.B('Apply', size=8, disabled=True, disabled_button_color='light grey', key='-APP_HT-')]
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
                        [[sg.I(background_color='#dae0e6', size=45, key='-LOG-', justification='c',
                               text_color='white')]], expand_x=True)],
              [sg.Button('Start', size=8, button_color='#93b7a6'),
               sg.Button('Stop', size=8, button_color='#ffcf61', disabled=True,
                         disabled_button_color='light grey', key='-STOP-'),
               sg.Button('Exit', size=8, button_color='#db5656')]
              ]

    window = sg.Window(WINDOW_TITLE, layout, keep_on_top=False)

    while True:
        event, values = window.read(timeout=10)

        with fuckit:
            keyboard.add_hotkey(str(values['-HT_KEY-']), lambda: graceful_exit(window=window))

        if event in ('Exit', sg.WIN_CLOSED):
            break

        if event == 'Start':
            window['-STOP-'].update(disabled=False)
            window['-STOP-'].update(button_color='#ffcf61')

            bgp = create_process(jiggler, pag, random)
            bgp.daemon = True

            if values['-ON-']:
                Thread(target=countdown, args=(values['-H-'], values['-M-'], values['-S-'], window, event_t, bgp),
                       daemon=True).start()

            bgp.start()
            window['-LOG-'].update('Application running', background_color='#5fad65')

        elif event == '-STOP-':

            if values['-ON-']:
                event_t.set()

            else:
                try:
                    bgp.terminate()
                    window['-LOG-'].update('Application terminated', background_color='#ffcf61')
                    window.refresh()
                except Exception as e:
                    logging.error(e)

            time.sleep(1)
            window['-LOG-'].update('', background_color='#dae0e6')
            window.refresh()

            window['-STOP-'].update(disabled=True)

        # Events for Frame - Hotkey
        if event == '-DEF-':
            window['-HT_KEY-'].update(disabled=True)
            window['-HT_KEY-'].update(text_color='grey')
            window['-APP_HT-'].update(disabled=True)

        if event == '-CUST-':
            window['-HT_KEY-'].update(disabled=False)
            window['-HT_KEY-'].update(text_color='black')
            window['-APP_HT-'].update(disabled=False)
            window['-APP_HT-'].update(button_color='#93b7a6')

        if event == '-APP_HT-':
            conf.htk_cust = True
            conf.hot_key = values['-HT_KEY-']
            conf.save_config_file()

        # Events for Frame - Timer
        if event == '-ON-':
            window['-H-'].update(disabled=False)
            window['-M-'].update(disabled=False)
            window['-S-'].update(disabled=False)
            window['-LOG_TIME-'].update(disabled=False, text_color='black')

        elif event == '-OFF-':
            window['-H-'].update(disabled=True)
            window['-M-'].update(disabled=True)
            window['-S-'].update(disabled=True)
            window['-LOG_TIME-'].update(disabled=True, text_color='grey')

        # Events for menubar
        if event == 'About':
            about_window()

        if event == 'Check for Updates':
            updates_window(RELEASE)

    window.close()


if __name__ == '__main__':

    RELEASE = '1.0.0'
    WINDOW_TITLE = f"X-Sleep GUI v{RELEASE}"
    FONT_FAMILY = "Arial"
    HOURS = list(range(0, 24))
    MINUTES = list(range(0, 60))
    SECONDS = list(range(0, 60))
    ICON = 'media/x-sleep.ico'

    github_url = {'name': 'Official GitHub Page',
                  'url': 'https://github.com/kbkozlev/x-sleepGUI'}

    theme = sg.theme("Reddit")
    sg.set_options(force_modal_windows=True, dpi_awareness=True, use_ttk_buttons=True, icon=ICON)

    event_t = Event()

    conf = Configurator()
    conf.create_on_start()

    main_window()
