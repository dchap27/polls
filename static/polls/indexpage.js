$(document).ready(function() {
    $('.recent-polls').load("/polls/recent");

    $('#suggested .suggested-polls').load('/polls/suggest_polls/');
    $('#suggested .suggest-button').click(function(){
      $('#suggested .suggested-polls').load('/polls/suggest_polls/');
      return false;
    });

    $('#suggested .suggested-people').load('/polls/people_suggest/');
    $('#suggested .people-button').click(function(){
      $('#suggested .suggested-people').load('/polls/people_suggest/');
      return false;
    });

});

$(document).ready(function() {
  var page = 1;
  var empty_page = false;
  var block_request = false;

  $(window).scroll(function() {
    var margin = $(document).height() - $(window).height() - 200;
    if ($(window).scrollTop() > margin && empty_page == false &&
  block_request == false) {
    block_request = true;
    page += 1;
    $.get('?page=' + page, function(data) {
      if(data == '') {
        empty_page = true;
      }
      else {
        block_request = false;
        $('#action-list').append(data);
      }
    });
  }
});
});
