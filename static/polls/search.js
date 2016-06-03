$(document).ready(function() {
  $("#index-search button").click(function () {
    var query = $("#id_query").val();
    $('.search-result').load(
      "polls/search/?ajax&query=" + encodeURIComponent(query));
      return false;
  });
});
