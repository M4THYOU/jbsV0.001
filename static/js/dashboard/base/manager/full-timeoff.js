$(function() {

    // get CSRF token
    var csrfToken = $('input[name="csrfmiddlewaretoken"]').val();

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

        $('#needs-box').append(alertBox).delay(5000).queue(function(next) {
            $(this).find('.alert').slideUp(500);
            next();
        });

    }

    var allTimeOffData = {};

    function setClickHandlers() {
        $('.time-off-approved').on('click', function(e) {
            $this = $(this);

            var $li = $this.parent().parent();

            $li.append('<div class="overlay time-off-loading-indicator"><i class="fa fa-refresh fa-spin"></i></div>');

            var id = $li.prop('id');
            var selectedTimeOff = allTimeOffData[id];

            var newStatus = {
                'pending': false,
                'approved': true,
                'denied': false,
                'expired': false
            }

            var timeOffData = {
                'email': selectedTimeOff['email'],
                'fullName': selectedTimeOff['name'],
                'date': selectedTimeOff['date'],
                'status': newStatus,
            }

            var timeOffDataString = JSON.stringify(timeOffData);
            ajaxUpdateAvailability(timeOffDataString);

        })

        $('.time-off-declined').on('click', function(e) {
            $this = $(this);

            var $li = $this.parent().parent();

            $li.append('<div class="overlay time-off-loading-indicator"><i class="fa fa-refresh fa-spin"></i></div>');

            var id = $li.prop('id');
            var selectedTimeOff = allTimeOffData[id];

            var newStatus = {
                'pending': false,
                'approved': false,
                'denied': true,
                'expired': false
            }

            var timeOffData = {
                'email': selectedTimeOff['email'],
                'fullName': selectedTimeOff['name'],
                'date': selectedTimeOff['date'],
                'status': newStatus,
            }

            var timeOffDataString = JSON.stringify(timeOffData);
            ajaxUpdateAvailability(timeOffDataString);

        })
    }

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    // get needs with ajax
    function ajaxGetAllTimeOff(date) {
        var dateString = moment(date).format('DD-MM-YYYY');

        $.ajax({
            url: "/hive/ajax/full-time-off/" + dateString + "/",
            type: "GET",
            success: function(data) {

                var pastTimeOff = data['past'];
                var todayTimeOff = data['today'];
                var upcomingTimeOff = data['upcoming'];

                pastTimeOff.sort(function(a, b) {
                    var dateA = moment(a['date'], 'DD/MM/YYYY').toDate();
                    var dateB = moment(b['date'], 'DD/MM/YYYY').toDate();

                    return dateA > dateB;
                })
                todayTimeOff.sort(function(a, b) {
                    var dateA = moment(a['date'], 'DD/MM/YYYY').toDate();
                    var dateB = moment(b['date'], 'DD/MM/YYYY').toDate();

                    return dateA > dateB;
                })
                upcomingTimeOff.sort(function(a, b) {
                    var dateA = moment(a['date'], 'DD/MM/YYYY').toDate();
                    var dateB = moment(b['date'], 'DD/MM/YYYY').toDate();

                    return dateA > dateB;
                })

                var appendToPast = ''
                pastTimeOff.forEach(function(timeOff) {
                    var liId = (timeOff['name'] + timeOff['date']).replace(/\//g, '-').replace(/ /g, '-');

                    var date = moment(timeOff['date'], 'DD/MM/YYYY').toDate();
                    var dateString = moment(date).format('MMMM DD, YYYY');

                    var statusLabel = '';
                    if (timeOff['status']['approved']) {
                        statusLabel = '<small class="label label-success">Approved</small>'
                    } else {
                        statusLabel = '<small class="label label-danger">Expired</small>'
                    }

                    appendToPast += (
                        '<li class="box" id="' + liId + '">' +
                        '<div class="text-badge-container">' +
                                statusLabel +
                                '<span><strong>' + timeOff['name'] + '</strong><br>' + dateString + '</span>' +
                            '</div>' +
                            '<div class="buttons-container">' +
                            '</div>' +
                        '</li>'
                    );

                    allTimeOffData[liId] = timeOff;

                })

                var appendToToday = '';
                todayTimeOff.forEach(function(timeOff) {
                    var liId = (timeOff['name'] + timeOff['date']).replace(/\//g, '-').replace(/ /g, '-');

                    var date = moment(timeOff['date'], 'DD/MM/YYYY').toDate();
                    var dateString = moment(date).format('MMMM DD, YYYY');

                    var statusLabel = '';
                    if (timeOff['status']['pending']) {
                        statusLabel = '<small class="label label-warning">Pending</small>'
                    } else if (timeOff['status']['approved']) {
                        statusLabel = '<small class="label label-success">Approved</small>'
                    } else if (timeOff['status']['denied']) {
                        statusLabel = '<small class="label label-danger">Declined</small>'
                    }

                    appendToToday += (
                        '<li class="box" id="' + liId + '">' +
                            '<div class="text-badge-container">' +
                                statusLabel +
                                '<span><strong>' + timeOff['name'] + '</strong><br>' + dateString + '</span>' +
                            '</div>' +
                            '<div class="buttons-container">' +
                                '<button type="button" class="btn btn-success time-off-approved">Approve</button>' +
                                '<button type="button" class="btn btn-danger time-off-declined">Decline</button>' +
                            '</div>' +
                        '</li>'
                    );

                    allTimeOffData[liId] = timeOff;

                })

                var appendToUpcoming = ''
                upcomingTimeOff.forEach(function(timeOff) {
                    var liId = (timeOff['name'] + timeOff['date']).replace(/\//g, '-').replace(/ /g, '-');

                    var date = moment(timeOff['date'], 'DD/MM/YYYY').toDate();
                    var dateString = moment(date).format('MMMM DD, YYYY');
                    var reason = timeOff['reason'];

                    console.log(reason);

                    var statusLabel = '';
                    if (timeOff['status']['pending']) {
                        statusLabel = '<small class="label label-warning">Pending</small>'
                    } else if (timeOff['status']['approved']) {
                        statusLabel = '<small class="label label-success">Approved</small>'
                    } else if (timeOff['status']['denied']) {
                        statusLabel = '<small class="label label-danger">Declined</small>'
                    }

                    appendToUpcoming += (
                        '<li class="box" id="' + liId + '">' +
                            '<div class="text-badge-container">' +
                                statusLabel +
                                '<span class="text-name"><strong>' + timeOff['name'] + '</strong></span><br><span class="text-date">' + dateString + '</span>' +
                            '</div>' +
                            '<div class="buttons-container">' +
                                '<button type="button" class="btn btn-success time-off-approved">Approve</button>' +
                                '<button type="button" class="btn btn-danger time-off-declined">Decline</button>' +
                            '</div>' +
                            '<div>' +
                                '<b>Reason</b>' +
                                '<p>' + reason + '</p>' +
                            '</div>' +
                        '</li>'
                    );

                    allTimeOffData[liId] = timeOff;

                })

                $('.time-off-loading-indicator').remove();

                $('#past-list').append(appendToPast);
                $('#today-list').append(appendToToday);
                $('#upcoming-list').append(appendToUpcoming);

                setClickHandlers();

            }
        })

    }

    // update a single time off request with ajax
    function ajaxUpdateAvailability(data) {
        $.ajax({
            url: "/hive/ajax/upcoming-time-off/",
            type: "POST",
            data: data,
            timeout: 15000,
            success: function(data) {
                var ogDateString = data['date'];
                var name = data['name'];
                var newStatus = data['new_status'];

                var liId = (name + ogDateString).replace(/\//g, '-').replace(/ /g, '-');

                var timeOffRequest = $('.nav-stacked').find('#' + liId);
                var label = timeOffRequest.find('.label');

                label.removeClass('label-warning');
                label.removeClass('label-danger');
                label.removeClass('label-success');

                if (newStatus['approved']) {
                    label.addClass('label-success');
                    label.text('Approved');
                } else if (newStatus['denied']) {
                    label.addClass('label-danger');
                    label.text('Denied');
                }

                timeOffRequest.find('.time-off-loading-indicator').remove();

                showAlert('Time off approval/declination successful.', true);
            },
            error: function(xhr, textStatus, errorThrown) {
                showAlert('Error: "' + textStatus + '"', false);

                var $listItems = $('.todo-list').children();
                $listItems.each(function(index, element) {
                    $element = $(this);

                    var loadingIndicator = $element.find('.time-off-loading-indicator');
                    if (loadingIndicator.length) {
                        loadingIndicator.remove();
                    }

                })

            },
            beforeSend: function(xhr, settings) {
                if (!this.crossDomain) {
                    xhr.setRequestHeader('X-CSRFToken', csrfToken);
                }
            }
        })
    }

    // call functions
    var currentDate = new Date();
    ajaxGetAllTimeOff(currentDate);

})