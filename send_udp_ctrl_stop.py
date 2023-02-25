# Script to save binary data to file with minimum parsing

from multiprocessing.dummy import Process
import serial
import serial.tools.list_ports
import struct
from mmradar_ops import mmradar_conf
from serial_ops import open_serial_ports, set_serials_cfg , close_serial_ports , open_serial_ports
import socket

################################################################
######################## DEFINITIONS ###########################
################################################################

#dst_udp_ip                      = '10.0.0.157' # Lipków raspberry pi 3b+
#dst_udp_ip                      = '10.0.0.159' # Lipków raspberry pi 02w
#dst_udp_ip                      = '10.0.0.5' # Lipków GO3
#dst_udp_ip                      = '192.168.1.17' # Meander raspberrypi
#dst_udp_ip                      = '192.168.1.30' # Meander MW50-SV0
dst_udp_ip                      = '127.0.0.1' # maczem GO3
#src_udp_ip                      = '10.0.0.5' # Lipków GO3
#src_udp_ip                      = '10.0.0.157' # Lipków raspberry pi 3b+
#src_udp_ip                      = '10.0.0.159' # Lipków raspberry pi 02w
#src_udp_ip                      = '127.0.0.1' # maczem GO3
src_udp_ip                      = socket.gethostbyname ( socket.gethostname () )
ctrl_udp_port                    = 10004
data_udp_port                    = 10005

#saved_raw_data_file_name       = 'save_bin_data/mmradar_gen_1655368399032378700.bin_raw_data
#saved_raw_data_file_name        = 'mmradar_gen-20220612_2.bin_raw_data'

mmradar_cfg_file_name           = 'chirp_cfg/ISK_6m_default-mmwvt-v14.11.0.cfg'
mmradar_stop_cfg_file_name      = 'chirp_cfg/sensor_stop.cfg'
mmradar_start_cfg_file_name     = 'chirp_cfg/sensor_start.cfg'

ctrl_exit = b'2143'

hello = "\n\n##########################################\n######### send_udp_frame started #########\n##########################################\n"

################################################################
################ SCRIPT START ##################################
################################################################
print ( hello )

################################################################
################ SOCKET Configuration ##########################
################################################################
dst_udp = socket.socket ( socket.AF_INET , socket.SOCK_DGRAM , socket.IPPROTO_UDP )
src_udp = socket.socket ( socket.AF_INET , socket.SOCK_DGRAM , socket.IPPROTO_UDP )
src_udp.bind ( ( src_udp_ip , data_udp_port ) )
################ MAIN ##########################################
dst_udp.sendto ( ctrl_exit , ( dst_udp_ip , ctrl_udp_port ) )
#frame , address = src_udp.recvfrom ( 4666 )
################# CLOSE DATA COM PORT FILE #####################
src_udp.close ()
dst_udp.close ()