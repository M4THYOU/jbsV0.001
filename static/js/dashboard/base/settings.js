$(function() {

// Change Password /////////////////////////////////////////////////////////////////////////////////////////////////////

    $('#password-change-button').on('click', function(e) {

        $('#change-password-box').append('<div class="overlay" id="change-password-loading-indicator"><i class="fa fa-refresh fa-spin"></i></div>')

        $('#email-field').removeClass('error-text-field');
        $('#current-password').removeClass('error-text-field');
        $('#new-password').removeClass('error-text-field');
        $('#change-password-error-text').text('');

        var email = $.trim($('#email-field').val());
        var currentPassword = $.trim($('#current-password').val());
        var newPassword = $.trim($('#new-password').val());

        var returnEarly = false;
        if (email === "") {
            $('#email-field').addClass('error-text-field');
            $('#change-password-error-text').text('Please enter a value.');
            returnEarly = true;
        }
        if (currentPassword === "") {
            $('#current-password').addClass('error-text-field');
            $('#change-password-error-text').text('Please enter a value.');
            returnEarly = true;
        }
        if (newPassword === "") {
            $('#new-password').addClass('error-text-field');
            $('#change-password-error-text').text('Please enter a value.');
            returnEarly = true;
        }

        if (returnEarly) {
            $('#change-password-loading-indicator').remove();
            return;
        }

        if (newPassword.length < 8) {
            $('#new-password').addClass('error-text-field');
            $('#change-password-error-text').text('Too short.');
            $('#change-password-loading-indicator').remove();
            return;
        }

        var realEmail = $('#current-email').val();

        if (realEmail != email) {
            $('#change-password-error-text').text('Invalid credentials.');
            $('#change-password-loading-indicator').remove();
            return;
        }

        firebase.auth().onAuthStateChanged(function(user) {
            if (user) {
                firebase.auth().signInWithEmailAndPassword(email, currentPassword).then(function(user) {
                    console.log('valid');

                    var currentUser = firebase.auth().currentUser;

                    currentUser.updatePassword(newPassword).then(function() {
                        $('#change-password-loading-indicator').remove();

                        window.location.href = '/hive/login/';

                    }).catch(function(error) {
                        $('#change-password-error-text').text(error['message']);
                        $('#change-password-loading-indicator').remove();
                    })

                }).catch(function(error) {
                    if (error['code'] === 'auth/user-not-found' || error['code'] === 'auth/wrong-password') {
                        $('#change-password-error-text').text('Invalid credentials.');
                    } else {
                        console.log(error);
                        $('#change-password-error-text').text(error['message']);
                    }
                    $('#change-password-loading-indicator').remove();
                })
            } else {
                console.log('null');
                $('#change-password-loading-indicator').remove();
            }
        })

    })

// xxx /////////////////////////////////////////////////////////////////////////////////////////////////////////////////

})