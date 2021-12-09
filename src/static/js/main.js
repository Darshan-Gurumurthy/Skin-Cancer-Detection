$(document).ready(function () {

    // Add the following code if you want the name of the file appear on select
    $(".custom-file-input").change(function () {
        var fileName = $(this).val().split("\\").pop();
        $(this).siblings(".custom-file-label").addClass("selected").html(fileName);
    });



    $('#upload-file').submit(function (event) {
        if (document.getElementById("customFile").files.length == 0) {
            event.preventDefault();
            alert("Please select a file before submit");
        }
    });

    $('#submit-url').submit(function (event) {
        //alert("Please enter image URL before submit");
        if (document.getElementById("url-input").value == "") {
            event.preventDefault();
            alert("Please enter image URL before submit");
        }
    });



    */
});
