$(document).ready(function() {

$(document).delegate('.vote','click',
    function () {
      var options = $(this).attr('id').split('-');
      var target = options[0];
      var id = options [2];
      var direction = options[3];
      if ( ( $(this).hasClass('up-voted') && direction == 'up') || ($(this).hasClass('down-voted') && direction == 'down') ){
        direction= 'clear';
      }
      $.post('/' + target + '/' + id + '/' + direction + 'vote/', {HTTP_X_REQUESTED: 'XMLHttpRequest'},
        function(data){
          if (data.success == true) {
            var $box = $('#' + target + '-votebox-' + id );
            var positive = ( data.score.score +  data.score.num_votes )/ 2 ;   
            var negative = ( data.score.num_votes - data.score.score )/ 2 ;
            $box.find('.okscore').text(positive);
            $box.find('.koscore').text(negative);   
            if (direction == 'up') {
              $box.find('#'+ target +'-vote-' + id + '-' + 'up').toggleClass('up-voted');
              $box.find('#'+ target +'-vote-' + id + '-' + 'down').removeClass('down-voted');
            }
            if (direction == 'down') {
              $box.find('#'+ target +'-vote-' + id + '-' + 'up').removeClass('up-voted');
              $box.find('#'+ target +'-vote-' + id + '-' + 'down').toggleClass('down-voted');            
            }
            if (direction == 'clear') {
              $box.find('#'+ target +'-vote-' + id + '-' + 'up').removeClass('up-voted');
              $box.find('#'+ target +'-vote-' + id + '-' + 'down').removeClass('down-voted');            
            }
          }else{
		        alert('ERROR: ' + data.error_message);
	        }
        }, 'json');
      return false;
});

});