function getCookie(cname) {
    let name = cname + "=";
    let decodedCookie = decodeURIComponent(document.cookie);
    let ca = decodedCookie.split(';');
    for (let i = 0; i < ca.length; i++) {
        let c = ca[i];
        while (c.charAt(0) === ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) === 0) {
            return c.substring(name.length, c.length);
        }
    }
    return null;
}

$(function () {
    let sidebar = $("#sidebar-wrapper");
    if (getCookie('menu') === 'close') {
        $("#wrapper").toggleClass("toggled");
        $("#menu-toggle img").attr("src", "{% static 'img/arrow_right.png' %}")
    }

    if (getCookie("sessionid") === null) {
        sidebar.css("visibility", "visible");
    }
    setTimeout(function () {
        sidebar.toggleClass("transition");
    }, 800);

    $("#menu-toggle").click(function (e) {
        e.preventDefault();
        $("#wrapper").toggleClass("toggled");
        let img = $("#menu-toggle img");
        if (img.attr("src").includes("left")) {
            img.attr("src", "{% static 'img/arrow_right.png' %}")
            document.cookie = 'menu=close; path=/';
        } else {
            img.attr("src", "{% static 'img/arrow_left.png' %}")
            document.cookie = 'menu=open; path=/';
        }
    });
})