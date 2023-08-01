import random
import PySimpleGUI as sg
import pyautogui as pag
import multiprocess as mp
from background_process import process
from timer import countdown


def create_process(target, *kwargs):
    return mp.Process(target=target, args=kwargs)


def main_window():
    layout = [[sg.Frame('Hotkey',
                        [[sg.I(disabled=True, default_text='CTRL + ALT + C', justification='c',
                               disabled_readonly_text_color='grey', disabled_readonly_background_color='#dae0e6', key='-INP-')],
                         [sg.Radio('Default', 'sel', default=True, enable_events=True, key='-DEF-'),
                          sg.Radio('Custom', 'sel', enable_events=True, key='-CUST-'), sg.Push(),
                          sg.B('Apply', size=8, disabled=True, disabled_button_color='light grey', key='-APP_HT-')]
                         ], expand_x=True)],
              [sg.Frame('Timer',
                        [[sg.T('Hours:'), sg.DropDown(HOURS, default_value=0, key='-H-', disabled=True,
                                                      button_background_color='#93b7a6'),
                          sg.T('Minutes:'), sg.DropDown(MINUTES, default_value=0, key='-M-', disabled=True,
                                                        button_background_color='#93b7a6'),
                          sg.T('Seconds:'), sg.DropDown(SECONDS, default_value=0, key='-S-', disabled=True,
                                                        button_background_color='#93b7a6')
                          ],
                         [sg.Radio('Off', 'timer', default=True, enable_events=True, key='-OFF-'),
                          sg.Radio('On', 'timer', enable_events=True, key='-ON-'), sg.Push(),
                          sg.B('Apply', size=8, disabled=True, disabled_button_color='light grey', key='-APP_TM-')],
                         ], expand_x=True)],
              [sg.Frame('Log',
                        [[sg.I(background_color='#dae0e6', size=45, key='-LOG-')]], expand_x=True)],
              [sg.Button('Start', size=8, button_color='#5fad65'), sg.Button('Stop', size=8, button_color='#ffcf61'),
               sg.Button('Exit', size=8, button_color='#db5656')]
              ]

    window = sg.Window("X-sleep", layout)

    while True:
        event, values = window.read()

        if event in ('Exit', sg.WIN_CLOSED):
            break

        if event == 'Start':
            bgp = create_process(process, [pag, random])
            bgp.daemon = True
            # bgp.start()

            if values['-ON-']:
                time_left = create_process(countdown, [1, 0, 0])
                time_left.daemon = True
                while True:
                    time_left.start()
                    window['-LOG-'].update(str(time_left))
                    # window.refresh()
                    if time_left == "00:00:00":
                        break


        if event == 'Stop':
            try:
                bgp.terminate()
                time_left.terminate()


            except UnboundLocalError:
                print('Process not running')

        # Events for Frame - Hotkey
        if event == '-DEF-':
            window['-INP-'].update(disabled=True)
            window['-INP-'].update(text_color='grey')
            window['-APP_HT-'].update(disabled=True)

        if event == '-CUST-':
            window['-INP-'].update(disabled=False)
            window['-INP-'].update(text_color='black')
            window['-APP_HT-'].update(disabled=False)
            window['-APP_HT-'].update(button_color='#93b7a6')

        # Events for Frame - Timer
        if event == '-ON-':
            window['-H-'].update(disabled=False)
            window['-M-'].update(disabled=False)
            window['-S-'].update(disabled=False)
            window['-APP_TM-'].update(disabled=False)
            window['-APP_TM-'].update(button_color='#93b7a6')


        elif event == '-OFF-':
            window['-H-'].update(disabled=True)
            window['-M-'].update(disabled=True)
            window['-S-'].update(disabled=True)
            window['-APP_TM-'].update(disabled=True)



    window.close()


if __name__ == '__main__':
    theme = sg.theme("Reddit")
    sg.set_options(force_modal_windows=True, dpi_awareness=True, use_ttk_buttons=True, icon='x-sleep.ico')

    HOURS = list(range(0, 24))
    MINUTES = list(range(0, 60))
    SECONDS = list(range(0, 60))

    main_window()
