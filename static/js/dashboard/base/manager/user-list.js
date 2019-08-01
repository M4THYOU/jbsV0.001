$(function() {

    // get CSRF token
    var csrfToken = $('input[name="csrfmiddlewaretoken"]').val();

    var userDict = {}

    // get users with ajax
    function ajaxGetUsers() {
        $.ajax({
            url: "/hive/ajax/user-list/",
            type: "GET",
            success: function(data) {
                userDict = data;

                var htmlToAppend = '';
                $.each(userDict, function(email, info) {


                    var name = info['name']['first'] + ' ' + info['name']['last'];
                    var status = info['status']

                    var statusBadge = '<td class="status-badge"><span class="label label-success">Active</span></td>';
                    if (status == 'active') {
                        statusBadge = '<td class="status-badge"><span class="label label-success">Active</span></td>';
                    } else if (status == 'leave') {
                        statusBadge = '<td class="status-badge"><span class="label label-warning">On Leave</span></td>';
                    } else if (status == 'remove') {
                        statusBadge = '<td class="status-badge"><span class="label label-danger">Pending Removal</span></td>';
                    }

                    var userRow = (
                        '<tr data-email="' + email + '">' +
                            '<td>' + name + '</td><td>' + email + '</td>' + statusBadge +
                            '<th><div>' +
                                    '<button type="button" class="btn btn-success btn-status status-activate">Activate</button>' +
                                    '<button type="button" class="btn btn-warning btn-status status-leave">Put on leave</button>' +
                                    '<button type="button" class="btn btn-danger btn-status status-remove">Remove</button>' +
                            '</div></th>' +
                        '</tr>'
                    );

                    htmlToAppend += userRow;

                })

                $('#user-list-table').append(htmlToAppend);
                $('.user-list-loading-indicator').remove();

                addButtonListeners();
            }
        })

    }

//updating status

    function addButtonListeners() {
        $('.status-activate').on('click', function() {
            $('#user-list-box').append('<div class="overlay" id="status-change-loading-indicator"><i class="fa fa-refresh fa-spin"></i></div>');

            var email = $(this).parent().parent().parent().data('email');
            var newStatus = 'active';

            var updateStatusData = {'email': email, 'status': newStatus};
            var jsonUpdateStatusDate = JSON.stringify(updateStatusData);
            ajaxUpdateUserStatus(jsonUpdateStatusDate);
        })
        $('.status-leave').on('click', function() {
            $('#user-list-box').append('<div class="overlay" id="status-change-loading-indicator"><i class="fa fa-refresh fa-spin"></i></div>');

            var email = $(this).parent().parent().parent().data('email');
            var newStatus = 'leave';

            var updateStatusData = {'email': email, 'status': newStatus};
            var jsonUpdateStatusDate = JSON.stringify(updateStatusData);
            ajaxUpdateUserStatus(jsonUpdateStatusDate);
        })
        $('.status-remove').on('click', function() {
            $('#user-list-box').append('<div class="overlay" id="status-change-loading-indicator"><i class="fa fa-refresh fa-spin"></i></div>');

            var email = $(this).parent().parent().parent().data('email');
            var newStatus = 'remove';

            var updateStatusData = {'email': email, 'status': newStatus};
            var jsonUpdateStatusDate = JSON.stringify(updateStatusData);
            ajaxUpdateUserStatus(jsonUpdateStatusDate);
        })
    }

    function showAlert(bodyText, isSuccess) {

        var alertBox;
        if (isSuccess) {
            var alertBox = ('<div class="alert alert-success alert-dismissible">' +
             '<button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button>' +
             '<h4><i class="icon fa fa-check"></i> Success</h4>' + bodyText + '</div>'
            );
        } else {
            var alertBox = ('<div class="alert alert-danger alert-dismissible">' +
             '<button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button>' +
             '<h4><i class="icon fa fa-ban"></i> Request Failed</h4>' + bodyText + '</div>'
            );
        }

        $('#user-list-box').append(alertBox).delay(5000).queue(function(next) {
            $(this).find('.alert').slideUp(500);
            next();
        });

    }

    function changeStatusBadge(email, status) {
        var statusBadge = '<span class="label label-success">Active</span>';
        if (status == 'active') {
            statusBadge = '<span class="label label-success">Active</span>';
        } else if (status == 'leave') {
            statusBadge = '<span class="label label-warning">On Leave</span>';
        } else if (status == 'remove') {
            statusBadge = '<span class="label label-danger">Pending Removal</span>';
        }

        var userRow = $("#user-list-box").find("tr[data-email='"+email+"']");
        var badgeContainer = userRow.find('.status-badge');
        badgeContainer.html(statusBadge);
    }

    // update needs with ajax
    function ajaxUpdateUserStatus(data) {
        $.ajax({
            url: "/hive/ajax/user-list/update/",
            type: "POST",
            data: data,
            timeout: 15000,
            success: function(data) {
                var message = data['message'];
                var newStatus = data['status'];
                var email = data['email'];
                $('#status-change-loading-indicator').remove();

                changeStatusBadge(email, newStatus);

                showAlert(message, true);
            },
            error: function(xhr, textStatus, errorThrown) {
                $('#status-change-loading-indicator').remove();
                showAlert('Error: "' + errorThrown + '"', false);
            },
            beforeSend: function(xhr, settings) {
                if (!this.crossDomain) {
                    xhr.setRequestHeader('X-CSRFToken', csrfToken);
                }
            }
        })
    }

    // Add user
    $('#add-user-button').on('click', function() {
        $('#modal-user-adder').modal('show');
    })

    function validateEmail(email) {
        var re = /\S+@\S+\.\S+/;
        return re.test(email);
    }

    function validateUserForm() {
        var isValid = true;

        var $firstField = $('#new-first');
        var $lastField = $('#new-last');
        var $emailField = $('#new-email');
        var $positionField = $('#new-position');
        var $isPtField = $('#new-is-pt');

        var first = $firstField.val().trim();
        var last = $lastField.val().trim();
        var email = $emailField.val().trim();
        var position = $positionField.val().trim();
        var isPt = $isPtField.is(':checked');

        if (first == "") {
            isValid = false;
            $firstField.css('border-color', 'red');
        } else {
            $firstField.css('border-color', '');
        }

        if (last == "") {
            isValid = false;
            $lastField.css('border-color', 'red');
        } else {
            $lastField.css('border-color', '');
        }

        if (email == "") {
            isValid = false;
            $emailField.css('border-color', 'red');
        } else if (!validateEmail(email)) {
            isValid = false;
            $emailField.css('border-color', 'red');
        } else {
            $emailField.css('border-color', '');
        }

        if (position == "") {
            isValid = false;
            $positionField.css('border-color', 'red');
        } else {
            $positionField.css('border-color', '');
        }

        var cleanedForm = {
            'isValid': isValid,
            'first': first,
            'last': last,
            'email': email,
            'position': position,
            'isPt': isPt
        }

        return cleanedForm;
    }

    $('#actual-add-user-button').on('click', function() {

        var cleanedForm = validateUserForm();
        var isValid = cleanedForm['isValid'];

        if (isValid) {
            console.log('make ajax request');

            $.ajax({
            url: "/hive/ajax/user-list/new/",
            type: "POST",
            data: cleanedForm,
            timeout: 15000,
            success: function(data) {
                console.log(data);
                /*
                var message = data['message'];
                var newStatus = data['status'];
                var email = data['email'];
                $('#status-change-loading-indicator').remove();

                changeStatusBadge(email, newStatus);

                showAlert(message, true);
                */
            },
            error: function(xhr, textStatus, errorThrown) {
                $('#status-change-loading-indicator').remove();
                showAlert('Error: "' + errorThrown + '"', false);
            },
            beforeSend: function(xhr, settings) {
                if (!this.crossDomain) {
                    xhr.setRequestHeader('X-CSRFToken', csrfToken);
                }
            }
        })

        }
    })

    // call functions
    ajaxGetUsers();

})