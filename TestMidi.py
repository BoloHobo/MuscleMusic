import random
import time
import mido
from MusicalValues import Note

octave = 2
key = 'F#'
scale = Note(key, octave)
notes_dict = {}
# Number of octaves
for octave_range in range(2, 7):
    # Notes in each octave
    for note_selection in scale.notes:
        number = (scale.notes.index(note_selection)) + (octave_range * 12)
        notes_dict[f'{note_selection}{octave_range - 2}'] = number
# print(notes_dict)
# primary_chords, secondary_chords, primary_triads, secondary_triads = scale.get_related_chords('minor')
print(scale.get_related_chords('minor'))
# related_chords = []
# for chord in primary_triads:
#     related_chords.append(chord)
#     for note in chord:
#         pivot_root = note[0]
#         pivot_octave = int(note[-1])
#         pivot_scale = Note(pivot_root, pivot_octave)
#         pivot_primary, pivot_secondary, pivot_primary_triad, pivot_secondary_triad = pivot_scale.get_related_chords('major')
#         related_chords.extend(pivot_primary_triad)
#         related_chords.extend(pivot_secondary_triad)
# related_chords_deduped = []
# for chord in related_chords:
#     if chord not in related_chords_deduped:
#         related_chords_deduped.append(chord)
# with mido.open_output('virtualMidi 1', autoreset=True) as output:
    # inputs = mido.open_input('virtualMidi 0')
    # note_on = mido.Message('note_on', note=notes_dict[f'C2'], channel=3, velocity=127)
    # msg = ''
    # output.send(mido.Message('note_on', note=61, channel=3, velocity=127))
    # msg += str(inputs.receive())
    # output.send(mido.Message('note_on', note=49, channel=3, velocity=127))
#     msg += str(inputs.receive())
#     print(msg)
    # note_on = mido.Message('note_on', note=notes_dict[f'{note}{octave}'], channel=3, velocity=75)
    # output.send(note_on)
    # time.sleep(2)
    # while True:
    #
    #     for chord in related_chords_deduped:
    #         note_buffer = []
    #         for note in (chord):
    #             note_buffer.append(note)
    #             output.send(mido.Message('note_on', note=notes_dict[note], channel=3, velocity=100))
    #             time.sleep(.1)
    #             last_note = note
    #         for note in reversed(chord):
    #             if note == last_note:
    #                 continue
    #             note_buffer.append(note)
    #             output.send(mido.Message('note_on', note=notes_dict[note], channel=3, velocity=100))
    #             time.sleep(.1)
    #         time.sleep(.1)
    #         for note in note_buffer:
    #             output.send(mido.Message('note_off', note=notes_dict[note], channel=3, velocity=100))
    #     time.sleep(10)
        # random_note = notes_dict[random.choice(notes)]
        # note_mod = mido.Message('control_change', channel=3, control=10, value=64)
        # note_off = mido.Message('note_off', note=note, channel=3, velocity=100)



