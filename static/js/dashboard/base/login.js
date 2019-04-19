$(function() {

    function toggleLoading(turnOn) {

        if (turnOn) {
            $('.login-box-body').append('<div class="overlay" id="loading-indicator"><i class="fa fa-refresh fa-spin"></i></div>')
        } else {
            $('#loading-indicator').remove()
        }

    }

    function signIn() {

        toggleLoading(true);

        $email = $('#id_email');
        $password = $('#id_password');

        firebase.auth().signInWithEmailAndPassword($email.val(), $password.val()).then(function(user) {

            firebase.auth().currentUser.getIdToken(true).then(function(idToken) {
                //send token to backend

                $('#id_token').val(idToken);

                $('#hidden-button').trigger('click');

            }).catch(function(error) {
                console.error(error);
                toggleLoading(false);
            })

        }).catch(function(error) {
            $('#form-error').text('Invalid Credentials');
            toggleLoading(false);
        });

    }

    $('#form-button').on('click', signIn);

    $('#id_password').keypress(function(e) {
        var key = e.which;

        if (key == 13) {
            signIn();
        }

    })

})