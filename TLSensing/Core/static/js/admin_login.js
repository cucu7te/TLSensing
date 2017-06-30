var logged_session="false";

function isLogged() {
 var my_session = JSON.parse(localStorage.getItem('saved_logged_session'));
 var my_session_string=String(my_session) 
 if (my_session_string.localeCompare("true")==0)
	{ 
	 return true;
	}
 else 
	{
	 return false;
	}
};

function showLoginForm() {
    	 document.getElementById("wrongpwd").style.display="none";
         document.getElementById("admin label").style.display="none";	  
         document.getElementById("img box").style.display="block";
	 document.getElementById("login button").style.display="block";
         document.getElementById("password_field").style.display="block";
         document.getElementById("login img").style.display="block";
         document.getElementById("login info").style.display="block";
	 document.getElementById("password_field").value="";
	 document.getElementById("old_password_field").value="";
	 document.getElementById("new_password_field_1").value="";
	 document.getElementById("new_password_field_2").value="";
	 document.getElementById("change_password_link").style.display="block";
	 document.getElementById("old_password_label").style.display="none";
	 document.getElementById("old_password_field").style.display="none";
	 document.getElementById("new_password_label_1").style.display="none";
	 document.getElementById("new_password_field_1").style.display="none";
	 document.getElementById("new_password_label_2").style.display="none";
	 document.getElementById("new_password_field_2").style.display="none";
         document.getElementById("change_password_button").style.display="none";
	 document.getElementById("error").style.display="none";
};

function logout(){
         logged_session="false";
 	 localStorage.setItem('saved_logged_session', logged_session);
	 invalidateCookie("username");
	 document.getElementById("welcome_msg").style.display="none";
	 window.location.reload(true);
};

function showChPwdForm() {
	document.getElementById("admin label").style.display="block"; 		 document.getElementById("wrongpwd").style.display="none";
	document.getElementById("img box").style.display="none";	  
	document.getElementById("login button").style.display="none";
        document.getElementById("password_field").style.display="none";
        document.getElementById("login img").style.display="none";
        document.getElementById("login info").style.display="none";
	document.getElementById("change_password_link").style.display="none";
	document.getElementById("old_password_label").style.display="block";
	document.getElementById("old_password_field").style.display="block";
	document.getElementById("new_password_label_1").style.display="block";
	document.getElementById("new_password_field_1").style.display="block";
	document.getElementById("new_password_label_2").style.display="block";
	document.getElementById("new_password_field_2").style.display="block";
	document.getElementById("change_password_button").style.display="block";

};




function admin_in(){
    	document.getElementById("wrongpwd").style.display="none";
	logged_session="true";
	localStorage.setItem("saved_logged_session", JSON.stringify(logged_session));
	var user = prompt("Please enter your name:", "");
        if (user != "" && user != null) {
            setCookie("username", user, 20); //set session's maximum duration to 20 minutes
        }
	window.location.reload(true);
 
};

function logIn(){
  var my_url="/admn/log/"+$("#password_field").val();
  $.ajax({
    type: "GET",
    url: my_url
  }).done(function(data) {
     admin_in();
  }).fail(function(data) {
    	document.getElementById("wrongpwd").style.display="block";
	document.getElementById("password_field").value="";
  });
};

function ch_pwd(){
  var my_url="/admn/chpwd/oldpwd/"+$("#old_password_field").val();
  $.ajax({
    type: "GET",
    url: my_url
  }).done(function(data) {
      if (match_pwd()==true){
	document.getElementById("error").style.display="none";
        save_new_pwd($("#new_password_field_1").val());
      }
      else {match_error(); }
  }).fail(function(data){
 	document.getElementById("error").style.display="block";
	document.getElementById("error").innerHTML="ERROR:</br>The old password is not correct. Try again. ";
 	document.getElementById("old_password_field").value="";
	document.getElementById("new_password_field_1").value="";
	document.getElementById("new_password_field_2").value="";
  });

};
 
function save_new_pwd(new_pwd){
 var my_url="/admn/chpwd/newpwd/"+new_pwd;
  $.ajax({
    type: "GET",
    url: my_url
  }).done(function(status) {
      successful_change();
  }).fail(function(data){
	document.getElementById("error").style.display="block";
	document.getElementById("error").innerHTML="ERROR:</br>All the fields must be filled in. ";
    
  });
};
 
function match_pwd(){
	var p1= $("#new_password_field_1").val();
	var p2= $("#new_password_field_2").val();
	if (p1.localeCompare(p2)==0) 
		{
		 return true;
		} 
	else 
		{
		 return false;
		}
};


function match_error(){
 document.getElementById("error").innerHTML="ERROR:</br>No match between the entered passwords.";
 document.getElementById("error").style.display="block";
 document.getElementById("new_password_field_1").value="";
 document.getElementById("new_password_field_2").value="";

};
 
function successful_change(){
  alert("Administrator's password successfully changed."); 
  $('#autenticazione').modal('toggle');
  admin_in();
};


function setCookie(cname, cvalue, exminutes) {
    var d = new Date();
    d.setTime(d.getTime() + (exminutes * 60 * 1000));
    var expires = "expires="+d.toUTCString();
    document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
};

function invalidateCookie(cname) {
    var user = getCookie("username");
    document.cookie = cname + "=" + user + ";expires=Thu, 01 Jan 1970 00:00:01 GMT;path=/";
};


function getCookie(cname) {
    var name = cname + "=";
    var ca = document.cookie.split(';');
    for(var i = 0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
            return c.substring(name.length, c.length);
        }
    }
    return "";
};

function checkCookie() {
    var user = getCookie("username");
    if (user != "") {
	document.getElementById("welcome_msg").innerHTML="<a><font color='428bca'>Welcome again " + user + "!</font></a>";
	document.getElementById("welcome_msg").style.display="block";
    } else {
	var my_session = JSON.parse(localStorage.getItem('saved_logged_session'));
 	var my_sess_string=String(my_session);
 	if (my_sess_string.localeCompare("true")==0){ logout();}        
    }
};

function modify(){
if(isLogged()==true){
  $("#set_thresh").style.display="block";
}
else{
  $("#set_thresh").style.display="none";}
};

function guard_admin(){
 if(isLogged()==false){
   alert("You are not logged in. Please login to TLSensing before access this page.");
   window.location=document.getElementById("back_btn").href;
 }
};



