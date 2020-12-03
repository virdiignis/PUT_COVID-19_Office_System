$(function () {
    $("#languageChangeButtonPL").on('click', function () {
        window.location.href = window.location.href.replaceAll('/en/', '/pl/');
    });
    $("#languageChangeButtonEN").on('click', function () {
        window.location.href = window.location.href.replaceAll('/pl/', '/en/');
    });
})