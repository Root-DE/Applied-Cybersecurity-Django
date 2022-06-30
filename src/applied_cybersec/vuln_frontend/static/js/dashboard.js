var hover_delay = 1500, hover_timeout;
$('.flip').hover(function(){
    hover_timeout = setTimeout(function(){
        $(this).find('.card').toggleClass('flipped');
    }, hover_delay);
}, function(){ 
    clearTimeout(hover_timeout);
});
