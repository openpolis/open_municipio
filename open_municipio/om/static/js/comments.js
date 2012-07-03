// Empty comments are not allowed!
$(document).ready(function() {
    $('#comment-form').submit(function() {
	if ($(this).find('textarea[name="comment"]').val().length == 0 ) {
            alert('Attenzione, il commento è vuoto.');
            return false;
        }
    });
});
