import logging
import math
import sys
import os
import PySimpleGUI as sg
from numpy.ma.extras import average

project_dir = os.path.dirname(__file__)
package_dir = os.path.join(project_dir, 'uMyo_tools')
sys.path.append(package_dir)
import umyo_parser
import serial
from serial.tools import list_ports
import mido
import time
from datetime import datetime
from MusicalValues import Note
import asyncio

def init_globals():
    global notes_dict, scale, octave, R_forearm, R_bicep, R_back, L_forearm, L_bicep, L_back, device_dict, scale
    root = 'F'
    octave = 2
    device_dict = {3709404326: {'Device ID': 3709404326, 'Note': '', 'Muscle': 'Right Forearm', 'Active': False, 'Flourish State': False, 'Channel': 2},
                   1723834707: {'Device ID': 1723834707, 'Note': '', 'Muscle': 'Left Forearm', 'Active': False, 'Flourish State': False,'Channel': 3},
                   1192667876: {'Device ID': 1192667876, 'Note': '', 'Muscle': 'Right Bicep', 'Active': False, 'Flourish State': False,'Channel': 4},
                   3369251029: {'Device ID': 3369251029, 'Note': '', 'Muscle': 'Left Bicep', 'Active': False, 'Flourish State': False,'Channel': 5},
                   2821543978: {'Device ID': 2821543978, 'Note': '', 'Muscle': 'Right Lat', 'Active': False, 'Flourish State': False,'Channel': 6},
                   2497006410: {'Device ID': 2497006410, 'Note': '', 'Muscle': 'Left Lat', 'Active': False, 'Flourish State': False,'Channel': 7}}

    base_note = Note(root, octave)
    scale = 'major'
    primary_chords, secondary_chords, primary_triads, secondary_triads = base_note.get_related_chords(scale)
    # R_forearm['Note'], R_bicep['Note'], R_back['Note'] = primary_chords
    # L_forearm['Note'], L_bicep['Note'], L_back['Note'] = secondary_chords
    chords = primary_chords + secondary_chords
    # print(chords)
    chord_index = 0
    for device in device_dict.values():
        device['Note'] = chords[chord_index]
        chord_index += 1
    print(device_dict)
    notes_dict = {}
    # Number of octaves
    for octave_range in range(2, 7):
        # Notes in each octave
        for note_selection in base_note.notes:
            number = (base_note.notes.index(note_selection)) + (octave_range * 12)
            notes_dict[f'{note_selection}{octave_range - 2}'] = number

def begin_monitoring():
    global device_dict, scale
    monitoring_layout = [[sg.Button('Start', key='-start-')],
                         [sg.Button('Stop', key='-stop-')]]
    monitoring_window = sg.Window('Monitoring Window', monitoring_layout)
    # Look for serial ports
    port = list(list_ports.comports())
    print("available ports:")
    for p in port:
        print(p.device)
        # Basically sets last port as the device we're looking for
        if p.device == 'COM3':
            device = p.device
    if not device:
        print(f'device not found')
    print("===")
    # Initializes the serial device
    ser = serial.Serial(port=device, baudrate=921600, parity=serial.PARITY_NONE, stopbits=1, bytesize=8, timeout=0)
    print("conn: " + ser.portstr)

    # Starts the EMG measurement loop
    while True:
        event, values = monitoring_window.read()
        if event in (sg.WIN_CLOSED, 'Exit'):
            break
        elif event == '-stop-':
            break
        elif event == '-start-':
            total_uMyo_emg = []
            device_emg_data = {}
            device_const_stream = {}
            reverse_notes = False
            for dev in device_dict.keys():
                device_emg_data[dev] = []
                device_const_stream[dev] = 0
            print(device_emg_data)
            print(mido.get_output_names())
            output = mido.open_output('virtualMidi 1')
            # input = mido.open_input('virtualMidi 0')
            time_start = datetime.now().timestamp()
            print(f'Starting a 90 second monitoring window from {time_start}')
            while True:

                if datetime.now().timestamp() - time_start < 90:
                    cnt = ser.in_waiting
                    if (cnt > 0):
                        # Begins reading COM data
                        data = ser.read(cnt)
                        # Begins parsing COM data
                        umyo_parser.umyo_parse_preprocessor(data)
                        # Gathers all uMyo devices
                        devices = umyo_parser.umyo_get_list()
                        cnt = len(devices)
                        # Don't measure unless there's something to measure
                        if (cnt < 1): continue
                        # Loops through all devices to grab spcgm data specifically
                        for dev in devices:
                            device_id = dev.unit_id
                            if device_id not in device_dict.keys():
                                continue
                            active_device = device_dict[device_id]
                            emg_measurement = dev.device_spectr[1]
                            device_emg_data[active_device['Device ID']].append(emg_measurement)
                            total_uMyo_emg.append((device_id, emg_measurement))
                            buffer_length = 45
                            try:
                            # Verifies buffer size is met in data stream
                                if len(device_emg_data[active_device['Device ID']]) > buffer_length:
                                    # Sets buffer values
                                    buffer = device_emg_data[active_device['Device ID']][len(device_emg_data[active_device['Device ID']])-buffer_length:]
                                    # Checks if muscle is flexing based on buffer average
                                    buffer_value = sum(buffer)/len(buffer)
                                    if buffer_value > 300:
                                        # Sends one note at a time based on muscle flexing
                                        if not active_device['Active']:
                                            play_note(active_device['Note'], active_device['Channel'], output)
                                            active_device['Active'] = True
                                        if active_device['Active']:
                                            # Create volume buffer for normalization
                                            max_emg_val = max(device_emg_data[active_device['Device ID']][len(device_emg_data[active_device['Device ID']])-1500:])
                                            # min_emg_val = min(device_emg_data[active_device['Device ID']][len(device_emg_data[active_device['Device ID']])-1500:])
                                            min_emg_val = 300
                                            vol_ratio = (buffer_value - min_emg_val)/(max_emg_val - min_emg_val)
                                            volume = int(math.sqrt((127**2)*(abs(vol_ratio))))
                                            if volume >= 127:
                                                volume = 127
                                            # modify_note('control_change', active_device['Channel'], output, control_val=7, value=volume)



                                            # Flip switch to track consecutive flexion sustain
                                            device_const_stream[device_id] += 1
                                            if device_const_stream[device_id] > 500:
                                                # Signal changes based on sensor orientation
                                                if  dev.pitch < 0:
                                                    scale = 'minor'
                                                else:
                                                    scale = 'major'
                                                roll = (-1 if dev.roll<0 else 1) * (dev.roll % 3000)
                                                # print(roll)
                                                # if roll > 0:
                                                #     reverse_notes = False
                                                # else:
                                                #     reverse_notes = True
                                                flourish(active_device['Note'], active_device['Channel'], output, scale, reverse_notes)
                                                ser.reset_input_buffer()
                                                device_emg_data[active_device['Device ID']] = []



                                    else:
                                        if active_device['Active']:
                                            turn_note_off(active_device['Note'], active_device['Channel'], output)
                                            device_const_stream[device_id] = 0
                                            # active_device['Flourish State'] = False
                                            active_device['Active'] = False
                            except Exception as e:
                                print(f'Error occurred: {e}')

                else:
                    break
            for device in device_dict.values():
                if device['Active']:
                    turn_note_off(device['Note'], device['Channel'], output)
            output.close()
    return total_uMyo_emg

def play_note(note, channel, output_reader, velocity=127):
    note_on = mido.Message('note_on', note=notes_dict[note], channel=channel, velocity=velocity)
    # with mido.open_output('virtualMidi 1', autoreset=True) as output:
    output_reader.send(note_on)

def turn_note_off(note, channel, output_reader, velocity=127):
    note_off = mido.Message('note_off', note=notes_dict[note], channel=channel, velocity=velocity)
    # with mido.open_output('virtualMidi 1', autoreset=True) as output:
    output_reader.send(note_off)

def modify_note(change_type, channel, output_reader, control_val=None, value=0):
    if control_val:
        note_mod = mido.Message(change_type, channel=channel, control=control_val, value=value)
    output_reader.send(note_mod)

def flourish(base_note, channel, output, pivot_scale, flip_melody):
    pivot_key = base_note[0]
    pivot_octave = int(base_note[-1])
    pivot_note = Note(pivot_key, pivot_octave)
    pivot_primary, pivot_secondary, pivot_primary_triad, pivot_secondary_triad = pivot_note.get_related_chords(pivot_scale, flip_melody)
    # notes_queue = []
    first_primary_triad = reversed(pivot_primary_triad[0]) if flip_melody else pivot_primary_triad[0]
    for note in first_primary_triad:
        # for note in chord:
        play_note(note, channel, output)
        time.sleep(.25)
        turn_note_off(note, channel, output)
    return first_primary_triad

def main():
    init_globals()
    main_layout = [[sg.Button('Begin monitoring', key='-Begin-')],
              [sg.Button('Save Results', key='-Save-')]]
    main_window = sg.Window('Music with Movement', main_layout)
    while True:
        event, values = main_window.read()
        if event in (sg.WIN_CLOSED, 'Exit'):
            break
        elif event == '-Begin-':
            try:
                results = begin_monitoring()
                print(results)
            except Exception as e:
                print(f'Error occurred in the window loop: {e}')

if __name__ == '__main__':
    main()


