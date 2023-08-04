import requests
import multiprocess as mp
import time
from threading import Event
import logging

logging.basicConfig(filename='log.log', encoding='utf-8', level=logging.INFO,
                    format='%(asctime)s %(message)s', datefmt='%Y/%m/%d %I:%M:%S %p')

keys = ['ALT', 'CTRL', 'SHIFT', 'WINDOWS',
        'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
        'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
        '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
        'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12']


def correct_key(data):
    not_valid = []
    key = data.upper().replace(' ', '').split('+')
    for k in key:
        if k not in keys:
            not_valid.append(k)

    return not_valid


def get_hotkey(conf):
    cust = conf.get_value('htk_cust')
    if cust:
        hot_hey = conf.get_value('cust_hot_key')
    else:
        hot_hey = conf.get_value('def_hot_key')
    return hot_hey, cust


def graceful_exit(event, window):
    try:
        event.set()
    except Exception as e:
        logging.error(e)
    finally:
        event.clear()
        time.sleep(0.1)
        window.write_event_value('Exit', True)


def countdown(hours, minutes, seconds, window, event: Event, bgp):
    countdown_time = ((hours * 60) * 60) + (minutes * 60) + seconds
    if not countdown_time == 0:
        while countdown_time > 0:
            seconds = countdown_time % 60
            minutes = int(countdown_time / 60) % 60
            hours = int(countdown_time / 3600)
            window['-LOG_TIME-'].update(f"{hours:02}:{minutes:02}:{seconds:02}")
            time.sleep(1)
            countdown_time -= 1
            if event.is_set():
                break

        try:
            bgp.terminate()
        except Exception as e:
            logging.error(e)

        event.clear()
        window['-LOG_TIME-'].update("00:00:00")
        window['-LOG-'].update('Application terminated', background_color='#ffcf61')
        window.refresh()
        time.sleep(1)
        window['-LOG-'].update('', background_color='#dae0e6')
        window['-STOP-'].update(disabled=True)

    window.write_event_value('-OFF-', True)
    window['-OFF-'].update(True)


def get_latest_version():
    try:
        response = requests.get("https://api.github.com/repos/kbkozlev/x-sleepGUI/releases/latest")
        latest_release = response.json()['tag_name']
        download_url = response.json()['html_url']

    except Exception as e:
        logging.error(e)
        latest_release = None
        download_url = None

    return latest_release, download_url


def create_process(args, *kwargs):
    return mp.Process(target=args, args=kwargs)
