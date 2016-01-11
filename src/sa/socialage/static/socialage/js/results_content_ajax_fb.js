$(document).ready(function () {
    $.ajax({
        url: "../fb_results/",
        success: function (result) {
            $("#content").html(result);
            $("document").title = 'results';
        }
    });
});