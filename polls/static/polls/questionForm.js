$(document).ready(function() {
  $('.hide-choices').hide();
  $('p.show-button').click(function() {
    $('.hide-choices').show();
    $(this).hide();
  });
});
