import logging
import time

def chirp_conf ( chirp_cfg , conf_com ) :
    for line in chirp_cfg :
        time.sleep(.1)
        conf_com.write ( line.encode () )
        ack = conf_com.readline ()
        logging.info ( f"{conf_com.name} port ack: {ack}" )
        ack = conf_com.readline ()
        logging.info ( f"{conf_com.name} port ack: {ack}" )
        time.sleep ( 3 )
        conf_com.reset_input_buffer ()

def mmradar_conf ( conf_file_name , conf_com ) :
    try:
        with open ( f'{conf_file_name}' , 'r' , encoding='utf-8' ) as conf_file:
            if conf_file.readable () :
                logging.info ( f"{conf_file.name} file is readable" )
            cfg = conf_file.readlines()
    except IOError as e :
        logging.info ( f"{conf_file.name} file opening problem... {str(e)}" )

    conf_com.reset_input_buffer ()
    conf_com.reset_output_buffer ()
    for line in cfg :
        time.sleep(.03)
        conf_com.write ( line.encode () )
        ack = conf_com.readline ()
        logging.info ( f"{conf_com.name} port ack: {ack}" )
        ack = conf_com.readline ()
        logging.info ( f"{conf_com.name} port ack: {ack}" )
        time.sleep ( 3 )
    conf_com.reset_input_buffer ()

################################################################
############# STOP SENSOR AND CLOSE CONF COM PORT ##############
################################################################
# Stop sensor (freez until know how to start it properly)
# conf_com.write ( 'sensorStop\n'.encode () )
# ack = conf_com.readline ()
# log_file.write ( f'\n{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {conf_com.name} port ack: {ack}' )
# ack = conf_com.readline ()
# log_file.write ( f'\n{time.gmtime ().tm_hour}:{time.gmtime ().tm_min}:{time.gmtime ().tm_sec} {conf_com.name} port ack: {ack}' )
# time.sleep ( 3 )
# conf_com.reset_input_buffer ()
# Close CONF COM Port