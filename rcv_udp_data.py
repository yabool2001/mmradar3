# Script with minimum parsing to send binary data to UDP with period 
# Rx test in linux system: sudo tcpdump -vv -A udp dst port 10004
# Tx test in linux system: echo -n "hello" >/dev/udp/10.0.0.102/10004


# ToDo zamiast wywoływać thread w każdej pętli to w funkcji thread stworzyć while który będzie działał non-stop. Zrobię to w wersji 2 

import sys
sys.path.append ( "~/python/mmradar3/modules/" )

import pprint
import struct
# sys.setdefaultencoding('utf-8')
import socket
import time
import threading


################################################################
######################## DEFINITIONS ###########################
################################################################
src_udp_ip                      = socket.gethostbyname ( socket.gethostname () )
ctrl_udp_port                   = 10004
data_udp_port                   = 10005
control                         = "ping"
udp_data_listening              = 1

hello = "\n\n##########################################\n############# mmradar started ############\n##########################################\n"

def data_udp_rx_thread () :
    while True :
        udp_data_rx = socket.socket ( socket.AF_INET , socket.SOCK_DGRAM )
        udp_data_rx.bind ( ( src_udp_ip , data_udp_port ) )
        try :
            ctrl , address = udp_data_rx.recvfrom ( 4096 )
            pprint.pprint ( ctrl.decode() )
            pprint.pprint ( address[0] )
        except struct.error as e :
            print ( e )

################################################################
################ SOCKET Configuration ##########################
################################################################
#src_udp_ctrl_rx = socket.socket ( socket.AF_INET , socket.SOCK_DGRAM )
#src_udp_ctrl_rx.setblocking ( False )
#src_udp_data_rx.settimeout ( 10 )
#src_udp_ctrl_rx.bind ( ( src_udp_ip , ctrl_udp_port ) )

##################### READ DATA #################################
#pprint.pprint ( src_udp_ip )
#while True :
#    try :
#        ctrl , address = src_udp_ctrl_rx.recvfrom ( 4096 )
#        pprint.pprint ( ctrl.decode() )
#        pprint.pprint ( address[0] )
#    except struct.error as e :
#        print ( e )
if udp_data_listening :
    data_udp_rx = threading.Thread ( target = data_udp_rx_thread )
    data_udp_rx.start ()

while True :
    pass

################# CLOSE DATA COM PORT FILE ######################
#src_udp_data_rx.close ()
#src_udp_ctrl_rx.close ()