import time


def countdown(hours, minutes, seconds, active, window):
    countdown_time = ((hours * 60) * 60) + (minutes * 60) + seconds
    while active:
        while countdown_time >= 0:
            seconds = countdown_time % 60
            minutes = int(countdown_time / 60) % 60
            hours = int(countdown_time / 3600)
            window['-LOG_TIME-'].update(f"{hours:02}:{minutes:02}:{seconds:02}")
            time.sleep(1)
            countdown_time -= 1
    return False










