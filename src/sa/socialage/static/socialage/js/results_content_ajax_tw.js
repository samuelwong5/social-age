$(document).ready(function () {
    $.ajax({
        url: "../tw_results/",
        success: function (result) {
            window.location.href = "../resultpage/";
            $("document").title = 'results';
        }
    });
});