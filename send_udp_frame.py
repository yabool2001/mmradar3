# Script to save binary data to file with minimum parsing

import serial
import serial.tools.list_ports
import struct
from mmradar_ops import mmradar_conf
from serial_ops import open_serial_ports, set_serials_cfg , close_serial_ports , open_serial_ports
import socket

################################################################
######################## DEFINITIONS ###########################
################################################################

chirp_conf                      = 2

control                         = 506660481457717506
frame                           = bytes (1)

#dst_udp_ip                      = '10.0.0.157' # Lipków raspberry pi 3b+
#dst_udp_ip                      = '192.168.43.227' # maczem raspberry pi 3b+
#dst_udp_ip                      = '192.168.43.215' # maczem GO3
#dst_udp_ip                      = '10.0.0.159' # Lipków raspberry pi 02w
dst_udp_ip                      = '10.0.0.5' # Lipków GO3
#dst_udp_ip                      = '192.168.1.17' # Meander raspberrypi
#dst_udp_ip                      = '192.168.1.30' # Meander MW50-SV0
#src_udp_ip                      = '10.0.0.157' # Lipków raspberry pi 3b+
#src_udp_ip                      = '192.168.43.227' # maczem raspberry pi 3b+
#src_udp_ip                      = '192.168.43.215' # maczem GO3
src_udp_ip                      = '10.0.0.159' # Lipków raspberry pi 02w
ctrl_udp_port                    = 10004
data_udp_port                    = 10005

#saved_raw_data_file_name       = 'save_bin_data/mmradar_gen_1655368399032378700.bin_raw_data
#saved_raw_data_file_name        = 'mmradar_gen-20220612_2.bin_raw_data'

mmradar_cfg_file_name           = 'chirp_cfg/AOP_6m_staticRetention.cfg'
#mmradar_cfg_file_name           = 'chirp_cfg/ISK_6m_default-mmwvt-v14.11.0.cfg'
mmradar_stop_cfg_file_name      = 'chirp_cfg/sensor_stop.cfg'
mmradar_start_cfg_file_name     = 'chirp_cfg/sensor_start.cfg'

sync_header_struct = 'Q'
sync_header_length = struct.calcsize ( sync_header_struct )

hello = "\n\n##########################################\n######### send_udp_frame started #########\n##########################################\n"

################################################################
################ SCRIPT START ##################################
################################################################
print ( hello )

################################################################
################ SERIALS COMM CONFiguration ####################
################################################################
conf_com = serial.Serial ()
data_com = serial.Serial ()
set_serials_cfg ( conf_com , data_com )
open_serial_ports ( conf_com , data_com )
conf_com.reset_input_buffer()
conf_com.reset_output_buffer()
if chirp_conf :
    if chirp_conf == 1 :
        mmradar_conf ( mmradar_start_cfg_file_name , conf_com )
    if chirp_conf == 2 :
        mmradar_conf ( mmradar_cfg_file_name , conf_com )
    print ("Chirp configured !")
data_com.reset_output_buffer()
data_com.reset_input_buffer ()

################################################################
################ SOCKET Configuration ##########################
################################################################
udp = socket.socket ( socket.AF_INET , socket.SOCK_DGRAM , socket.IPPROTO_UDP )

##################### READ DATA #################################
data_com.reset_output_buffer ()
data_com.reset_input_buffer ()
while True :
    frame = data_com.read ( 4666 )
    try :
        sync = struct.unpack ( sync_header_struct , frame[:sync_header_length] )
        if sync[0] == control :
            udp.sendto ( frame , ( dst_udp_ip , data_udp_port ) )
    except struct.error as e :
        pass
################# CLOSE DATA COM PORT FILE ######################
close_serial_ports ( conf_com , data_com )
udp.close ()
