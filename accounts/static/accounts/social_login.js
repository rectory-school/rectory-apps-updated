onAuth = (googleUser) => {
    console.log(googleUser);

    let loc = $(location).attr("href");
    var id_token = googleUser.getAuthResponse().id_token;

    $.ajax({
        url: loc,
        type: 'post',
        data: { 'token': id_token },
        headers: { 'X-CSRFToken': csrftoken },
        dataType: 'json',
        success: function (data) {
            let next = getUrlParameter("next");
            window.location = next;

            console.info(data);
        },
        error: onAuthError,
    });
}

onAuthError = (error) => {
    $(".hide-during-sign-in").show();
    $(".show-during-sign-in").hide();

    if (error.error == "popup_closed_by_user") {
        console.log("popup was closed");
        return
    }

    console.log("error when executing Google sign-in", error);
    alert("There was an issue when signing into Google. Please contact Technology.");
};

$(document).ready(function () {
    gapi.load('auth2', function () {
        // Retrieve the singleton for the GoogleAuth library and set up the client.
        auth2 = gapi.auth2.init({});

        $(".google-sign-in").each(function (i, e) {
            auth2.attachClickHandler(e, {}, onAuth, onAuthError);
        });

        $(".google-sign-in").click(function (e) {
            $(".hide-during-sign-in").hide();
            $(".show-during-sign-in").show();
        });
    });
});



