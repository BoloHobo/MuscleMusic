import typing
# import matplotlib.pyplot as plt
#
# sample_data = []
#
# emg_vals = [data[1] for data in sample_data]
# time_seconds = [i for i in range(len(emg_vals))]
#
# plt.plot(time_seconds, emg_vals)
# plt.show()

# le = [1, 2, 3, 4, 5, 6, 7, 8, 9]
#
# print(le[len(le)-4:])
# val = -2500
# neg = 1 if 0>=val else -1
#
# print((-1 if 0>=val else 1)*(val%3000))

print(14%12)

# sample_list = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
#
# initial_note = 'C'
# initial_octave = '3'
#
#
# index_of_root = sample_list.index(initial_note)
# fifths_list = []
# for i in range(12):
#     index_of_root = (index_of_root + 7) % 12
#     fifths_list.append(sample_list[index_of_root])
#
# index_of_fifths = fifths_list.index(initial_note)
#
# num = 3
# index_of_fifths = (index_of_fifths + num) % 12
#
# print(f'{fifths_list[index_of_fifths]}{initial_octave}')