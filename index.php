<?php 
//bochron backend

//Session
error_reporting(E_ERROR | E_WARNING | E_PARSE);
session_name('s');
ini_set('session.use_trans_sid', True);
ini_set('session.use_cookies', False);
ini_set('session.use_only_cookies', False);
ini_set('session.gc_maxlifetime', 64800);


session_start(); 

//Header
header( 'content-type: application/json; charset=utf-8' ); 


//MySql Settings
$v_mysql_user = 'username';
$v_mysql_password = 'password';
$v_mysql_host = 'localhost';
$v_mysql_table = 'tablename';

//MySql Connect
$mysql = mysql_connect("$v_mysql_host", "$v_mysql_user", "$v_mysql_password");
mysql_select_db("$v_mysql_table");

//Backend Start
if (isset($_GET["b"])) {
$b = $_GET["b"];
}else{
$b = "";	
}

//Login
if($b == "get_user"){
    
    $query = "SELECT bname FROM bo_benutzer WHERE disabled = 0";
    $res = mysql_query($query);

    // iterate over every row
    while ($row = mysql_fetch_assoc($res)) {
        // for every field in the result..
        for ($i=0; $i < mysql_num_fields($res); $i++) {
            $info = mysql_fetch_field($res, $i);
            $type = $info->type;

            // cast for real
            if ($type == 'real')
                $row[$info->name] = doubleval($row[$info->name]);
            // cast for int
            if ($type == 'int')
                $row[$info->name] = intval($row[$info->name]);
        }

        $rows[] = $row;
        
    }
	mysql_free_result($res);
    // JSON-ify all rows together as one big array
    #echo "{\"test\":".json_encode($rows)."}";
	echo json_encode($rows);

}elseif($b == "auth_user"){
	$user = $_GET["user"];
	$password = $_GET["password"];
	$password = crypt($password, CRYPT_DES_EXT);
	
	
	    
	$res =  mysql_query( "SELECT * FROM bo_benutzer WHERE bname = '$user' ");
	while  ($row  =  mysql_fetch_row($res))
	{
		$v_user_id = $row[0];
		$v_pass = $row[15];
		if($v_pass == $password){
		$_SESSION['user_id'] = $v_user_id;	
		$_SESSION['user'] = $user;
		$_SESSION['login_status'] = '1';	
		}
	
	}
	mysql_free_result($res);
	
	if(!isset($_SESSION['user']))
	{
	echo "[{\"login_status\":\"0\"}]";	
		}else{
	$v_session_id = session_id();	
	$v_login_status = $_SESSION['login_status'];
	
	echo "[{\"login_status\":\"$v_login_status\", \"session_id\":\"$v_session_id\"}]";
	}


}elseif($b == "login_status"){


	if(!isset($_SESSION['user']))
	{
	echo "[{\"login_status\":\"0\"}]";
	exit;
	}   
	echo "[{\"login_status\":\"1\"}]";


	
}elseif($b == "logout"){
$_SESSION = array();	
session_destroy();
echo "[{\"login_status\":\"0\", \"session_id\":\"$v_session_id\"}]";


}elseif($b == "add_recorder"){ 
	if(!isset($_SESSION['user']))
   {
   echo "[{\"login_status\":0}]";
   exit;
   }
   
	$v_rec_art = 1;
	$v_rec_color = $_GET["color"];
	$v_rec_user_id = $_SESSION['user_id'];
	$v_rec_user = $_SESSION['user'];
	$v_rec_title = $_GET["title"];
	$v_rec_description = $_GET["description"];
	
	mysql_query("insert  into  bochron_recorder (art, color, user_id, user, customer_id, customer, project_id, project, task_id, task, title, description) values 
	('$v_rec_art', '$v_rec_color', '$v_rec_user_id', '$v_rec_user', '$v_rec_customer_id', '$v_rec_customer', '$v_rec_project_id', '$v_rec_project', '$v_rec_task_id', '$v_rec_task', '$v_rec_title', '$v_rec_description' )");

	$last_id = mysql_insert_id();
	echo "[{\"id\":$last_id, \"login_status\":1}]";
	

}elseif($b == "get_recorder"){ 
	if(!isset($_SESSION['user']))
   {
   echo "[{\"login_status\":0}]";
   exit;
   }
   
	$user_id = $_SESSION['user_id'];
	$user_name = $_SESSION['user'];
	
	//Check for open records and close
	$v_mysql_recorder =  mysql_query( "SELECT * FROM bochron_time_record WHERE user_id = '$user_id' AND stop_time = '0000-00-00 00:00:00' ");
	while  ($row  =  mysql_fetch_row($v_mysql_recorder))
		{
		$v_id = $row[0];
		$v_art = $row[1];
		$v_recorder_id = $row[2];
		$v_recorder = $row[3];	
		$v_start_time = $row[12];
		$v_stop_time = date("Y-m-d H:i:s");
		}
	
   
    $query = "SELECT * FROM bochron_recorder WHERE user_id = '$user_id'";
    $res = mysql_query($query);

    // iterate over every row
    while ($row = mysql_fetch_assoc($res)) {
        // for every field in the result..
        for ($i=0; $i < mysql_num_fields($res); $i++) {
            $info = mysql_fetch_field($res, $i);
            $type = $info->type;

            // cast for real
            if ($type == 'real')
                $row[$info->name] = doubleval($row[$info->name]);
            // cast for int
            if ($type == 'int')
                $row[$info->name] = intval($row[$info->name]);
        }
		
		if($row['id'] == $v_recorder_id ){
			$row['open_rec'] = 1;
			$row['start_time'] = "$v_start_time";
		}else{
			$row['open_rec'] = 0;
			$row['start_time'] = "";
		}
        
        $rows[] = $row;
        
    }
	mysql_free_result($res);
    // JSON-ify all rows together as one big array
    #echo "{\"test\":".json_encode($rows)."}";
    
    
	echo json_encode($rows);  

}elseif($b == "get_history"){ 
	if(!isset($_SESSION['user']))
   {
   echo "[{\"login_status\":0}]";
   exit;
   }
   
	$user_id = $_SESSION['user_id'];
	$user_name = $_SESSION['user'];
	
	
	$v_mysql_recorder =  mysql_query( "SELECT * FROM bochron_recorder");
	while  ($row  =  mysql_fetch_row($v_mysql_recorder))
		{
		$v_id = $row[0];
		$v_color = $row[2];
		$colors[$v_id] = $v_color;
		}
	
    $v_akt_datum = date('Y-m-d'); 
    
    $query = "SELECT * FROM bochron_time_record WHERE user_id = '$user_id' ORDER by id DESC LIMIT 20";
    $res = mysql_query($query);

    // iterate over every row
    while ($row = mysql_fetch_assoc($res)) {
        // for every field in the result..
        for ($i=0; $i < mysql_num_fields($res); $i++) {
            $info = mysql_fetch_field($res, $i);
            $type = $info->type;

            // cast for real
            if ($type == 'real')
                $row[$info->name] = doubleval($row[$info->name]);
            // cast for int
            if ($type == 'int')
                $row[$info->name] = intval($row[$info->name]);
                
       
                
        }
        
        
        if(date('Y-m-d', strtotime($row['start_time'])) == $v_last_start_time){
			$v_last_minutes = $v_last_minutes + $row['minutes'];
			$row['show_day_minutes'] = 0;
		}else{
			if($v_last_start_time == ""){
			$row['show_day_minutes'] = 0;
			}else{
			$row['show_day_minutes'] = 1;
			$curr_date= date('D. Y-m-d', strtotime($v_last_start_time));
			$row['last_time'] = "$curr_date - $last_hours h $last_minutes m";
			}
			$v_last_minutes = $row['minutes'];
		
		}
		
		$v_last_start_time = date('Y-m-d', strtotime($row['start_time']));
        
        
        $last_hours  = floor($v_last_minutes/60); //round down to nearest minute. 
		$last_minutes = $v_last_minutes % 60; 
        
        
        $hours  = floor($row['minutes']/60); //round down to nearest minute. 
		$minutes = $row['minutes'] % 60; 
		
				
		$row['time'] = "$hours Std. $minutes Min. ($last_hours h $last_minutes m)";    
        
        
		$row['color'] = $colors[$row['recorder_id']];
		$row['login_status'] = 1;
        $rows[] = $row;
        
    }
	mysql_free_result($res);
    // JSON-ify all rows together as one big array
    #echo "{\"test\":".json_encode($rows)."}";
    
    
	echo json_encode($rows);  

}elseif($b == "get_history_record"){ 
	if(!isset($_SESSION['user']))
   {
   echo "[{\"login_status\":0}]";
   exit;
   }
   
	$user_id = $_SESSION['user_id'];
	$user_name = $_SESSION['user'];
	$record_id = $_GET["record_id"];
	
	$v_mysql_recorder =  mysql_query( "SELECT * FROM bochron_recorder");
	while  ($row  =  mysql_fetch_row($v_mysql_recorder))
		{
		$v_id = $row[0];
		$v_color = $row[2];
		$colors[$v_id] = $v_color;
		}
	
   
    $query = "SELECT * FROM bochron_time_record WHERE id = '$record_id'";
    $res = mysql_query($query);

    // iterate over every row
    while ($row = mysql_fetch_assoc($res)) {
        // for every field in the result..
        for ($i=0; $i < mysql_num_fields($res); $i++) {
            $info = mysql_fetch_field($res, $i);
            $type = $info->type;

            // cast for real
            if ($type == 'real')
                $row[$info->name] = doubleval($row[$info->name]);
            // cast for int
            if ($type == 'int')
                $row[$info->name] = intval($row[$info->name]);
                
       
                
        }
        
        
        $hours  = floor($row['minutes']/60); //round down to nearest minute. 
		$minutes = $row['minutes'] % 60; 
		
		$row['time'] = "$hours Std. $minutes Min.";    
        
		$row['color'] = $colors[$row['recorder_id']];
		$row['login_status'] = 1;
        $rows[] = $row;
        
    }
	mysql_free_result($res);
    // JSON-ify all rows together as one big array
    #echo "{\"test\":".json_encode($rows)."}";
    
    
	echo json_encode($rows);  

}elseif($b == "update_history_record"){ 
	
	if(!isset($_SESSION['user']))
	{
	echo "[{\"login_status\":0}]";
	exit;
	}
	echo "[{\"login_status\":1}]";
	
	$v_record_id = $_GET["record_id"];
	$v_start_time = $_GET["start_time"];
	$v_stop_time = $_GET["stop_time"];
	$v_note = $_GET["note"];
	
	$user_id = $_SESSION['user_id'];
	$user_name = $_SESSION['user'];
	
	$date1 = new DateTime($v_start_time);
	$date2 = new DateTime($v_stop_time);
	$v_interval = $date1->diff($date2);
	
	$minutes = $v_interval->days * 24 * 60;
	$minutes += $v_interval->h * 60;
	$minutes += $v_interval->i;
	
	$v_elapsed_time = $minutes;
	
	$abfrage = "UPDATE
		bochron_time_record SET
		bochron_time_record.start_time='$v_start_time',
		bochron_time_record.stop_time='$v_stop_time',
		bochron_time_record.minutes='$v_elapsed_time',
		bochron_time_record.note='$v_note'
		WHERE
		bochron_time_record.id='$v_record_id'";
	$ergebnis = mysql_query($abfrage);
	


}elseif($b == "rec_start_stop"){ 
	
	if(!isset($_SESSION['user']))
	{
	echo "[{\"login_status\":0}]";
	exit;
	}
	echo "[{\"login_status\":1}]";
	$recorder_id = $_GET["recorder_id"];
	$user_id = $_SESSION['user_id'];
	$user_name = $_SESSION['user'];

//Check for open records and close
	$v_mysql_recorder =  mysql_query( "SELECT * FROM bochron_time_record WHERE user_id = '$user_id' AND stop_time = '0000-00-00 00:00:00' ");
	while  ($row  =  mysql_fetch_row($v_mysql_recorder))
	{
	$v_id = $row[0];
	$v_art = $row[1];
	$v_recorder_id = $row[2];
	$v_recorder = $row[3];	
	$v_start_time = $row[12];
	$v_stop_time = date("Y-m-d H:i:s");
	
	
	$date1 = new DateTime($v_start_time);
	$date2 = new DateTime($v_stop_time);
	$v_interval = $date1->diff($date2);
	
	$minutes = $v_interval->days * 24 * 60;
	$minutes += $v_interval->h * 60;
	$minutes += $v_interval->i;
	
	$v_elapsed_time = $minutes;
	
	//echo"$v_id, $v_recorder_id, $v_recorder, $v_start_time - $v_stop_time = $v_elapsed_time \n";
	
	$abfrage = "UPDATE
		bochron_time_record SET
		bochron_time_record.stop_time='$v_stop_time',
		bochron_time_record.minutes='$v_elapsed_time'
		WHERE
		bochron_time_record.id='$v_id'";
	$ergebnis = mysql_query($abfrage);
	
	}
	
	if($v_recorder_id == $recorder_id){
//Only close		
	}else{
	
//Add new Record
	$v_mysql_recorder =  mysql_query( "SELECT * FROM bochron_recorder WHERE id = '$recorder_id' ");
	while  ($row  =  mysql_fetch_row($v_mysql_recorder))
	{
	$v_id = $row[0];
	$v_art = $row[1];
	$v_color = $row[2];
	$v_user_id = $row[3];
	$v_user = $row[4];
	$v_customer_id = $row[5];
	$v_customer = $row[6];
	$v_project_id = $row[7];
	$v_project = $row[8];
	$v_task_id = $row[9];
	$v_task = $row[10];
	$v_title = $row[11];
	$v_description = $row[12];
	}	

	
				
	$v_rec_art = $v_art;
	$v_rec_recorder_id = $recorder_id;
	$v_rec_recorder = $v_title;
	$v_rec_user_id = $user_id;
	$v_rec_user = $user_name;
	$v_rec_customer_id = $v_customer_id;
	$v_rec_customer = $v_customer;
	$v_rec_project_id = $v_project_id;
	$v_rec_project = $v_project;
	$v_rec_task_id = $v_task_id;
	$v_rec_task = $v_task;
	$v_rec_start_time = date("Y-m-d H:i:s");
	$v_rec_stop_time = '';
	$v_rec_minutes = '';
	$v_rec_note = $v_description;
				

	mysql_query("insert  into  bochron_time_record (art, recorder_id, recorder, user_id, user, customer_id, customer, project_id, project, task_id, task, start_time, stop_time, minutes, note) values 
	('$v_rec_art', '$v_rec_recorder_id', '$v_rec_recorder', '$v_rec_user_id', '$v_rec_user', '$v_rec_customer_id', '$v_rec_customer', '$v_rec_project_id', '$v_rec_project', '$v_rec_task_id', '$v_rec_task', '$v_rec_start_time', '$v_rec_stop_time', '$v_rec_minutes', '$v_rec_note')");

		
	}	

}elseif($b == "test"){
	if(!isset($_SESSION['user']))
   {
   echo "[{\"login_status\":\"False\"}]";
   exit;
   }   
   echo"signed in";
   
}
   

//MySql Close
mysql_close($mysql);  
?>

