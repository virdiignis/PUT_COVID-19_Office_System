// This code activates flatpickr on fields with the 'datetimefield' class when the document has loaded
$(function () {
    flatpickr(".datetimefield", {
        enableTime: true,
        enableSeconds: true,
        dateFormat: "d.m.Y H:i:S",
        time_24hr: true,
        defaultDate: new Date()
    });
    flatpickr(".datefield", {
        enableTime: false,
        enableSeconds: false,
        dateFormat: "d.m.Y",
        time_24hr: true,
        defaultDate: new Date()
    });

    $("input:not([type=hidden])").addClass("form-control");
    // $('select:not([class])').addClass("form-control");
    let inputfile = $("input:file");
    inputfile.addClass("form-control-file");
    inputfile.removeClass("form-control");
    let label = $("label")
    label.addClass("col-5");
    label.addClass("col-form-label");
});