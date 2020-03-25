$(function(){
    $(".error").hide();
    $("#spinner").hide();
    $('#get_result').click(function(){
        $('.error').hide();
        $("#spinner").hide();
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

        var data_string = "signal="+signal+"&snippet="+snippet;
        $("#spinner").show();
        $("#spinner").focus();
        $.ajax({
            type : "POST",
            url : "http://localhost:9999/rolling_window",
            data : data_string,
            success : function(response,status){
                var obj=jQuery.parseJSON(response)
                for (i=0;i<obj.length;i++){
                    score=jQuery.parseJSON(obj[i].score)
                    display_data=[]
                    for (j=0;j<score.length;j++){
                        for (k=0;k<score[i].length;k++){
                            display_data.push([j,k,score[j][k].toFixed(2)*100])
                        }
                    }
                    $("#myheatMap_"+i.toString()).highcharts({
                        chart: {
                            type: 'heatmap',
                            marginTop: 40,
                            marginBottom: 80,
                             plotBorderWidth: 1
                        },
                        title: {
                            text: 'Gram_'+(i+1).toString()
                        },
                        xAxis: {
                            categories: jQuery.parseJSON(obj[i].signals)
                        },
                        yAxis: {
                            categories: jQuery.parseJSON(obj[i].snippets),
                            title: null
                        },
                        colorAxis: {
                            min: 0,
                            minColor: '#FFFFFF',
                            maxColor: Highcharts.getOptions().colors[0]
                        },
                         legend: {
                            align: 'right',
                            layout: 'vertical',
                            margin: 0,
                            verticalAlign: 'top',
                            y: 25,
                            symbolHeight: 280
                        },
                        series: [{
                                name: '',
                                borderWidth: 1,
                                data: display_data,
                                dataLabels: {
                                    enabled: true,
                                    color: '#000000'
                                }
                            }]
                    });
                $("#myheatMap_"+i.toString()).after("<div id=myheatMap_"+(i+1).toString()+" style='width: 600px; height: 500px; margin: 0 auto'></div>")

                }
            $("#spinner").hide();
            }
        });
        return false;
    });
});