function drawStuff(id, options, json, bar) {
    try {
        var data = new google.visualization.arrayToDataTable(json);
        if (bar) {
            var chart = new google.visualization.BarChart(document.getElementById(id));
        } else {
            var chart = new google.visualization.ColumnChart(document.getElementById(id));
        }
    }
    catch (err) {

    }
    chart.draw(data, options);
}
;

$(document).ready(function () {
    google.charts.load('current', {packages: ['corechart']});
    $("#results").click(function () {
        $.ajax({
            url: "../results/",
            success: function (result) {
                $("#content").html(result);
            }
        });
    });
    $("#recommend").click(function () {
        $.ajax({
            url: "../recommended/",
            success: function (result) {
                $("#content").html(result);
            }
        });
    });
    $("#analysis").click(function () {
        $.ajax({
            url: "../analysis/",
            success: function (result) {
                $("#content").html(result);
                $('#example').dataTable();
            }
        });
    });
    $("#friends").click(function () {
        $.ajax({
            url: "../friends/",
            success: function (result) {
                $("#content").html(result);
                $.ajax({
                    url: "../friends_data/",
                    success: function (result) {
                        try {
                            var dataTable = new google.visualization.DataTable();
                            dataTable.addColumn('number', 'Biological Age');
                            dataTable.addColumn('number', 'Social Age');
                            dataTable.addColumn({type: 'string', role: 'tooltip', 'p': {'html': true}});
                            dataTable.addRows(result.data);
                            var options = {
                                title: 'Biological and Social Ages of Friends',
                                width: 900,
                                legend: {position: 'none'},
                                chart: {
                                    title: 'Biological and Social Ages of Friends'
                                },
                                hAxis: {title: 'Biological Age'},
                                vAxis: {title: 'Social Age'},
                                tooltip: {isHtml: true}
                            };
                            var chart = new google.visualization.ScatterChart(document.getElementById('friend-scatter'));
                            chart.draw(dataTable, options);
                        } catch (err) {
                        }
                    }
                });
            }
        });
    });
    $("#graphs").click(function () {
        $.ajax({
            url: "../graphs/",
            success: function (result) {
                $("#content").html(result);
                $.ajax({
                    url: "../graph_data/",
                    success: function (result) {
                        var options = {
                            title: 'Average age of liked pages',
                            width: 900,
                            legend: {position: 'none'},
                            chart: {
                                title: 'Liked Pages and Followed Users',
                                subtitle: 'average age'
                            },
                            hAxis: {title: 'Social Age'},
                            vAxis: {title: 'Page'},
                            bar: {groupWidth: "90%"}
                        };
                        drawStuff("page-chart", options, result.page_age, true);
                        options = {
                            title: 'Distribution of other users\' social age with same biological age as you',
                            width: 900,
                            legend: {position: 'none'},
                            chart: {
                                title: 'Distribution of Social Age',
                                subtitle: 'Biological Age = ' + result.bio_age
                            },
                            hAxis: {title: 'Social Age'},
                            vAxis: {title: 'Frequency'},
                            bar: {groupWidth: "90%"}
                        };
                        drawStuff("bio-age", options, result.bio_dist, false);

                        options = {
                            title: 'Distribution of other users\' biological Age with same social age as you',
                            width: 900,
                            legend: {position: 'none'},
                            chart: {
                                title: 'Distribution of Biological Age',
                                subtitle: 'Social Age = ' + result.soc_age
                            },
                            hAxis: {title: 'Biological Age'},
                            vAxis: {title: 'Frequency'},
                            bar: {groupWidth: "90%"}
                        };
                        drawStuff("soc-age", options, result.soc_dist, false);
                    }
                });
            }
        });
    });
});

