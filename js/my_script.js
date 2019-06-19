function onLogout() {
    var userselection = confirm("Caution! Logging out deletes all of your photos and videos!");

    if (userselection == true){
        window.location.href = '/logout';
    }
}

function getPage(page) {
    console.log(window.location.href);
    sep = page.split("#", 2);
    console.log(sep);
    if (sep.length == 1) {
        window.location.href = page + '?rand=' + Math.random();
    } else {
        window.location.href = page;
    }
}