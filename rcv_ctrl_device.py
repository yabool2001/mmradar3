# Script with minimum parsing to send binary data to UDP with period 
# Rx test in linux system: sudo tcpdump -vv -A udp dst port 10004
# Tx test in linux system: echo -n "hello" >/dev/udp/10.0.0.102/10004

import os
import sys
sys.path.append ( "/Users/mzeml/python/mmradar3/modules/" )
sys.path.append ( "/home/mzemlo/python/mmradar3/modules/" )

import logging
import struct
import socket
import threading


################################################################
######################## DEFINITIONS ###########################
################################################################
src_udp_ip                      = socket.gethostbyname ( socket.gethostname () )
src_udp_ip                      = '0.0.0.0'
ctrl_device_udp_port            = 10003
ctrl_udp_port                   = 10004
data_udp_port                   = 10005
ctrl_udp_ip                     = [ '10.0.0.102' , '10.0.0.157' , '10.0.0.159', '192.168.43.215' , '192.168.43.227'] # Lipków raspberry pi 3b+
log_file_name                   = 'log/mmradar.log'

hello = "\n\n##########################################\n########## rcv_udp_ctrl_device started ###\n##########################################\n"

################################################################
################ LOG Configuration #############################
################################################################

LOG_FORMAT = '%(asctime)s;%(message)s;%(funcName)s;line:%(lineno)d;%(levelname)s'
logging.basicConfig ( filename = log_file_name , level = logging.INFO , format = LOG_FORMAT )

logging.info ( hello )

src_udp_ctrl_rx = socket.socket ( socket.AF_INET , socket.SOCK_DGRAM )
src_udp_ctrl_rx.bind ( ( src_udp_ip , ctrl_device_udp_port ) )
logging.info ( f"Ctrl device started.")
logging.info ( f"{src_udp_ctrl_rx.getsockname()}\n")

while True :
    try :
        ctrl , address = src_udp_ctrl_rx.recvfrom ( 1024 )
        logging.info ( f"Got {ctrl.decode ()} from {address[0]}\n")
        ctrl_split = ( ctrl.decode ().split ( '.' ) )
        if ctrl_split[0] == "ctrl" and address[0] in ctrl_udp_ip :
            if ctrl_split[1] == "device" :
                if ctrl_split[2] == "reboot" :
                    os.system ( 'sudo reboot' )
                    logging.info ( f"{ctrl.decode()} execution.\n")
            else :
                logging.info ( f"Unknown {ctrl.decode()} command from {address[0]}\n")
        else :
            logging.info ( f"Unknown  {ctrl.decode ()} command from {address[0]}\n")
    except struct.error as e :
        print ( e )

################# CLOSE DATA COM PORT FILE ######################
#src_udp_data_rx.close ()
#src_udp_ctrl_rx.close ()