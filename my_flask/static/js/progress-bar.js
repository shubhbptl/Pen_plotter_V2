
$(function () {
    $('#form1').fileupload({
        dataType: 'json',
        progressall: function (e, data) {
            var progress = parseInt(data.loaded / data.total * 100, 10);
            $('#progress-bar').setAttribute('value', progress);
        },
        done: function (e, data) {
            alert('File uploaded successfully');
        }
    });
});
