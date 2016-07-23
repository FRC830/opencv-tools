$(function() {
    $('input').on('change', function() {
        console.log("CHANGE");
        // console.log($(this).attr('id'), $(this).val());
        var params = {};
        params[$(this).attr('id')] = $(this).val();
        $.post('/params/edit', params);
    });
});
