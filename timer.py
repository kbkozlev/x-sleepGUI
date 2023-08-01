import time
import fuckit
from threading import Event


def countdown(hours, minutes, seconds, window, event: Event, bgp):
    countdown_time = ((hours * 60) * 60) + (minutes * 60) + seconds
    while countdown_time > 0:
        seconds = countdown_time % 60
        minutes = int(countdown_time / 60) % 60
        hours = int(countdown_time / 3600)
        window['-LOG_TIME-'].update(f"{hours:02}:{minutes:02}:{seconds:02}")
        time.sleep(1)
        countdown_time -= 1
        if event.is_set():
            break
    window['-LOG_TIME-'].update("00:00:00")
    with fuckit:
        bgp.terminate()











