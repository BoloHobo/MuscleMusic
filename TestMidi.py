import random
import time
import mido
from MusicalValues import Note

octave = 3
note = 'C'
base_note = Note(note, octave)
notes_dict = {}
# Number of octaves
for octave_range in range(2, 7):
    # Notes in each octave
    for note_selection in base_note.notes:
        number = (base_note.notes.index(note_selection)) + (octave_range * 12)
        notes_dict[f'{note_selection}{octave_range - 2}'] = number
# print(notes_dict)
primary_chords, secondary_chords, primary_triads, secondary_triads = base_note.get_related_chords('minor')
notes = []
notes.extend([eph_note for eph_note in primary_chords])
notes.extend([eph_note for eph_note in secondary_chords])
for eph_notes in primary_triads:
    notes.extend([eph_note for eph_note in eph_notes])
for eph_notes in secondary_triads:
    notes.extend([eph_note for eph_note in eph_notes])

while True:
    random_note = notes_dict[random.choice(notes)]
    note_on = mido.Message('note_on', note=random_note, channel=2, velocity=100)
    note_on_2 = mido.Message('note_on', note=random_note+4, channel=3, velocity=100)
    note_off = mido.Message('note_off', note=random_note, channel=2, velocity=100)
    with mido.open_output('virtualMidi 1', autoreset=True) as output:
        output.send(note_on)
        output.send(note_on_2)
        time.sleep(1)
        output.send(note_off)

