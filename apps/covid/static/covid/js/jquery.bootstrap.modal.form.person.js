/*
django-bootstrap-modal-forms
version : 2.0.0
Copyright (c) 2020 Uros Trstenjak
https://github.com/trco/django-bootstrap-modal-forms
*/

(function ($) {

    // Open modal & load the form at formURL to the modalContent element
    let modalForm = function (settings) {
        $(settings.modalID).find(settings.modalContent).load(settings.formURL, function () {
            $(settings.modalID).modal("show");
            $(settings.modalForm).attr("action", settings.formURL);
            addEventHandlers(settings);
        });
    };

    let addEventHandlers = function (settings) {
        // submitBtn click handler
        $(settings.submitBtn).on("click", function () {
            isFormValid(settings, submitForm);
        });
        // Modal close handler
        $(settings.modalID).on("hidden.bs.modal", function () {
            $(settings.modalForm).remove();
        });
    };


    // Check if form.is_valid() & either show errors or submit it via callback
    let isFormValid = function (settings, callback) {
        $.ajax({
            type: $(settings.modalForm).attr("method"),
            url: $(settings.modalForm).attr("action"),
            data: $(settings.modalForm).serialize(),
            beforeSend: function () {
                $(settings.submitBtn).prop("disabled", true);
            },
            success: function (response) {
                if ($(response).find(settings.errorClass).length > 0) {
                    // Form is not valid, update it with errors
                    $(settings.modalID).find(settings.modalContent).html(response);
                    $(settings.modalForm).attr("action", settings.formURL);
                    // Reinstantiate handlers
                    addEventHandlers(settings);
                } else {
                    // Form is valid, submit it
                    callback(settings);
                }
            }
        });
    };

    // Submit form callback function
    let submitForm = function (settings) {
        let asyncSettings = settings.asyncSettings;
        let asyncSettingsValid = validateAsyncSettings(asyncSettings);

        if (asyncSettingsValid) {
            $.ajax({
                type: $(settings.modalForm).attr("method"),
                url: $(settings.modalForm).attr("action"),
                // Add asyncUpdate and check for it in save method of CreateUpdateAjaxMixin
                data: $(settings.modalForm).serialize() + "&asyncUpdate=True",
                success: function (response) {
                    // Update page without refresh
                    if (asyncSettings.closeOnSubmit) {
                        $(settings.modalID).modal("hide");
                    } else {
                        // Reload form
                        $(settings.modalID).find(settings.modalContent).load(settings.formURL, function () {
                            $(settings.modalForm).attr("action", settings.formURL);
                            addEventHandlers(settings);
                        });
                    }

                    let option = new Option(response["name"], response["id"], true, true);
                    $('#id_people').append(option).trigger('change');

                }
            });

        }
    };


    let validateAsyncSettings = function (settings) {
        let missingSettings = [];

        if (!settings.addModalFormFunction) {
            missingSettings.push("addModalFormFunction");
            console.error("django-bootstrap-modal-forms: 'addModalFormFunction' in asyncSettings is missing.");
        }

        return missingSettings.length === 0;
    };

    $.fn.modalForm = function (options) {
        // Default settings
        let defaults = {
            modalID: "#modal",
            modalContent: ".modal-content",
            modalForm: ".modal-content form",
            formURL: null,
            errorClass: ".invalid",
            submitBtn: ".submit-btn",
            asyncUpdate: false,
            asyncSettings: {
                closeOnSubmit: false,
                addModalFormFunction: null
            }
        };

        // Extend default settings with provided options
        let settings = $.extend(defaults, options);

        this.each(function () {
            // Add click event handler to the element with attached modalForm
            $(this).click(function (event) {
                // Instantiate new form in modal
                modalForm(settings);
            });
        });

        return this;
    };

}(jQuery));