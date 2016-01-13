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
                                axes: {
                                    x: {
                                        0: {side: 'top', label: 'Age'} // Top x-axis.
                                    }
                                },
                                bar: {groupWidth: "90%"}
                            };
                            drawStuff("page-chart", options, result.page_age, true);
                            options = {
                                title: 'Distribution of other users\' social age with same biological age as you',
                                width: 900,
                                legend: {position: 'none'},
                                chart: {
                                    title: 'Distribution of Social Age',
                                    subtitle: 'Biological Age = 24'
                                },
                                axes: {
                                    x: {
                                        0: {side: 'top', label: 'Social Age'} // Top x-axis.
                                    },
                                    y: {
                                        0: {label: 'Frequency'} // Top x-axis.
                                    }
                                },
                                bar: {groupWidth: "90%"}
                            };
                            drawStuff("bio-age", options, result.bio_dist, false);

                            options = {
                                title: 'Distribution of other users\' biological Age with same social age as you',
                                width: 900,
                                legend: {position: 'none'},
                                chart: {
                                    title: 'Distribution of Biological Age',
                                    subtitle: 'Social Age = ' + result.soc_age.toString()
                                },
                                axes: {
                                    x: {
                                        0: {side: 'top', label: 'Biological Age'} // Top x-axis.
                                    },
                                    y: {
                                        0: {label: 'Frequency'} // Top x-axis.
                                    }
                                },
                                bar: {groupWidth: "90%"}
                            };
                            drawStuff("soc-age", options, result.soc_dist, false);
                        }
                    });
                }
            });
        });
    });

