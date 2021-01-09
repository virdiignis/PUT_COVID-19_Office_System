$("input:not([type=hidden])").addClass("form-control");
$('select:not([class])').addClass("form-control");
let inputfile = $("input:file");
inputfile.addClass("form-control-file");
inputfile.removeClass("form-control");
let label = $("label")
label.addClass("col-5");
label.addClass("col-form-label");