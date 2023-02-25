import logging
import pprint
import time
import struct


class PC3D :
    def __init__ ( self , data_com ) :
        self.data_com = data_com
        self.tlvs_bytes = bytearray(b'')
        #self.control = 506660481457717506 # poprzednio używana w wersji 2 wartość decimal
        self.control = bytearray ( b'\x02\x01\x04\x03\x06\x05\x08\x07' )
        self.control_leght = len ( self.control )
        self.v_type_point_cloud = 1020
        self.v_type_targets = 1010
        self.v_type_target_index = 1011
        self.v_type_target_height = 1012
        self.v_type_presence_indication = 1021
        self.frame_dict = dict ()
        self.frame_header_wo_control_struct = '8I'
        self.frame_header_wo_control_length = struct.calcsize ( self.frame_header_wo_control_struct )
        self.tlv_dict = dict ()
        self.tlv_list = []
        self.tl_struct = '2I'
        self.tl_length = struct.calcsize ( self.tl_struct )
        self.pointcloud_unit_struct = '5f'
        self.pointcloud_unit_length = struct.calcsize ( self.pointcloud_unit_struct )
        self.point_struct = '2b3h'
        self.point_length = struct.calcsize ( self.point_struct )
        self.target_struct = 'I27f'
        self.target_part1_struct = 'I9f'
        self.target_part2_struct = '16f'
        self.target_part3_struct = '2f'
        self.target_length = struct.calcsize ( self.target_struct )
        self.target_part1_length = struct.calcsize ( self.target_part1_struct )
        self.target_part2_length = struct.calcsize ( self.target_part2_struct )
        self.target_part3_length = struct.calcsize ( self.target_part3_struct )
        self.target_height_struct = 'B2f'
        self.target_height_length = struct.calcsize ( self.target_height_struct )
        self.target_index_struct = 'B'
        self.target_index_length = struct.calcsize ( self.target_index_struct )
        self.presence_indication_struct = 'I'
        self.presence_indication_length = struct.calcsize ( self.presence_indication_struct )

    def get_target_index ( self ) :
        target_index_list = []
        number = int ( self.tlv_dict['tl']['v_length'] / self.target_index_length )
        for i in range ( number ) :
            try :
                target_id = struct.unpack ( self.target_index_struct , self.tlvs_bytes[(self.tl_length) + ( i * self.target_index_length ):][:self.target_index_length] )
                target_index_dict = { 'target_id' : target_id[0] }
            except struct.error as e :
                target_index_dict = { 'error' : e }
                logging.info ( f"get_target_index error {e} during frame number: {self.frame_dict['frame_header']['frame_number']}" )
            target_index_list.append ( target_index_dict )
        self.tlv_dict['target_indexes'] = target_index_list

    def get_target_height ( self ) :
        target_height_list = []
        number = int ( self.tlv_dict['tl']['v_length'] / self.target_height_length )
        for i in range ( number ) :
            try :
                target_id , max_z , min_z = struct.unpack ( self.target_height_struct , self.tlvs_bytes[(self.tl_length) + ( i * self.target_height_length ):][:self.target_height_length] )
                target_height_dict = { 'target_id' : target_id , 'max_z' : max_z , 'min_z' : min_z } 
            except struct.error as e :
                target_height_dict = { 'error' : e }
                logging.info ( f"get_target_height error {e} during frame number: {self.frame_dict['frame_header']['frame_number']}" )
            target_height_list.append ( target_height_dict )
        self.tlv_dict['target_heights'] = target_height_list

    def get_targets ( self ) :
        #  trzeba zastanowić sie i przerobić na listę dictionary
        target_list = []
        number = int ( self.tlv_dict['tl']['v_length'] / self.target_length )
        for i in range ( number ) :
            try :
                target_id , target_pos_x , target_pos_y , target_pos_z , target_vel_x , target_vel_y , target_vel_z , target_acc_x , target_acc_y , target_acc_z = struct.unpack ( self.target_part1_struct , self.tlvs_bytes[(self.tl_length) + ( i * self.target_length ):][:self.target_part1_length] )
                # Zostawiam err_covariance[16] na później
                err_covariance = struct.unpack ( self.target_part2_struct , self.tlvs_bytes[(self.tl_length) + ( i * self.target_length ) + self.target_part1_length:][:self.target_part2_length] )
                gain , confidence_level = struct.unpack ( self.target_part3_struct , self.tlvs_bytes[(self.tl_length) + ( i * self.target_length ) + self.target_part1_length + self.target_part2_length:][:self.target_part3_length] )
                # Zapisz target
                target_dict = { 'target_id' : target_id , 'target_pos_x' : target_pos_x , 'target_pos_y' : target_pos_y , 'target_pos_z' : target_pos_z , 'target_vel_x' : target_vel_x , 'target_vel_y' : target_vel_y , 'target_vel_z' : target_vel_z , 'target_acc_x' : target_acc_x , 'target_acc_y' : target_acc_y , 'target_acc_z' : target_acc_z , 'err_covariance' : err_covariance , 'gain' : gain , 'confidence_level' :  confidence_level}
            except struct.error as e :
                target_dict = { 'error' : e }
                logging.info ( f"get_targets error {e} during frame number: {self.frame_dict['frame_header']['frame_number']}" )
            target_list.append ( target_dict )
        self.tlv_dict['targets'] = target_list

    def get_points ( self ) :
        # UWAGAAAAAAAAAAAAAA! W ramce 840 wyjątkowo mało punktów wyszło, next header is wrong. Check if it could be reason.
        # przeanalizować przerobienie na listę dict
        point_list = [] # trzeba deklarować
        points_number = int ( ( self.tlv_dict['tl']['v_length'] - self.pointcloud_unit_length ) / self.point_length )
        for i in range ( points_number ) :
            try :
                # uwaga, żeby poniżej nie zdefiniować range jako zmiennej
                point_elevation , point_azimuth , point_doppler , point_range , point_snr = struct.unpack ( self.point_struct , self.tlvs_bytes[ ( self.tl_length + self.pointcloud_unit_length ) + ( i * self.point_length ):][:self.point_length] )
                point_dict = { 'elevation' : point_elevation , 'azimuth' : point_azimuth , 'doppler' : point_doppler , 'range' : point_range , 'snr' : point_snr }
            except struct.error as e :
                point_dict = { 'error' : e }
                logging.info ( f"get_points unpack error {e} during frame number: {self.frame_dict['frame_header']['frame_number']}" )
            point_list.append ( point_dict )
        self.tlv_dict['points'] = point_list

    def get_pointcloud_unit ( self ) :
        try :
            elevation_unit , azimuth_unit , doppler_unit , range_unit , snr_unit = struct.unpack ( self.pointcloud_unit_struct , self.tlvs_bytes[self.tl_length:][:self.pointcloud_unit_length] )
            pointcloud_unit_dict = { 'elevation_unit' : elevation_unit , 'azimuth_unit' : azimuth_unit , 'doppler_unit' : doppler_unit , 'range_unit' : range_unit , 'snr_unit' : snr_unit }
        except struct.error as e :
            pointcloud_unit_dict = { 'error' : e }
            logging.info ( f"get_pointcloud_unit unpack error {e} during frame number: {self.frame_dict['frame_header']['frame_number']}" )
        self.tlv_dict['units'] = pointcloud_unit_dict

    def get_presence_indication ( self ) :
        try :
            presence_indication = struct.unpack ( self.presence_indication_struct , self.tlvs_bytes[self.tl_length:][:self.presence_indication_length] )
            presence_indication_dict = { 'presence_indication' : presence_indication[0] } # Dlaczego otrzymuję tuple, a nie int32bit
            #if presence_indication[0] != 0 :
            #    pprint.pprint ( self.frame_dict['frame_header']['frame_number'] )
        except struct.error as e :
            presence_indication_dict = { 'error' : e }
            logging.info ( f"get_presence_indication unpack error {e} during frame number: {self.frame_dict['frame_header']['frame_number']}" )
        self.tlv_dict['presence'] = presence_indication_dict

    def get_tl ( self ) :
        try:
            v_type, v_length = struct.unpack ( self.tl_struct , self.tlvs_bytes[:self.tl_length] )
            tl_dict = { 'v_type' : v_type , 'v_length' : v_length }
            logging.info ( f"Got tlv v_type: {v_type}" )
        except struct.error as e :
            tl_dict = { 'error' : e }
            logging.info ( f"TL unpack error {e} during frame number: {self.frame_dict['frame_header']['frame_number']}" )
        self.tlv_dict['tl'] = tl_dict

    def get_tlv ( self ) :
        self.get_tl ()
        if not self.tlv_dict['tl'].get ( 'error' ) :
            #xl = len (self.tlvs_bytes) # do usunięcia
            #print ( xl ) # do usunięcia
            if self.tlv_dict['tl'].get ( 'v_type' ) == self.v_type_point_cloud :
                self.get_pointcloud_unit ()
                if not self.tlv_dict['units'].get ( 'error' ) :
                    self.get_points ()
                    self.tlv_list.append ( self.tlv_dict.copy() )
            elif self.tlv_dict['tl'].get ( 'v_type' ) == self.v_type_targets :
                    self.get_targets ()
                    self.tlv_list.append ( self.tlv_dict.copy() )
            elif self.tlv_dict['tl'].get ( 'v_type' ) == self.v_type_target_index :
                    self.get_target_index ()
                    self.tlv_list.append ( self.tlv_dict.copy() )
            elif self.tlv_dict['tl'].get ( 'v_type' ) == self.v_type_target_height :
                    self.get_target_height ()
                    self.tlv_list.append ( self.tlv_dict.copy() )
            elif self.tlv_dict['tl'].get ( 'v_type' ) == self.v_type_presence_indication :
                    self.get_presence_indication ()
                    self.tlv_list.append ( self.tlv_dict.copy() ) # muszę kopiować, bo inaczej po skasowaniu źródła tracę dane
            else :
                logging.info ( f"Error in match get_tlv in frame nr: {self.frame_dict['frame_header']['frame_number']}" )
                self.tlv_dict['tl'] = { 'error' : "v_type not matched" }
                self.tlv_list.append ( self.tlv_dict.copy() )
                return False
            # Tutaj usuwam cały TLV. Usuwam dł. header i dł. payload, bo sprawdziłem w debug, że v_length nie obejmuje tlv_header
            #xl = len (self.tlvs_bytes) # do usunięcia
            self.tlvs_bytes = self.tlvs_bytes[self.tlv_dict['tl']['v_length']:]
            #xl = len (self.tlvs_bytes) # do usunięcia
            self.tlv_dict.clear ()
            return True
        else :
            logging.info ( f"Error in get_tlv() in frame nr: {self.frame_dict['frame_header']['frame_number']}" )
            return False

    # Rozpakuj po kolei każdy z TLV
    def get_tlvs ( self ) :
        i = self.frame_dict['frame_header']['number_of_tlvs']
        while i > 0 : # self.frame_header_dict['num_tlvs'] exists for sure and I don't need get function.
            if not self.get_tlv () :
                break
            i= i - 1
        self.frame_dict['tlvs'] = self.tlv_list
            
    def tlvs2json ( self ) :
        l = len ( self.tlv_list )
        self.tlvs_json = "'tlvs':["
        for i in range ( l ) :
            self.tlvs_json = self.tlvs_json + str ( self.tlv_list[i] )
            if i < ( l - 1 ) :
                self.tlvs_json = self.tlvs_json + ","
        self.tlvs_json = self.tlvs_json + "]"
        self.tlv_list.clear ()

    def get_frame_header ( self ) :
        frame_header_dict = dict ()
        control_error = 0
        self.data_com.reset_input_buffer ()
        self.data_com.reset_output_buffer ()
        control = self.data_com.read ( self.control_leght )
        while ( control != self.control ) : # nidgy w testach nie okazało się potrzebne to skomplikowane co jest poniżej. Może wystaczyłby jedynie return False
            control_error += 1 # do usunięcie i ew. zamiany na logging
            if ( control_error == 10000 ) : # jw.
                logging.info ( f"Control error." ) # jw.
                return False
            index_b2 = control.find ( self.control[0] ) # sprawdź czy w śrdoku nie ma bajtu będącego początkiem control, jeśli był to spróbuj czy nie jest to początek control 
            if index_b2 == -1 :
                control = self.data_com.read ( self.control_leght )
            else :
                control = control[index_b2:]
                control = control + self.data_com.read ( self.control_leght - self.control_leght )
        try :
            frame_header = self.data_com.read ( self.frame_header_wo_control_length )
            version , total_packet_length , platform , frame_number , time , number_of_points , number_of_tlvs , subframe_number = struct.unpack ( self.frame_header_wo_control_struct , frame_header[:self.frame_header_wo_control_length] )
            frame_header_dict = { 'frame_number' : frame_number , 'number_of_tlvs' : number_of_tlvs , 'number_of_points' : number_of_points , 'subframe_number' : subframe_number , 'version' : version , 'total_packet_length' : total_packet_length , 'platform' : platform , 'time' : time }
            logging.info ( f"Got frame number: {frame_number}" )
            self.tlvs_bytes = self.data_com.read ( total_packet_length - ( self.control_leght + self.frame_header_wo_control_length ) ) # do usunięcia
        except struct.error as e :
            frame_header_dict = { 'error' : e }
            logging.info ( f"Frame header unpack error: {e} during frame unpack number: {frame_header_dict}" )
        self.frame_dict['frame_header'] = frame_header_dict
        if frame_header_dict.get ( 'error' ) :
            return False
        else :
            return True
