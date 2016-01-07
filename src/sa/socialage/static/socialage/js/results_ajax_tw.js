$( document ).ready(function(){
    $.ajax({url: "../tw_results/",
        success: function(result){
        $("body").html(result);
    }});
});