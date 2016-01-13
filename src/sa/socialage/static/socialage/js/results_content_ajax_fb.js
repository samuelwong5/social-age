$(document).ready(function () {
    $.ajax({
        url: "../fb_results/",
        success: function (result) {
            window.location.href = "../resultpage";
            $("document").title = 'results';
        }
    });
});