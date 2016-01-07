$(document).ready(function () {
    $.ajax({
        url: "../fb_results/",
        success: function (result) {
            $("body").html(result);
            $("document").title = 'Results';
        }
    });
});