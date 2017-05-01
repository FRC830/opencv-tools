$(function() {
    socket = io('/stream/' + $('#stream-target').attr('data-ns'));
    var image_url;
    var URL = window.URL || window.webkitURL;
    if (!URL) {
        throw new Error("window.URL not available");
    }
    socket.on('frame', function(data) {
        var blob = new Blob([new Uint8Array(data.raw)], {type: "image/jpeg"});
        // free the old URL
        if (image_url) {
            URL.revokeObjectURL(image_url);
        }
        image_url = URL.createObjectURL(blob);
        document.getElementById('stream-target').src = image_url;
    });
});
