import logging
import math
import sys
import os
import PySimpleGUI as sg
from numpy.ma.extras import average

from TestMidi import notes_dict

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
    device_dict = {3709404326: {'Device ID': 3709404326, 'Note': '', 'Chord': [], 'Muscle': 'Right Forearm',
                                'Active': False, 'Playing': False, 'Channel': 2},
                   1723834707: {'Device ID': 1723834707, 'Note': '', 'Chord': [], 'Muscle': 'Left Forearm',
                                'Active': False, 'Playing': False,'Channel': 3},
                   1192667876: {'Device ID': 1192667876, 'Note': '', 'Chord': [], 'Muscle': 'Right Bicep',
                                'Active': False, 'Playing': False,'Channel': 4},
                   3369251029: {'Device ID': 3369251029, 'Note': '', 'Chord': [], 'Muscle': 'Left Bicep',
                                'Active': False, 'Playing': False,'Channel': 5},
                   2821543978: {'Device ID': 2821543978, 'Note': '', 'Chord': [], 'Muscle': 'Right Lat',
                                'Active': False, 'Playing': False,'Channel': 6},
                   2497006410: {'Device ID': 2497006410, 'Note': '', 'Chord': [], 'Muscle': 'Left Lat',
                                'Active': False, 'Playing': False,'Channel': 7}}

    base_note = Note(root, octave)
    scale = 'major'
    primary_chords, secondary_chords, primary_triads, secondary_triads = base_note.get_related_chords(scale)
    # R_forearm['Note'], R_bicep['Note'], R_back['Note'] = primary_chords
    # L_forearm['Note'], L_bicep['Note'], L_back['Note'] = secondary_chords
    chords = primary_chords + secondary_chords
    triads = primary_triads + secondary_triads
    print(chords)
    print(triads)
    chord_index = 0
    for device in device_dict.values():
        device['Note'] = chords[chord_index]
        device['Chord'] = triads[chord_index]
        chord_index += 1
    # print(device_dict)
    notes_dict = {}
    # Number of octaves
    for octave_range in range(2, 7):
        # Notes in each octave
        for note_selection in base_note.notes:
            number = (base_note.notes.index(note_selection)) + (octave_range * 12)
            notes_dict[f'{note_selection}{octave_range - 2}'] = number
    # print(notes_dict)
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
            musical_queue = []
            for dev in device_dict.keys():
                device_emg_data[dev] = []
                device_const_stream[dev] = 0
            print(device_emg_data)
            print(mido.get_output_names())
            output = mido.open_output('loopMIDI Port 1')
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
                                    music_value = active_device['Chord']
                                    active_device_count = 0
                                    if buffer_value > 300:
                                        if not active_device['Active']:
                                            active_device['Active'] = True
                                        active_device_count = sum(1 for device_num, device_values in device_dict.items() if device_values['Active'])
                                        if active_device_count <= 1:
                                            if not active_device['Playing']:
                                                play_note(music_value, active_device['Channel'], output)
                                                active_device['Playing'] = True
                                            # change_volume(device_emg_data, active_device, buffer_value, output)
                                            # Flip switch to track consecutive flexion sustain
                                            device_const_stream[device_id] += 1
                                            if device_const_stream[device_id] > 500:
                                                add_flourish(dev=dev, active_device=active_device, output=output, ser=ser, device_emg_data=device_emg_data)
                                        else:
                                            musical_queue = [device_values['Chord'] for device_num, device_values in device_dict.items() if device_values['Playing']]
                                            # for chord, channel in playing_notes:
                                            #     turn_note_off(chord, channel, output)
                                            # active_notes = [(device_values['Chord'], device_values['Channel']) for device_num, device_values in device_dict.items() if device_values['Active']]
                                            # for chord, channel in active_notes:
                                            if not active_device['Playing']:
                                                musical_queue.append(active_device['Chord'])
                                                active_device['Playing'] = True
                                            print(musical_queue)

                                            # for chord in musical_queue:
                                            #     arpeggiate(chord, 15, output, ser=ser, device_emg_data=device_emg_data[active_device['Device ID']])

                                            # musical_queue.append(music_value)
                                            # for music in musical_queue:
                                            #     if not active_device['Playing']:
                                            #         play_note(music, active_device['Channel'], output)
                                            #         active_device['Playing'] = True
                                    else:
                                        if active_device['Active']:
                                            if active_device_count > 1:
                                                del musical_queue[musical_queue.index(active_device['Chord'])]
                                            turn_note_off(music_value, active_device['Channel'], output)
                                            device_const_stream[device_id] = 0
                                            active_device['Active'] = False
                                            active_device['Playing'] = False
                            except Exception as e:
                                print(f'Error occurred: {e}')


                else:
                    break
            for device in device_dict.values():
                if device['Active']:
                    turn_note_off(device['Note'], device['Channel'], output)
            output.close()
    return total_uMyo_emg

def play_note(music, channel, output_reader, velocity=127):
    if isinstance(music, list):
        chord = music
        for note in chord:
            note_on = mido.Message('note_on', note=notes_dict[note], channel=channel, velocity=velocity)
            output_reader.send(note_on)
        # time.sleep(.5)
        # turn_note_off([chord[0], chord[2]], channel, output_reader, velocity)
    else:
        note_on = mido.Message('note_on', note=notes_dict[music], channel=channel, velocity=velocity)
        output_reader.send(note_on)

def turn_note_off(music, channel, output_reader, velocity=127):
    if isinstance(music, list):
        chord = music
        for note in chord:
            note_off = mido.Message('note_off', note=notes_dict[note], channel=channel, velocity=velocity)
            output_reader.send(note_off)
    else:
        note_off = mido.Message('note_off', note=notes_dict[music], channel=channel, velocity=velocity)
        output_reader.send(note_off)

def modify_note(change_type, channel, output_reader, control_val=None, value=0):
    if control_val:
        note_mod = mido.Message(change_type, channel=channel, control=control_val, value=value)
    output_reader.send(note_mod)

def flourish(base_note, channel, output, pivot_scale, flip_melody=False):
    pivot_key = base_note[0]
    pivot_octave = int(base_note[-1])
    pivot_note = Note(pivot_key, pivot_octave)
    pivot_primary, pivot_secondary, pivot_primary_triad, pivot_secondary_triad = pivot_note.get_related_chords(pivot_scale, flip_melody)
    # notes_queue = []
    first_primary_triad = reversed(pivot_primary_triad[0]) if flip_melody else pivot_primary_triad[0]
    # print(first_primary_triad)
    for note in first_primary_triad:
        # for note in chord:
        play_note(note, channel, output)
        time.sleep(.25)
        turn_note_off(note, channel, output)
    return first_primary_triad

def change_volume(device_emg_data, active_device, buffer_value, output):
    # Create volume buffer for normalization
    max_emg_val = max(
        device_emg_data[active_device['Device ID']][len(device_emg_data[active_device['Device ID']]) - 1500:])
    # min_emg_val = min(device_emg_data[active_device['Device ID']][len(device_emg_data[active_device['Device ID']])-1500:])
    min_emg_val = 300
    vol_ratio = (buffer_value - min_emg_val) / (max_emg_val - min_emg_val)
    volume = int(math.sqrt((127 ** 2) * (abs(vol_ratio))))
    if volume >= 127:
        volume = 127
    modify_note('control_change', active_device['Channel'], output, control_val=7, value=volume)

def add_flourish(dev, active_device, output, ser, device_emg_data):
    # Signal changes based on sensor orientation
    if dev.pitch < 0:
        scale = 'minor'
    else:
        scale = 'major'
    # roll = (-1 if dev.roll<0 else 1) * (dev.roll % 3000)
    # print(roll)
    # if roll > 0:
    #     reverse_notes = False
    # else:
    #     reverse_notes = True
    flourish(active_device['Note'], active_device['Channel'], output, scale)
    ser.reset_input_buffer()
    device_emg_data[active_device['Device ID']] = []

def arpeggiate(chord, channel, output, ser, device_emg_data, velocity=127):
    for note in chord:
        play_note(note, channel, output)
        time.sleep(.5)
        turn_note_off(note, channel, output)
        ser.reset_input_buffer()
        device_emg_data = []
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


