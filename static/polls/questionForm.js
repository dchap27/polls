$(document).ready(function() {
  $('.hide-choices').hide();
  $('p.show-button').click(function() {
    $('.hide-choices').show();
    $(this).hide();
  });
  //$('#eligibility').hide();
  $('#check-eligible input').click(function(event){
    $('#eligibility').toggleClass('hidden');
    });
});
