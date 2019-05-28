$(function() {

    // get CSRF token
    var csrfToken = $('input[name="csrfmiddlewaretoken"]').val();

    // show error or success box for post requests.
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

        $('#time-off-box').append(alertBox).delay(5000).queue(function(next) {
            $(this).find('.alert').slideUp(500);
            next();
        });

    }

    // once approve and decline buttons appear, add on click handlers.
    function setClickHandlers(nameKey) {
        $('.time-off-approved').on('click', function(e) {
            $this = $(this);

            var $li = $this.parent().parent();

            $li.append('<div class="overlay" id="time-off-loading-indicator"><i class="fa fa-refresh fa-spin"></i></div>');

            var text = $li.find('.text').text().split('|');
            var name = text[0].trim();
            var ogDateString = text[1].trim();

            var date = moment(ogDateString, 'MMMM DD, YYYY').toDate();
            var dateString = moment(date).format('DD/MM/YYYY');

            var email = nameKey[name];

            var status = {
                'pending': false,
                'approved': true,
                'denied': false,
                'expired': false
            }

            var timeOffData = {
                'email': email,
                'fullName': name,
                'date': dateString,
                'status': status,
            }

            var timeOffDataString = JSON.stringify(timeOffData);
            ajaxUpdateAvailability(timeOffDataString);

        })

        $('.time-off-declined').on('click', function(e) {
            $this = $(this);

            var $li = $this.parent().parent();

            $li.append('<div class="overlay" id="time-off-loading-indicator"><i class="fa fa-refresh fa-spin"></i></div>');

            var text = $li.find('.text').text().split('|');
            var name = text[0].trim();
            var ogDateString = text[1].trim();

            var date = moment(ogDateString, 'MMMM DD, YYYY').toDate();
            var dateString = moment(date).format('DD/MM/YYYY');

            var email = nameKey[name];

            var status = {
                'pending': false,
                'approved': false,
                'denied': true,
                'expired': false
            }

            var timeOffData = {
                'email': email,
                'fullName': name,
                'date': dateString,
                'status': status,
            }

            var timeOffDataString = JSON.stringify(timeOffData);
            ajaxUpdateAvailability(timeOffDataString);
        })
    }

    // get pending and approved time off requests within the next 3 weeks with ajax
    function ajaxGetUpcomingTimeOff(date) {
        var dateString = moment(date).format('DD-MM-YYYY');

        $.ajax({
            url: "ajax/upcoming-time-off/" + dateString + "/",
            type: "GET",
            success: function(data) {
                var nameKey = data['name_key'][0];
                delete data['name_key'];

                var time_off_dicts = [];
                $.each(data, function(dateString, timeOffList) {
                    var date = moment(dateString, 'DD/MM/YYYY').toDate();

                    timeOffList.forEach(function(time_off_item) {
                        time_off_item['date'] = date;
                        time_off_dicts.push(time_off_item);
                    })
                })

                time_off_dicts.sort(function(a, b) {
                    return a['date'] > b['date'];
                })

                var htmlToAppend = ''
                time_off_dicts.forEach(function(time_off_dict) {

                    var dateString = moment(time_off_dict['date']).format('MMMM DD, YYYY');

                    if (time_off_dict['status']['pending']) {
                        var liId = (time_off_dict['name'] + dateString).replace(/ /g, '-').replace(',', '');
                        var html = (
                            '<li class="box" id="' + liId + '">' +
                                '<span class="text">' + time_off_dict['name'] + ' | ' + dateString + '</span>' +
                                '<small class="label label-warning">Pending</small>' +
                                '<div style="float: right">' +
                                    '<button type="button" class="btn btn-success time-off-approved">Approve</button>' +
                                    '<button type="button" class="btn btn-danger time-off-declined">Decline</button>' +
                                '</div>' +
                            '</li>'
                        );
                    } else {
                        var html = (
                            '<li>' +
                                '<span class="text">' + time_off_dict['name'] + ' | ' + dateString + '</span>' +
                                '<small class="label label-success">Approved</small>' +
                                '<div style="float: right">' +
                                '</div>' +
                            '</li>'
                        );
                    }

                    htmlToAppend += html;

                })

                $('#time-off-loading-indicator').remove();
                $('.todo-list').append(htmlToAppend);
                setClickHandlers(nameKey);

            },
            error: function(xhr, textStatus, errorThrown) {
                $('#time-off-loading-indicator').remove();
            }
        })

    }

    // update a single time off request with ajax
    function ajaxUpdateAvailability(data) {
        $.ajax({
            url: "ajax/upcoming-time-off/",
            type: "POST",
            data: data,
            timeout: 15000,
            success: function(data) {
                console.log(data);
                var ogDateString = data['date'];
                var name = data['name'];
                var newStatus = data['new_status'];

                var date = moment(ogDateString, 'DD/MM/YYYY').toDate();
                var dateString = moment(date).format('MMMM DD, YYYY');

                var liId = (name + dateString).replace(/ /g, '-').replace(',', '');

                var timeOffRequest = $('.todo-list').find('#' + liId);
                var label = timeOffRequest.find('.label');

                label.removeClass('label-warning');

                if (newStatus['approved']) {
                    label.addClass('label-success');
                    label.text('Approved');
                } else if (newStatus['denied']) {
                    label.addClass('label-danger');
                    label.text('Denied');
                }

                timeOffRequest.find('div').empty();
                timeOffRequest.find('#time-off-loading-indicator').remove();

                showAlert('Time off approval/declination successful.', true);
            },
            error: function(xhr, textStatus, errorThrown) {
                showAlert('Error: "' + textStatus + '"', false);

                var $listItems = $('.todo-list').children();
                console.log('a', $listItems);
                $listItems.each(function(index, element) {
                    $element = $(this);

                    console.log('c', $element);

                    var loadingIndicator = $element.find('#time-off-loading-indicator');
                    console.log('d', loadingIndicator);
                    if (loadingIndicator.length) {
                        console.log('e', loadingIndicator);
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
    ajaxGetUpcomingTimeOff(currentDate);

})