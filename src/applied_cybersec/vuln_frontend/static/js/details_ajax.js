$(document).ready(function() {
    var page = 2;
    var block_request = false;
    var end_pagination = JSON.parse(document.getElementById('end_pagination').textContent);

    // save the state of the initial page
    history.replaceState({
        'vuln_table_body': document.getElementById('vuln_table_body').innerHTML,
        'scan_data': document.getElementById('scan_data').innerHTML,
        'time_select_div': document.getElementById('time_select_div').innerHTML,
        'act_date': document.getElementById('datepicker_input').value,
    }, '', window.location.href);

    // datetimepicker functionality
    $(function() {
        $('#id_1').datetimepicker({
            "allowInputToggle": true,
            "showClose": true,
            "showClear": true,
            "showTodayButton": true,
            "format": "DD-MM-YYYY",
        }).on('dp.hide', function(e) {
            // function to call, when the date is changed
            var date = $('#datepicker_input').val();
            var datetime = date + ' 23:59:59';
            
            // load the new scan
            $.load_scan(datetime);
        });
    });

    // select new time functionality
    $('#time_select_div').on('change', '#time_select', function(e) {
        e.preventDefault();
        // select a new scan
        var date = $('#datepicker_input').val();
        var time = $('#time_select').val();
        var datetime = date + ' ' + time;
        // load the new scan
        $.load_scan(datetime);
    });

    // download file functionality
    $('#download_sbom_btn').click(function() {
        download_file('sbom');
    });
    $('#download_vuln_btn').click(function() {
        download_file('vuln');
    });

    // infinit scroll functionality
    $(window).scroll(function() {
        var margin = $(document).height() - $(window).height() - 300; //$(window).scrollTop();
        if ($(window).scrollTop() >= margin && end_pagination === false && block_request === false) {
            // request the next page
            console.log("request next page");
            block_request = true;
            
            
            // build the url
            var repo_org = JSON.parse(document.getElementById('repo_org').textContent)
            var repo_name = JSON.parse(document.getElementById('repo_name').textContent)
            var url_params = new URLSearchParams(window.location.search);
            var url = '/details/' + repo_org + '/' + repo_name
            var date = url_params.get('date');
            if (date) {
                url += '?date=' + decodeURI(date);
            }
            var search_term = document.getElementById('vuln_search_input').value;
            
            // get the filter values
            filter_type = document.getElementById('filter_input').value
            filter_direction = document.getElementById('direction_input').value

            // send the request
            $.ajax({
                url: url,
                type: 'POST',
                data: {
                    'action': 'infinit_scroll',
                    'page': page,
                    'search_term': search_term,
                    'filter_type': filter_type,
                    'filter_direction': filter_direction,
                },
                success: function(ajax_data) {
                    // set new table content
                    vuln_table_body.innerHTML += ajax_data.vuln_table

                    // refresh the state
                    page += 1;
                    if (ajax_data.end_pagination === true) {
                        console.log("end_pagination");
                        end_pagination = true;
                    } else {
                        block_request = false;
                    }
                }
            });
        }
    }); // end infinit scroll functionality

    // search functionality
    $('#vuln_search_input').on('input', function() {
        var search_term = $(this).val();
        console.log(search_term);
        block_request = true;
    
        // build the url
        var repo_org = JSON.parse(document.getElementById('repo_org').textContent)
        var repo_name = JSON.parse(document.getElementById('repo_name').textContent)
        var url_params = new URLSearchParams(window.location.search);
        var url = '/details/' + repo_org + '/' + repo_name
        var date = url_params.get('date');
        if (date) {
            url += '?date=' + decodeURI(date);
        }

        // reset the infinite scroll
        page = 1;
        end_pagination = false;

        // send the search request
        $.ajax({
            url: url,
            type: 'POST',
            data: {
                'action': 'search',
                'page': page,
                'search_term': search_term,
            },
            success: function(ajax_data) {
                // set new table content
                vuln_table_body.innerHTML = ajax_data.vuln_table

                // refresh the state
                page += 1;
                if (ajax_data.end_pagination === true) {
                    end_pagination = true;
                } else {
                    block_request = false;
                }
            }
        });        
    }); // end search functionality


    // load a new scan functionality
    $.load_scan = function(date) {
        block_request = true;
        page = 1;
        end_pagination = false;

        var repo_org = JSON.parse(document.getElementById('repo_org').textContent)
        var repo_name = JSON.parse(document.getElementById('repo_name').textContent)
        var url = '/details/' + repo_org + '/' + repo_name + '?date=' + date

        var scan_data_div = document.getElementById('scan_data');
        var datetimepicker_input = document.getElementById('datepicker_input');
        var time_select_div = document.getElementById('time_select_div');
        var vuln_table_body = document.getElementById('vuln_table_body');
        
        $.ajax({
            url: url,
            type: 'POST',
            data: {
                'action': 'select_scan',
                'page': page,
            },
            success: function(ajax_data) {
                // set new table content
                vuln_table_body.innerHTML = ajax_data.vuln_table
                // set the date of the scan
                datetimepicker_input.value = ajax_data.scan_time
                // set the new times
                time_select_div.innerHTML = ajax_data.time_select_div
                // set new scan content
                scan_data_div.innerHTML = ajax_data.scan_data
                // refresh the pieChart
                $.generate_pieChart(ajax_data.statistics);
                // reset the search input
                $('#vuln_search_input').val('');
                new_state = {
                    // 'vuln_table_body': ajax_data.vuln_table,
                    'scan_data': ajax_data.scan_data,
                    'time_select_div': ajax_data.time_select_div,
                    'act_date': ajax_data.scan_time,
                }
                window.history.pushState(new_state, '', url)

                // refresh the state
                page += 1;
                if (ajax_data.end_pagination === true) {
                    end_pagination = true;
                } else {
                    block_request = false;
                }
            }
        });
    }

    $('th[id^="filter_"]').on('click', function() {
        elem_id = $(this).attr('id');

        // we start from beginning with new order
        block_request = true;
        page = 1;
        end_pagination = false;

        // build the url
        var repo_org = JSON.parse(document.getElementById('repo_org').textContent)
        var repo_name = JSON.parse(document.getElementById('repo_name').textContent)
        var date = $('#datepicker_input').val();
        var datetime = date + ' 23:59:59';
        var url = '/details/' + repo_org + '/' + repo_name + '?date=' + datetime

        // remove all filter icons first
        filter_ids = ['filter_id', 'filter_sev', 'filter_stat', 'filter_cvss']
        filter_ids.forEach(element => {
            document.getElementById(element).getElementsByTagName('i')[0].className = ''
        });

        // now add the new filter icon
        var filter_elem = document.getElementById(elem_id);
        var filter_icon = filter_elem.getElementsByTagName('i')[0];
        // if filter_type is changed always take ascending order
        var filter_type_old = document.getElementById('filter_input').value
        var filter_type_new = filter_elem.dataset.filter;
        var filter_direction = document.getElementById('direction_input').value;
        var new_direction = 'asc';
        if (filter_type_old == filter_type_new) {
            new_direction = filter_direction == 'asc' ? 'desc' : 'asc';
        }
        filter_icon.className = new_direction == 'asc' ? 'fa fa-arrow-down' : 'fa fa-arrow-up';

        // set the filter type to hidden input
        document.getElementById('filter_input').value = filter_type_new;
        document.getElementById('direction_input').value = new_direction;

        // send the ajax to apply the new filter
        $.ajax({
            url: url,
            type: 'POST',
            data: {
                'action': 'filter',
                'filter_direction': new_direction,
                'filter_type': filter_type_new,
            },
            beforeSend: function() {
                // show the loading icon
                document.getElementById('loading_icon').style.display = 'block';
            },
            success: function(ajax_data) {
                // set new table content
                vuln_table_body.innerHTML = ajax_data.vuln_table

                // refresh the state
                page += 1;
                if (ajax_data.end_pagination === true) {
                    end_pagination = true;
                } else {
                    block_request = false;
                }
            },
            complete: function() {
                // hide the loading icon
                document.getElementById('loading_icon').style.display = 'none';
            }
        });
    })

    // expand table row functionality
    // $("#vuln_table_body").find('tr[id^="vuln_hidden_div_"]').hide();
    $("#vuln_table_body").on('click', 'tr[id^="vuln_row_"]', function(event) {
        event.stopPropagation();
        var $target = $(event.target);
        // id of clicked row
        clicked_id = $(this).attr("id").split('_').pop();
        $("#vuln_hidden_div_" + clicked_id).slideToggle();
    });


});

function download_file(result_type) {
    document.getElementById('workflow_id_target').value = document.getElementById('workflow_id_src').textContent;
    document.getElementById('result_type_target').value = result_type;
    document.getElementById('download_form').submit();
}


// make back and forward buttons work
window.onpopstate = function(event) {
    // prevent scrolling
    event.preventDefault();
    if ('scrollRestoration' in window.history) {
        window.history.scrollRestoration = 'manual';
    }

    if (event.state) {
        // set the new table content
        if (event.state.vuln_table_body) {
            document.getElementById('vuln_table_body').innerHTML = event.state.vuln_table_body
        }
        // set the new scan content
        if (event.state.scan_data) {
            document.getElementById('scan_data').innerHTML = event.state.scan_data
        }
        // set the new time select content
        if (event.state.time_select_div) {
            document.getElementById('time_select_div').innerHTML = event.state.time_select_div
        }
        // set the new date
        if (event.state.act_date) {
            document.getElementById('datepicker_input').value = event.state.act_date
        }
        // reset the infinite scroll
        page = 1;
        end_pagination = false;
        block_request = false;
        // set the new search term
        // if (event.state.search_term) {
        //     $('#vuln_search_input').val(event.state.search_term)
        // }

    } else {
        alert("initial page")
    }
}

$.generate_myChart = function(graph_data) {

    var ctx_line = document.getElementById("myChart").getContext("2d");

    const number_vuln_critical = graph_data.critical;
    const number_vuln_high = graph_data.high;
    const number_vuln_medium = graph_data.medium;
    const number_vuln_low = graph_data.low;
    const number_vuln_negligible = graph_data.negligible;
    const number_vuln_unknown = graph_data.unknown;

    // change to type date:
    for (var i = 0; i < graph_data.created_at.length; i++) {
        graph_data.created_at[i] = new Date(graph_data.created_at[i]);
    }

    const myChart = new Chart(ctx_line, {
        type: 'line',
        data: {
            labels: graph_data.created_at,
            datasets: [{
                label: "Unknown",
                fill: true,
                backgroundColor: colors.cvss_unknown.fill,
                pointBackgroundColor: colors.cvss_unknown.fill,
                borderColor: colors.cvss_unknown.stroke,
                borderWidth: 1,
                pointHighlightStroke: colors.cvss_unknown.stroke,
                borderCapStyle: 'butt',
                data: number_vuln_unknown,
                pointRadius: 5,
                pointHoverRadius: 10,
            },{
                label: "Negligible",
                fill: true,
                backgroundColor: colors.cvss_negligible.fill,
                pointBackgroundColor: colors.cvss_negligible.fill,
                borderColor: colors.cvss_negligible.stroke,
                borderWidth: 1,
                pointHighlightStroke: colors.cvss_negligible.stroke,
                borderCapStyle: 'butt',
                data: number_vuln_negligible,
                pointRadius: 5,
                pointHoverRadius: 10,
            },{
                label: "Low",
                fill: true,
                backgroundColor: colors.cvss_low.fill,
                pointBackgroundColor: colors.cvss_low.fill,
                borderColor: colors.cvss_low.stroke,
                pointHighlightStroke: colors.cvss_low.stroke,
                borderWidth: 1,
                borderCapStyle: 'butt',
                data: number_vuln_low,
                pointRadius: 5,
                pointHoverRadius: 10,
            }, {
                label: "Medium",
                fill: true,
                backgroundColor: colors.cvss_medium.fill,
                pointBackgroundColor: colors.cvss_medium.fill,
                borderColor: colors.cvss_medium.stroke,
                pointHighlightStroke: colors.cvss_medium.stroke,
                borderWidth: 1,
                borderCapStyle: 'butt',
                data: number_vuln_medium,
                pointRadius: 5,
                pointHoverRadius: 10,
            }, {
                label: "High",
                fill: true,
                backgroundColor: colors.cvss_high.fill,
                pointBackgroundColor: colors.cvss_high.fill,
                borderColor: colors.cvss_high.stroke,
                pointHighlightStroke: colors.cvss_high.stroke,
                borderWidth: 1,
                borderCapStyle: 'butt',
                data: number_vuln_high,
                pointRadius: 5,
                pointHoverRadius: 10,
            }, {
                label: "Critical",
                fill: true,
                backgroundColor: colors.cvss_critical.fill,
                pointBackgroundColor: colors.cvss_critical.fill,
                borderColor: colors.cvss_critical.stroke,
                pointHighlightStroke: colors.cvss_critical.stroke,
                borderWidth: 1,
                data: number_vuln_critical,
                pointRadius: 5,
                pointHoverRadius: 10,
            }]
        },
        options: {
            // Can't just `stacked: true` like the docs say
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Date of Scan'
                    },
                    type: 'time',
                    time: {
                        unit: 'day',
                        displayFormats: {
                        minute: 'DD T'
                        },
                        tooltipFormat: 'DD T'
                    },
                    grid: {
                        z: 1
                    }
                },
                y: {
                    min: 0,
                    stacked: true,
                    title: {
                        display: true,
                        text: 'Vulnerabilities'
                    },
                    grid: {
                        z: 1
                    }
                }
            },
            animation: {
                duration: 750,
            },
            plugins: {
                legend: {
                    position: 'bottom'
                }
            },
            onClick: function(evt) {
                var activePoints = myChart.getElementsAtEventForMode(evt, 'point', true);
                // make sure click was on an actual point
                if (activePoints.length === 0) {
                    return;
                }

                var firstPoint = activePoints[0];
                var label = myChart.data.labels[firstPoint.index];

                var date = label;
                //transform date object to string
                var date_string = date.getDate() + '-' + ("0" + (date.getMonth() + 1)).slice(-2) + '-' + date.getFullYear() + " " + date.getHours() + ":" + date.getMinutes() + ":" + date.getSeconds();

                // load the new scan
                $.load_scan(date_string);
            }
        }
    });

}

$.generate_pieChart = function(statistics) {
    var ctx_pie = document.getElementById("pieChart").getContext('2d');

    var data_arr = [
        statistics.number_vuln_unknown,
        statistics.number_vuln_negligible,
        statistics.number_vuln_low,
        statistics.number_vuln_medium,
        statistics.number_vuln_high,
        statistics.number_vuln_critical
    ];
                
    const colors = {
        cvss_unknown: {
            fill: '#8aa5bc',
            stroke: '#154c79',
        },
        cvss_negligible: {
            fill: '#f6f6f1',
            stroke: '#eeeee4',
        },
        cvss_low: {
            fill: '#F4E9A9',
            stroke: '#ebd35b'
        },
        cvss_medium: {
            fill: '#F4D4A9',
            stroke: '#f2b25e',
        },
        cvss_high: {
            fill: '#F4BEA9',
            stroke: '#FF8F64',
        },
        cvss_critical: {
            fill: '#F4A8A9',
            stroke: '#FF6464',
        },  
    };

    const pieChart = new Chart(ctx_pie, {
        type: 'pie',
        data: {
            labels: ['Unknown', 'Negligible', 'Low', 'Medium', 'High', 'Critical'],
            datasets: [{
                backgroundColor: [colors.cvss_unknown.fill, 
                                colors.cvss_negligible.fill,
                                colors.cvss_low.fill,
                                colors.cvss_medium.fill,
                                colors.cvss_high.fill,
                                colors.cvss_critical.fill],
                borderColor: [colors.cvss_unknown.stroke,
                                colors.cvss_negligible.stroke,
                                colors.cvss_low.stroke,
                                colors.cvss_medium.stroke,
                                colors.cvss_high.stroke,
                                colors.cvss_critical.stroke],
                borderWidth: [1, 1, 1, 1, 1, 1],
                data: data_arr,
            }]
        },
        options: {
            title: {
                display: true,
                text: 'Vulnerability Categories'
            },
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

window.onload = function() {
    var statistics = JSON.parse(document.getElementById('statistics').textContent);
    var graph_data = JSON.parse(document.getElementById('graph_data').textContent);
    $.generate_myChart(graph_data);
    $.generate_pieChart(statistics);
};

// define color palette for the charts
var colors = {
    cvss_unknown: {
        fill: '#8aa5bc',
        stroke: '#154c79',
    },
    cvss_negligible: {
        fill: '#f6f6f1',
        stroke: '#eeeee4',
    },
    cvss_low: {
        fill: '#F4E9A9',
        stroke: '#ebd35b'
    },
    cvss_medium: {
        fill: '#F4D4A9',
        stroke: '#f2b25e',
    },
    cvss_high: {
        fill: '#F4BEA9',
        stroke: '#FF8F64',
    },
    cvss_critical: {
        fill: '#F4A8A9',
        stroke: '#FF6464',
    },  
};


// function filter_table(elem_id) {
//     // we start from beginning with new order
//     block_request = true;
//     page = 1;
//     end_pagination = false;

//     // build the url
//     var repo_org = JSON.parse(document.getElementById('repo_org').textContent)
//     var repo_name = JSON.parse(document.getElementById('repo_name').textContent)
//     var date = $('#datepicker_input').val();
//     var datetime = date + ' 23:59:59';
//     var url = '/details/' + repo_org + '/' + repo_name + '?date=' + datetime

//     // remove all filter icons first
//     filter_ids = ['id_filter', 'sev_filter', 'stat_filter', 'cvss_filter']
//     filter_ids.forEach(element => {
//         document.getElementById(element).getElementsByTagName('i')[0].className = ''
//     });
    
//     // now add the new filter icon
//     var filter_elem = document.getElementById(elem_id);
//     var filter_icon = filter_elem.getElementsByTagName('i')[0];
//     var filter_direction = document.getElementById('direction_input').value;
//     var filter_type = filter_elem.dataset.filter;
//     var new_direction = filter_direction == 'asc' ? 'desc' : 'asc';
//     filter_icon.className = new_direction == 'asc' ? 'fa fa-arrow-down' : 'fa fa-arrow-up';
    
//     // set the filter type to hidden input
//     document.getElementById('filter_input').value = filter_type;
//     document.getElementById('direction_input').value = new_direction;

//     // send the ajax to apply the new filter
//     $.ajax({
//         url: url,
//         type: 'POST',
//         data: {
//             'action': 'filter',
//             'filter_direction': new_direction,
//             'filter_type': filter_type,
//         },
//         success: function(ajax_data) {
//             // set new table content
//             vuln_table_body.innerHTML = ajax_data.vuln_table


//             // refresh the state
//             page += 1;
//             if (ajax_data.end_pagination === true) {
//                 end_pagination = true;
//             } else {
//                 block_request = false;
//             }
//         }
//     });
// }