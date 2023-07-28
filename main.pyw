import random
import PySimpleGUI as sg
import pyautogui as pag
import multiprocess as mp
from background_process import process


def create_process(prc):
    return mp.Process(target=prc, args=[pag, random])


def main_window():

    layout = [[sg.Frame('Hotkey',
                        [[sg.I(disabled=True, default_text='CTRL + ALT + C',
                                                  justification='c', text_color='grey', key='-INP-')],
                         [sg.Radio('Default', 'sel', default=True, enable_events=True, key='-DEF-'),
                          sg.Radio('Custom', 'sel', enable_events=True, key='-CUST-'), sg.B('Apply', size=8)]
                         ],expand_x=True)],
              [sg.T()],
              [sg.Button('Start', size=8), sg.Button('Stop', size=8), sg.Button('Exit', size=8)]
    ]

    window = sg.Window("X-sleep", layout, size=(500, 200))

    while True:
        event, values = window.read()

        if event in ('Exit', sg.WIN_CLOSED):
            break

        elif event == 'Start':
            bgp = create_process(process)
            bgp.daemon = True
            bgp.start()

        elif event == 'Stop':
            try:
                bgp.terminate()
            except:
                print('Process not running')

        elif event == '-CUST-':
            window['-INP-'].update(disabled=False)

    window.close()


if __name__ == '__main__':
    theme = sg.theme("Reddit")
    sg.set_options(force_modal_windows=True, dpi_awareness=True, icon='x-sleep.ico')

    main_window()
