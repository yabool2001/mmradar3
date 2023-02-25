# Script with minimum parsing to send binary data to UDP with period 
# Test in linux system: sudo tcpdump -vv -A udp dst port 10005

import sys
sys.path.append ( "~/python/mmradar3/modules/" )

import pprint
import struct
# sys.setdefaultencoding('utf-8')
import socket


################################################################
######################## DEFINITIONS ###########################
################################################################
src_udp_ip                      = socket.gethostbyname ( socket.gethostname () )
ctrl_udp_port                   = 10004
data_udp_port                   = 10005

hello = "\n\n##########################################\n############# mmradar started ############\n##########################################\n"

################################################################
################ SOCKET Configuration ##########################
################################################################
src_udp_ctrl_rx = socket.socket ( socket.AF_INET , socket.SOCK_DGRAM )
#src_udp_ctrl_rx.setblocking ( False )
#src_udp_data_rx.settimeout ( 10 )
src_udp_ctrl_rx.bind ( ( src_udp_ip , ctrl_udp_port ) )

##################### READ DATA #################################
pprint.pprint ( src_udp_ip )
#while True :
#    try :
#        ctrl , address = src_udp_ctrl_rx.recvfrom ( 4096 )
#        pprint.pprint ( ctrl.decode() )
#        pprint.pprint ( address[0] )
#    except struct.error as e :
#        print ( e )
try :
    ctrl , address = src_udp_ctrl_rx.recvfrom ( 4096 )
    pprint.pprint ( ctrl.decode() )
    pprint.pprint ( address[0] )
except struct.error as e :
    print ( e )
################# CLOSE DATA COM PORT FILE ######################
#src_udp_data_rx.close ()
src_udp_ctrl_rx.close ()