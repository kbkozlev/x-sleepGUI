import requests
import logging
import ctypes
import time
from threading import Event
from multiprocess import Process


logging.basicConfig(filename='./app/settings/log.log', encoding='utf-8', level=logging.INFO,
                    format='%(asctime)s | %(message)s', datefmt='%Y/%m/%d %I:%M:%S %p')


keys_list = ['ALT', 'CTRL', 'SHIFT', 'WINDOWS',
             'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
             'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
             '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
             'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12']


def correct_key(text: str):
    not_valid = []
    keys = text.upper().replace(' ', '').split('+')
    for key in keys:
        if key not in keys_list:
            not_valid.append(key)

    valid_keys = ' + '.join(keys)

    return not_valid, valid_keys


def get_hotkey(conf):
    if conf.get_value('hot_key_state'):
        hot_key = conf.get_value('cust_hot_key')
    else:
        hot_key = conf.get_value('def_hot_key')
    return hot_key


def is_capslock_on(pag):
    if ctypes.WinDLL("User32.dll").GetKeyState(0x14):
        pag.press('capslock')


def graceful_exit(event, window, pag):
    try:
        event.set()
    except Exception as e:
        logging.error(e)
    finally:
        is_capslock_on(pag)
        window.write_event_value('Exit', True)


def terminate(window, bgp):
    try:
        bgp.terminate()
        window['-LOG-'].update('Application terminated', background_color='#ffcf61')
        window.refresh()
        time.sleep(1)
        window['-LOG-'].update('', background_color='#dae0e6')
        window['-STOP-'].update(disabled=True)
        window['-START-'].update(disabled=False)

    except Exception as e:
        logging.error(e)


def countdown(hours, minutes, seconds, window, event: Event, bgp):
    countdown_time = (int(hours) * 3600) + (int(minutes) * 60) + int(seconds)
    while countdown_time > 0:
        if event.is_set():
            event.clear()
            break

        hours = int(countdown_time / 3600)
        minutes = int(countdown_time / 60) % 60
        seconds = countdown_time % 60

        window['-LOG_TIME-'].update(f"{hours:02}:{minutes:02}:{seconds:02}")
        countdown_time -= 1
        time.sleep(1)

    window['-LOG_TIME-'].update("00:00:00")
    terminate(window, bgp)
    window.write_event_value('-OFF-', True)
    window['-OFF-'].update(True)


def get_latest_version():
    try:
        response = requests.get("https://api.github.com/repos/kbkozlev/x-sleepGUI/releases/latest")
        response_data = response.json()
        latest_release_name = response_data.get('tag_name')
        download_url = response_data.get('html_url')

        if latest_release_name:
            latest_release = int(''.join(filter(str.isdigit, latest_release_name)))
        else:
            latest_release = None

    except Exception as e:
        logging.error(e)
        latest_release_name = None
        download_url = None
        latest_release = None

    return latest_release, latest_release_name, download_url


def create_process(args, *kwargs):
    return Process(target=args, args=kwargs)
