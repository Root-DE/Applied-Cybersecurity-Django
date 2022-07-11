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

    // select new scan on timeline
    document.getElementById("myChart").onclick = function(evt) {
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
        
    };

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
            

            // send the request
            $.ajax({
                url: url,
                type: 'POST',
                data: {
                    'action': 'infinit_scroll',
                    'page': page,
                    'search_term': search_term,
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
                // reset the search input
                $('#vuln_search_input').val('');
                new_state = {
                    // 'vuln_table_body': ajax_data.vuln_table,
                    'scan_data': ajax_data.scan_data,
                    'time_select_div': ajax_data.time_select_div,
                    'act_date': ajax_data.scan_time,
                }
                window.history.pushState(new_state, '', url)

                console.log(ajax_data.vuln_table);

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


    // expand table row functionality
    // $("#vuln_table_body").find('tr[id^="vuln_hidden_div_"]').hide();
    $("#vuln_table_body").on('click', 'tr[id^="vuln_row_"]', function(event) {
        console.log("clicked");
        event.stopPropagation();
        var $target = $(event.target);
        // id of clicked row
        clicked_id = $(this).attr("id").split('_').pop();
        console.log(clicked_id);
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