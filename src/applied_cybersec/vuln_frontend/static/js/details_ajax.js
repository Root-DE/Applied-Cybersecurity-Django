$(document).ready(function(){
    $('#pagination_div').on('click', 'a[id^="pagination_link_"]', function(e){
        e.preventDefault();
        var repo_org = $(this).attr('data-repo-org');
        var repo_name = $(this).attr('data-repo-name');
        var page_number = $(this).attr('data-page-number');
        var url = '/details/' + repo_org + '/' + repo_name + '?page=' + page_number

        var pagination_div = document.getElementById('pagination_div');
        var vuln_table_body = document.getElementById('vuln_table_body');

        $.ajax({
            url: url,
            type: 'POST',
            data: {
                'action': 'paginate',
                'page': page_number,
            },
            success: function(ajax_data) {
                // set new table content
                vuln_table_body.innerHTML = ajax_data.vuln_table
                // set new pagination
                pagination_div.innerHTML = ajax_data.pagination_div
                // set the new url
                window.history.pushState('', '', url)
            }

        });
    });
});

function select_scan(repo_org, repo_name) {
    // get table body and scan info field for new data
    var vuln_table_body = document.getElementById('vuln_table_body');
    $.ajax({
        url: '/details/' + repo_org + '/' + repo_name,
        type: 'POST',
        data: {
            'action': 'select_scan',
            'date': ''
        },
        dataType: 'json',
        success: function (ajax_data) {
            // set new table content
            vuln_table_body.innerHTML = ajax_data.vuln_table
        }
    })
}

// function paginate(repo_org, repo_name, page_number) {
//     var url = '/details/' + repo_org + '/' + repo_name + '?page=' + page_number

//     var pagination_div = document.getElementById('pagination_div');
//     var vuln_table_body = document.getElementById('vuln_table_body');

//     $.ajax({
//         url: url,
//         type: 'POST',
//         data: {
//             'action': 'paginate',
//             'page': page_number,
//         },
//         success: function(ajax_data) {
//             // set new pagination
//             pagination_div.innerHTML = ajax_data.pagination_div
//             // set new table content
//             vuln_table_body.innerHTML = ajax_data.vuln_table
//             // set the new url
//             window.history.pushState({route:url}, '', url)
//         }

//     });
// }
