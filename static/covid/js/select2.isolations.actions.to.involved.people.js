$(function () {
    function setup_select2_propagation(selector) {
        $(selector).each(function () {
            $(this).on("select2:select", (e) => {
                let data = e.params.data;
                let people = $('#id_people');
                let ids = people.select2("data").map(item => item.id);
                if (!ids.includes(data["id"])) {
                    let option = new Option(data["text"], data["id"], true, true);
                    people.append(option).trigger('change');
                }
            });
        });
    }

    setup_select2_propagation('[id ^=id_isolations-][id $=-person]');
    setup_select2_propagation('[id ^=id_actions-][id $=-contact_from]');
});