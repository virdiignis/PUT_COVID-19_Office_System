$(function () {
    $("#languageChangeButtonEN").on('click', function () {
        window.location.href = window.location.href.replaceAll('/en/', '/pl/');
    });
    $("#languageChangeButtonPL").on('click', function () {
        window.location.href = window.location.href.replaceAll('/pl/', '/en/');
    });
})