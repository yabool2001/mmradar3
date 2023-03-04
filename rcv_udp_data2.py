# Script with minimum parsing to send binary data to UDP with period 
# Rx test in linux system: sudo tcpdump -vv -A udp dst port 10004
# Tx test in linux system: echo -n "hello" >/dev/udp/10.0.0.102/10004


# ToDo zamiast wywoływać thread w każdej pętli to w funkcji thread stworzyć while który będzie działał non-stop. Zrobię to w wersji 2 
# Sprawdzić czy działa

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
udp_ctrl_listening              = 0

hello = "\n\n##########################################\n############# mmradar started ############\n##########################################\n"

def data_udp_ctrl_rx_thread () :
    global control
    src_udp_ctrl_rx = socket.socket ( socket.AF_INET , socket.SOCK_DGRAM )
    src_udp_ctrl_rx.bind ( ( src_udp_ip , ctrl_udp_port ) )
    while True :
        try :
            ctrl , address = src_udp_ctrl_rx.recvfrom ( 4096 )
            pprint.pprint ( ctrl.decode() )
            pprint.pprint ( address[0] )
            control = ctrl.decode()
        except struct.error as e :
            print ( e )
    #src_udp_ctrl_rx.close ()
        #udp.sendto ( str.encode ( str ( pc3d_object.frame_dict ) , "utf-8" ) , ( dst_udp_ip , data_udp_port ) )

################################################################
################ SOCKET Configuration ##########################
################################################################
#src_udp_ctrl_rx = socket.socket ( socket.AF_INET , socket.SOCK_DGRAM )
#src_udp_ctrl_rx.setblocking ( False )
#src_udp_data_rx.settimeout ( 10 )
#src_udp_ctrl_rx.bind ( ( src_udp_ip , ctrl_udp_port ) )

##################### READ DATA #################################
pprint.pprint ( src_udp_ip )
#while True :
#    try :
#        ctrl , address = src_udp_ctrl_rx.recvfrom ( 4096 )
#        pprint.pprint ( ctrl.decode() )
#        pprint.pprint ( address[0] )
#    except struct.error as e :
#        print ( e )
if udp_ctrl_listening == 0 :
    thread_udp_ctrl_rx = threading.Thread ( target = data_udp_ctrl_rx_thread )
    thread_udp_ctrl_rx.start ()
start_t = time.perf_counter ()
while True :
    finish_t = time.perf_counter ()
    if finish_t - start_t > 2 :
        print ( control )
        start_t = time.perf_counter ()

################# CLOSE DATA COM PORT FILE ######################
#src_udp_data_rx.close ()
#src_udp_ctrl_rx.close ()