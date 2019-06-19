function onLogout() {
    var userselection = confirm("Caution! Logging out deletes all of your photos and videos!");

    if (userselection == true){
        window.location.href = '/logout';
    }
}

function getPage(page) {
    window.location.href = page + '?rand=' + Math.random();
}