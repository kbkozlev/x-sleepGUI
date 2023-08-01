import time


def countdown(hours, minutes, seconds):
    countdown_time = ((hours * 60) * 60) + (minutes * 60) + seconds
    while countdown_time > 0:
        seconds = countdown_time % 60
        minutes = int(countdown_time / 60) % 60
        hours = int(countdown_time / 3600)
        time_left = f"{hours:02}:{minutes:02}:{seconds:02}"
        # print(time_left)
        time.sleep(1)
        countdown_time -= 1
    return "00:00:00"  # Return this to indicate the countdown has finished










