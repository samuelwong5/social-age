$(document).ready(function () {
    alert("Your result is being calculated at the moment. Please wait for around 30s.");
    $.ajax({
        url: "../tw_results/",
        success: function (result) {
            $("#content").html(result);
            $("document").title = 'results';
        }
    });
});