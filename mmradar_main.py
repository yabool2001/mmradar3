# ToDo:
# thread do wysyłania UDP i zapisywania do log
# zarządzanie przez UDP
# możliwość rzadszego parsowania pakietów np. co 10, ustawianie przez UDP
# crontab do uruchamiania skryptu po każdym reboot

# Wymagania dla Linux
# sys.path.append ( "/home/mzemlo/mmradar3/modules/" )
# sudo apt install python3-pip
# python -m pip install pyserial

# Przykłady operacji w Linux
# cd /home/mzemlo/mmradar3
# python mmradar_main3.py
# tail -f mmradar.log
# sudo tcpdump -A  port 10005
# Rx test in linux system: sudo tcpdump -vv -A udp dst port 10004
# Tx test in linux system: echo -n "ctrl.data_dst.3" >/dev/udp/10.0.0.102/10004
# Tx test in linux system: echo -n "ctrl.data_dst_frame_divider.100" >/dev/udp/10.0.0.102/10004

import os
import sys
#sys.setdefaultencoding('utf-8')
#sys.path.append ( "/Users/mzeml/python/mmradar3/modules/" )
sys.path.append ( "/Users/mzeml/python/mmradar3/modules/" )
sys.path.append ( "/home/mzemlo/python/mmradar3/modules/" )
import logging
import pprint

import datetime
import file_ops
import mmradar_ops
import mmradar_pc3d
import socket
import serial
import serial_ops
import threading
import time

#from mmradar_ops2 import mmradar_conf
#from file_ops2 import write_data_2_local_file

################################################################
### DEFINITIONS 
################################################################

data_src                        = 0 # 0: device, 1: UDP, 2: file
cfg_chirp                       = 2 # 0: no cfg, 1: sensor start, 2: full cfg
cfg_ctrl                        = 1 # 0: no cfg, 1: udp cfg
data_dst                        = 0 # 0: no dst, 1: UDP, 2: Azure, 3: file
data_dst_frame_divider          = 100 # co która ramka ma być zapisywana
ctrl_start                      = 0
raw_byte                        = bytes(1)
frames_limit                    = 0
log_file_name                   = 'log/mmradar.log'
data_file_name                  = 'mmradar.data'
saved_parsed_data_file_name     = 'saved_parsed_data/mmradar.data.json'
saved_bin_data_file_name        = 'saved_bin_data/mmradar_gen_1675746223207587500.bin_raw_data'
cfg_chirp_full_file_name        = 'chirp_cfg/ISK_6m_staticRetention.cfg'
cfg_chirp_start_file_name       = 'chirp_cfg/sensor_start.cfg'
src_udp_ip                      = socket.gethostbyname ( socket.gethostname () )
#dst_udp_ip                      = '10.0.0.102' # Lipków MW50-SV0
dst_udp_ip                      = '10.0.0.157' # Lipków raspberry pi 3b+
#dst_udp_ip                      = '192.168.43.227' # maczem raspberry pi 3b+
#dst_udp_ip                      = '192.168.43.215' # maczem GO3
#dst_udp_ip                      = '127.0.0.1' # localhost
ctrl_udp_ip                      = [ '10.0.0.102' , '10.0.0.157' , '10.0.0.159', '192.168.43.215' , '192.168.43.227']# Lipków raspberry pi 3b+
ctrl_udp_port                    = 10004
data_udp_port                    = 10005

def data_udp_ctrl_rx_thread () :
    global data_dst
    global data_dst_frame_divider
    src_udp_ctrl_rx = socket.socket ( socket.AF_INET , socket.SOCK_DGRAM )
    src_udp_ctrl_rx.bind ( ( src_udp_ip , ctrl_udp_port ) )
    while True :
        try :
            ctrl , address = src_udp_ctrl_rx.recvfrom ( 4096 )
            logging.info ( f"############# Got {ctrl.decode ()} from {address[0]}\n")
            ctrl_split = ( ctrl.decode ().split ( '.' ) )
            if ctrl_split[0] == "ctrl" and address[0] in ctrl_udp_ip :
                if ctrl_split[1] == 'data_dst' :
                    if ctrl_split[2] == '0' :
                        data_dst = 0
                    elif ctrl_split[2] == '1' :
                        data_dst = 1
                    elif ctrl_split[2] == '2' :
                        data_dst = 2
                    elif ctrl_split[2] == '3' :
                        data_dst = 3
                    else :
                        logging.info ( f"############# Unknown data_dst value {ctrl_split[2]} from {address[0]}\n")
                if ctrl_split[1] == "data_dst_frame_divider" :
                    if ctrl_split[2].isdigit()  :
                        data_dst_frame_divider = int ( ctrl_split[2] ) if int ( ctrl_split[2] ) >= 1 else 1
                if ctrl_split[1] == "device" :
                    if ctrl_split[2] == "reboot" :
                        os.system ( 'sudo reboot' )
            else :
                logging.info ( f"############# Unknown command {ctrl.decode ()} from {address[0]}\n")
        except struct.error as e :
            print ( e )
    #src_udp_ctrl_rx.close ()
        #udp.sendto ( str.encode ( str ( pc3d_object.frame_dict ) , "utf-8" ) , ( dst_udp_ip , data_udp_port ) )

def data_dst_3_thread () :
    file_ops.write_2_local_file ( saved_parsed_data_file_name , str ( pc3d_object.frame_dict ) )
def data_dst_1_thread () :
    udp_data_tx.sendto ( str.encode ( str ( pc3d_object.frame_dict ) , "utf-8" ) , ( dst_udp_ip , data_udp_port ) )

hello = "\n\n##########################################\n############# mmradar started ############\n##########################################"

################################################################
###################### LOGGING CONFIG ##########################
################################################################

LOG_FORMAT = '%(asctime)s;%(message)s;%(funcName)s;line:%(lineno)d;%(levelname)s'
logging.basicConfig ( filename = log_file_name , level = logging.INFO , format = LOG_FORMAT )

################################################################
################ SERIALS COMM CONFiguration ####################
################################################################

################################################################
####################### START PROGRAM ##########################
################################################################

logging.info ( hello )

### READ DATA
if data_src == 0 :
    logging.info ( f"############# Direct device sourcing.\n")
    conf_com = serial.Serial ()
    data_com = serial.Serial ()
    serial_ops.set_serials_cfg ( conf_com , data_com )
    serial_ops.open_serial_ports ( conf_com , data_com )
    if cfg_chirp == 0 :
        logging.info ( f"############# Device no cfg.\n")
    elif cfg_chirp ==  1 :
        mmradar_ops.mmradar_conf ( cfg_chirp_start_file_name , conf_com )
        logging.info ( f"############# Device started.\n")
    elif cfg_chirp ==  2 : # full cfg
        mmradar_ops.mmradar_conf ( cfg_chirp_full_file_name , conf_com )
        print ( "\n############# Device full cfg.\n" )
        logging.info ( f"############# Device full cfg.\n")
    conf_com.close ()
elif data_src == 1:
    logging.info ( f"############# UDP sourcing. App exit!\n")
    exit ()
elif data_src == 2:
    logging.info ( f"############# Saved raw data sourcing.\n")
    saved_bin_frames = open ( saved_bin_data_file_name , 'r' ) .readlines ()
    frames_limit = len ( saved_bin_frames )
else :
    logging.info (f"Error: data_src not known. App exit!\n")
    exit ()

if data_dst == 0 :
    logging.info (f"Error: No data destination.\n")
elif data_dst == 1 :
    ################ SOCKET Configuration
    # Konfiguracja gniazda do nadawania danych
    udp_data_tx = socket.socket ( socket.AF_INET , socket.SOCK_DGRAM , socket.IPPROTO_UDP )
    logging.info ( f"############# UDP destination socket configured.\n")
elif data_dst == 2 :
    logging.info (f"Error: Data destination Azure.\n")
elif data_dst == 3 :
    logging.info (f"Error: Data destination local file.\n")

if ( cfg_ctrl ) :
    thread_udp_ctrl_rx = threading.Thread ( target = data_udp_ctrl_rx_thread )
    thread_udp_ctrl_rx.start ()
    logging.info ( f"############# UDP ctrl configured.\n")

i = 0
while ( i < frames_limit or data_src < 2 ) :
    if data_src == 0 :
        pc3d_object = mmradar_pc3d.PC3D ()
        if pc3d_object.get_frame_header_from_device ( data_com ) :
            pc3d_object.get_tlvs ()
    elif data_src == 1 :
        logging.info (f"Error: data_src = 1. App exit!\n")
        exit ()
    elif data_src ==  2 :
        pc3d_object = mmradar_pc3d.PC3D ()
        if pc3d_object.get_frame_header_from_saved_bytes ( eval ( saved_bin_frames[i] ) ) :
            pc3d_object.get_tlvs ()
        i += 1
    if pc3d_object.frame_dict.get ('frame_header') :
        if int ( pc3d_object.frame_dict['frame_header'].get ( 'frame_number' ) ) % data_dst_frame_divider == 0 :
            if data_dst == 0 :
                pass
            elif data_dst == 1 :
                #udp_data_tx.sendto ( str.encode ( str ( pc3d_object.frame_dict ) , "utf-8" ) , ( dst_udp_ip , data_udp_port ) ) # alternatywa dla 2 poniższych wierszy
                thread_data_dst_1 = threading.Thread ( target = data_dst_1_thread )
                thread_data_dst_1.start ()
            elif data_dst == 2 :
                pass
            elif data_dst == 3 :
                #file_ops.write_2_local_file ( saved_parsed_data_file_name , str ( pc3d_object.frame_dict ) ) # alternatywa dla 2 poniższych wierszy
                thread_data_dst_3 = threading.Thread ( target = data_dst_3_thread )
                thread_data_dst_3.start ()
    del pc3d_object

if data_src == 0 :
    data_com.close ()
elif data_src == 1 or data_dst == 1 :
    udp_data_tx.close ()
    udp_ctrl_rx.close ()
logging.info (f"App end.\n")