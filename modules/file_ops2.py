def write_2_local_file ( file_name , s ) :
    with open ( file_name , 'a' , encoding='utf-8' ) as f :
        f.write ( s )