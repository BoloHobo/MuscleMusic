
class Note:

    def __init__(self, scale, octave):
        self.note = scale
        self.octave = octave
        self.notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

    # @property
    # def note_number(self):
    #     return self.note_number

    @property
    def scale_note(self):
        return f'{self.note}{self.octave}'

    def get_scale_notes(self, scale_type):

        root_index = self.notes.index(self.note)
        scale_intervals = {
            'major': [0, 2, 4, 5, 7, 9, 11],
            'minor': [0, 2, 3, 5, 7, 8, 10]
        }
        scale_notes = [(root_index + interval) for interval in scale_intervals[scale_type]]
        scale_notes = [f'{self.notes[index%12]}{self.octave + int(index/12)}' for index in scale_notes]

        return scale_notes

    def get_triad_chord(self, chord_type, note=None, diminished=False):
        # Define intervals for Major and Minor chords
        if not note:
            note = self.note

        intervals = {
        'major': [0, 4, 7] if not diminished else [0, 3, 6],  # Root, Major third, Perfect fifth unless diminished
        'minor': [0, 3, 7]  # Root, Minor third, Perfect fifth
        }

        root_index = self.notes.index(note)
        # print(root_index)
        # Calculate the triad notes
        # print([f'{(root_index + interval) % 12}' for interval in intervals[chord_type]])
        # for interval in intervals[chord_type]:
        #     print(f'{interval} | {chord_type}')
        chord_notes = [f'{self.notes[(root_index + interval) % 12]}{self.octave + int((root_index + interval)/12)}' for interval in intervals[chord_type]]

        return chord_notes

    def get_related_chords(self, chord_type):
        chord_scale = ['minor', 'major']
        if chord_type == 'major':
            diminished = False
        else:
            diminished = True

        # Calculate primary and secondary chords
        if self.note in self.notes:
            index = self.notes.index(self.note)
            # Primary chords: Tonic (I), Subdominant (IV), Dominant (V)
            primary = [
                f'{self.notes[index]}{self.octave + int(index/12)}',  # Tonic
                f'{self.notes[(index + 5) % len(self.notes)]}{self.octave + int((index+5)/12)}',  # Subdominant
                f'{self.notes[(index + 7) % len(self.notes)]}{self.octave + int((index+7)/12)}'   # Dominant
            ]

            # Secondary chords: Supertonic (ii), Mediant (iii), Submediant (VI)
            secondary = [
                f'{self.notes[(index + 2) % len(self.notes)]}{self.octave + int((index+2)/12)}',  # Supertonic
                f'{self.notes[(index + 4-int(diminished)) % len(self.notes)]}{self.octave + int((index+4)/12)}',  # Mediant
                f'{self.notes[(index + 9-int(diminished)) % len(self.notes)]}{self.octave + int((index+9)/12)}',  # Submediant
            ]

            primary_triads = []
            for chord_note in primary:
                primary_triads.append(self.get_triad_chord(chord_type, chord_note[:-1]))

            secondary_triads = []
            for chord_note in secondary:
                if chord_type == 'minor' and chord_note == secondary[0]:
                    secondary_triads.append(self.get_triad_chord(chord_scale[int(diminished)], chord_note[:-1], diminished))
                    continue
                secondary_triads.append(self.get_triad_chord(chord_scale[int(diminished)], chord_note[:-1]))

            return primary, secondary, primary_triads, secondary_triads
        else:
            return None, None, None, None