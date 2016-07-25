$(function() {
    $('input').on('change', function() {
        // console.log($(this).attr('id'), $(this).val());
        var params = {};
        params[$(this).attr('id')] = $(this).val();
        $.post('/params/edit', params);
    });
});

//Setup for jquery-ui range sliders
$(function(){
  $(".slider-range").slider({
    orientation:"vertical",
    range:true,
    min:0,
    max:255,
    values:[0,255],
    slide: function(event, ui) {
      $("#"+this.id+"label").val("("+ui.values[ 0 ]+","+ui.values[ 1 ]+")");
      var params = {};
      params[this.id+"_min"] = ui.values[0];
      params[this.id+"_max"] = ui.values[1];
      $.post('/params/edit', params);
    }
  });
});