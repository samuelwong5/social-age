$( document ).ready(function(){
    $.ajax({url: "./results/",
        success: function(result){
        $("body").html(result);
    }});
});