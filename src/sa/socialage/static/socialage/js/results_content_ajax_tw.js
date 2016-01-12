$(document).ready(function () {
    $.ajax({
        url: "../tw_results/",
        success: function (result) {
            $("#content").html(result);
            $("document").title = 'results';
        }
    });
});