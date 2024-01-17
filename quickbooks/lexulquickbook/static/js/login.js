$(document).ready(function(){
    $('#login').click(function(e){

        $.post(API_URL+'login/',{'csrfmiddlewaretoken':$('input[name="csrfmiddlewaretoken"]').val(),'username': $('#username').val(), 'password': $('#password').val()}, function(username){
            if(username == "error")
                alert("The username or password is wrong.");
            else{
                localStorage.setItem("username", username);
                location.href = "/";
            }
            
        });
    });
});