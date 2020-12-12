// validation example for Login form
$("#btnLogin").click(function(event) {
    
    var form = $("#loginForm");
    
    if (form[0].checkValidity() === false) {
      event.preventDefault();
      event.stopPropagation();
    }
    
    // if validation passed form
    // would post to the server here
    
    form.addClass('was-validated');
});

var resetchecker = document.getElementById('resetPasswd')
var submitpasswordbtn = document.getElementById('submitresetbtn')
resetchecker.onchange = function() {
  submitresetbtn.disabled = !this.checked;
}

function verify_both() {
  var passwd = document.getElementById("passwd");
  var passwd_validation = document.getElementById("passwd_validation");
  var submitpasswdbtn = document.getElementById("submitpasswdbtn");

  if (passwd.value != '' && passwd_validation.value != '') {
    submitpasswdbtn.disabled = false;
  } else {
    submitpasswdbtn.disabled = true;
  }
}