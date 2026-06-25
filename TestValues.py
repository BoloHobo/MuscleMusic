import sys
import os
project_dir = os.path.dirname(__file__)
package_dir = os.path.join(project_dir, 'uMyo_tools')
sys.path.append(package_dir)
import umyo_parser

# list
from serial.tools import list_ports
port = list(list_ports.comports())
print("available ports:")
for p in port:
    print(p.device)
    if p.device == 'COM3':
        device = p.device
print("===")

#read
import serial
ser = serial.Serial(port=device, baudrate=921600, parity=serial.PARITY_NONE, stopbits=1, bytesize=8, timeout=0)

print("conn: " + ser.portstr)
last_data_upd = 0
# display_stuff.plot_init()
parse_unproc_cnt = 0
while(1):
    cnt = ser.in_waiting
    if(cnt > 0):
#        print(parse_unproc_cnt)
        cnt_corr = parse_unproc_cnt/200
        data = ser.read(cnt)
        parse_unproc_cnt = umyo_parser.umyo_parse_preprocessor(data)
        devices = umyo_parser.umyo_get_list()
        cnt = len(devices)
        if (cnt < 1): continue
        for dev in devices:
            # val = vars(dev)
            val = dev.roll
            print(val)

        # break
        # for x in range(devices[0].data_count):
        #     val = devices[0].data_array[x]
        #     print(val)
        # for dev in devices:
        #     print(f'\rArray: {dev.data_array}')
        #     print(f'\rSpectr: {dev.device_spectr}')

        # parse_unproc_cnt = umyo_parser.umyo_parse_preprocessor(data)
        # sys.stdout.flush()
        # dat_id = display_stuff.plot_prepare(umyo_parser.umyo_get_list())
        # d_diff = 0
        # if(not (dat_id is None)):
        #     d_diff = dat_id - last_data_upd
        # if(d_diff > 2 + cnt_corr):
            #display_stuff.plot_cycle_lines()
            # display_stuff.plot_cycle_tester()
            # last_data_upd = dat_id

