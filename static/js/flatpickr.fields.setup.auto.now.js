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
});