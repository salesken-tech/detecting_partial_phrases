//$("#my_form").submit(function(event){
//    event.preventDefault();
//    var post_url = $(this).attr("action")
//    var request_method = $(this).attr("method");
//    var form_data = $(this).serialize();
//    $.ajax({
//        url : post_url,
//        type : request_method,
//        data : form_data
//    }).done(function(response){
//        $("#server-results").html(response);
//    });
//});

$(function(){
    $(".error").hide();
    $("#result_table").hide();
    $("#get_matches").click(function(){
        $('.error').hide();
        $("#result_table").hide();
        $(".table tbody").empty();
        var signal= $("input#signal").val();
        if (signal == ''){
            $('label#signal_error').show();
            $("input#signal").focus();
            return false;
        }
        var snippet = $("input#snippet").val();
        if (snippet == ''){
            $('label#snippet_error').show();
            $("input#snippet").focus();
            return false;
        }

        var threshold = $('input#threshold').val();
        if (threshold == ''){
            $('label#threshold_error').show();
            $("input#threshold").focus();
            return false;
        }

        var data_string = "signal="+signal+"&snippet="+snippet+'&threshold='+threshold;
//        alert(data_string);return false;
        $.ajax({
            type : "POST",
            url : "http://localhost:9999/match_playground",
            data : data_string,
            success : function(response,status) {
                markup="";
                for (i = 0; i < response.length; i++){
                markup+="<tr>\n"+
                        "<td>"+response[i].tag+"</td>\n"+
                        "<td>"+response[i].signal+"</td>\n"+
                        "<td>"+response[i].snippet+"</td>\n"+
                        "<td>"+response[i].score+"</td>\n"+
                        "<td>"+response[i].status+"</td>\n"+
                        "</tr>";

                }
                $(".table tbody").append(markup);
                $("#result_table").show()





            }
        });
        return false;

    });
});