$(document).ready(function() {
    var block_request = false;

    $("#repo_search_input").on("keydown", function(e) {
        if (e.keyCode == 13) {
            $("#repo_search_button").click();
        }
    });

    $("#repo_search_button").click(function() {
        var search_term = $("#repo_search_input").val();
        // get selected value
        var search_org = $("#repo_org_select").val();
        console.log(search_org);
        block_request = true;

        var repo_container = document.getElementById('repository_container');

        $.ajax({
            url: '/dashboard/',
            type: 'POST',
            data: {
                'action': 'search_repos',
                'search_term': search_term,
                'search_org': search_org
            },
            success: function(ajax_data) {
                // set new repository content
                repo_container.innerHTML = ajax_data.card_deck;
                $.generate_graphs(ajax_data.graph_data);
                block_request = false;
            }
        });

    });
});

var hover_delay = 1500,
    hover_timeout;
$('.flip').hover(function() {
    hover_timeout = setTimeout(function() {
        $(this).find('.card').toggleClass('flipped');
    }, hover_delay);
}, function() {
    clearTimeout(hover_timeout);
});

$.generate_graphs = function(graph_data) {
    graph_data.forEach(function(graph) {
        var ctx = document.getElementById(graph.repo_org + graph.repo_name).getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                datasets: [{
                    data: [
                        graph.statistics.number_vuln_critical,
                        graph.statistics.number_vuln_high,
                        graph.statistics.number_vuln_medium,
                        graph.statistics.number_vuln_low,
                        graph.statistics.number_vuln_negligible
                    ],
                    backgroundColor: ['#00bcd4', '#f44336', '#ff9800', '#4caf50', '#9e9e9e'],
                }],
                labels: ['Crit', 'High', 'Med', 'Low', 'Neg']
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                scales: {
                    x: {
                        ticks: {display: false},
                        grid: {display: false}
                    },
                    y: {
                        grid: {display: false}
                    }
                },
                plugins: {
                    legend: {display: false},
                    title: {
                        display: true,
                        text: 'Vulnerabilities'
                    },
                },
            }
        });
    });
}

window.onload = function() {
    var scans = JSON.parse(document.getElementById('scan_data').textContent);
    $.generate_graphs(scans);
};