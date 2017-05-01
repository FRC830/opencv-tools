$(function() {
    socket = io('/stream/' + $('#stream-target').attr('data-ns'));
    socket.on('frame', function(data) {
        var blob = new Blob([new Uint8Array(data.raw)], {type: "image/jpeg"});
        var imageUrl = (window.URL || window.webkitURL).createObjectURL(blob);
        document.getElementById('stream-target').src = imageUrl;
    })
});
