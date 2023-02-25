import logging
import platform
import serial
import serial.tools.list_ports
import time

def set_serials_cfg ( conf_com , data_com ) :
    serial_ports =  serial.tools.list_ports.comports()
    for s_p in serial_ports:
        if 'CP2105'.lower () in s_p.description.lower () and 'Enhanced'.lower () in s_p.description.lower ():
            if platform.system () == "Windows":
                conf_com.port = s_p.name
            elif platform.system () == "Linux":
                conf_com.port = '/dev/' + s_p.name
            else:
                logging.info ( f"Error: No compatible os!" )
        if 'CP2105'.lower () in s_p.description.lower () and 'Standard'.lower () in s_p.description.lower ():
            if platform.system () == "Windows":
                data_com.port = s_p.name
            elif platform.system () == "Linux":
                data_com.port = '/dev/' + s_p.name
            else:
                logging.info ( f"Error: No compatible os!")
    conf_com.baudrate       = 115200
    data_com.baudrate       = 921600
    #conf_com.bytesize       = serial.EIGHTBITS
    #data_com.bytesize       = serial.EIGHTBITS
    conf_com.parity         = serial.PARITY_NONE
    data_com.parity         = serial.PARITY_NONE
    conf_com.stopbits       = serial.STOPBITS_ONE
    data_com.stopbits       = serial.STOPBITS_ONE
    conf_com.timeout        = 0.3
    data_com.timeout        = 0.3
    conf_com.write_timeout  = 1

def close_serial_ports ( *sp ) :
    for i in sp :
        if i.is_open :
            try:
                i.close ()
                logging.info ( f"{i.name} port is closed" )
            except serial.SerialException as e :
                logging.info ( f"{i.name} port closing error: {str(e)}" )

def open_serial_ports ( *sp ) :
    for i in sp :
        try: 
            i.open ()
            logging.info ( f"{i.name} port opened" )
        except serial.SerialException as e :
            logging.info ( f"{i.name} port error opening: {str(e)}" )