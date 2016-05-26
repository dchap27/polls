$(document).ready(function() {

  var username = $('small.username').text();
  $('.col-sm-4 .recent-polls').click(function() {
    event.preventDefault();
    $('div#userpage-rightcol').load("/polls/recent #recent");
  });

  $('.col-sm-4 .votes').click(function() {
    event.preventDefault();
    $('div#userpage-rightcol').load("/polls/" + encodeURIComponent(username) + "/voted/");
  });

  $('.col-sm-4 .comments').click(function() {
    event.preventDefault();
    $('div#userpage-rightcol').load("/polls/" + encodeURIComponent(username) + "/commented/");
  });

  $('.col-sm-4 .following').click(function() {
    event.preventDefault();
    $('div#userpage-rightcol').load("/polls/friends/" + encodeURIComponent(username));
  });

});
