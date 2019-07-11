$(function() {

    // get CSRF token
    var csrfToken = $('input[name="csrfmiddlewaretoken"]').val();

    // initialize each start time picker
    $('.timepicker-start').timepicker({
      defaultTime: '9:00 AM',
      minuteStep: 5,
      showInputs: false
    })
    // initialize each end time picker
    $('.timepicker-end').timepicker({
      defaultTime: '5:00 PM',
      minuteStep: 5,
      showInputs: false
    })

    // initialize each slider
    var $slider = $('.slider')
    $slider.bootstrapSlider()

    // change selected availability button
    $('.avail-btn').on('click', function(e) {
        $this = $(this);

        if (!$this.hasClass('selected-avail-btn')) {
            $this.addClass('selected-avail-btn');
            $this.siblings().removeClass('selected-avail-btn');

            var thisTD = $this.parent().parent();
            var thisTimeFields = thisTD.siblings('.time-fields');

            var startField = thisTimeFields.find('.timepicker-start');
            var endField = thisTimeFields.find('.timepicker-end');

            if ($this.text() == 'Time') {
                //show text inputs
                startField.prop('disabled', false);
                endField.prop('disabled', false);

            } else {
                //hide text inputs
                startField.prop('disabled', true);
                endField.prop('disabled', true);

            }

        }

    })

    // handle the slider values and respective badges
    $slider.on('change', function(e) {
        var newValues = $(this).bootstrapSlider('getValue');
        var newMinValue = newValues[0];
        var newMaxValue = newValues[1];

        var badges = $(this).parent().parent().find('.badges');
        var minBadge = badges.children('.min');
        var maxBadge = badges.children('.max');

        minBadge.text(newMinValue);
        maxBadge.text(newMaxValue);

    });

    // convert the decimal value of a time into a readable string time.
    function hourDoubleToTime(hourDouble) {

        var suffix;
        var newHour = Math.floor(hourDouble);

        if (newHour == 0) {
            newHour = 12;
            suffix = 'AM';
        } else if (newHour < 12) {
            //newHour = newHour;
            suffix = 'AM';
        } else if (newHour == 12) {
            //newHour = newHour;
            suffix = 'PM';
        } else {
            newHour = newHour - 12;
            suffix = 'PM';
        }

        var minute = Math.round((hourDouble - Math.floor(hourDouble)) * 60)
        var minuteString = '0';
        if (minute.toString().length == 1) {
            minuteString += minute;
        } else {
            minuteString = minute.toString();
        }

        var time = newHour + ':' + minuteString + ' ' + suffix;

        return time

    }

    // convert a readable string time into the decimal value of a time.
    function timeToHourDouble(timeString) {

        var timeSplit = timeString.split(' ');
        var hourMins = timeSplit[0].split(':');
        var suffix = timeSplit[1];

        var hour = parseInt(hourMins[0]);
        var minute = parseInt(hourMins[1]);

        var realMinute = minute / 60;

        if (suffix =='AM') {
            if (hour == 12) {
                hour = 0
            }
        } else if (suffix == 'PM') {
            if (hour != 12) {
                hour += 12
            }
        }

        var hourDouble = hour + realMinute;

        return hourDouble

    }

    // toggles the loading indicator on the availability box
    function toggleLoading(turnOn) {

        if (turnOn) {
            $('#avail-box').append('<div class="overlay" id="loading-indicator"><i class="fa fa-refresh fa-spin"></i></div>')
        } else {
            $('#loading-indicator').remove()
        }

    }

    // get availability with ajax
    function ajaxGetAvailabilityData() {
        $.ajax({
            url: "ajax/availability/",
            type: "GET",
            success: function(data) {
                sunday = data['sunday'];
                monday = data['monday'];
                tuesday = data['tuesday'];
                wednesday = data['wednesday'];
                thursday = data['thursday'];
                friday = data['friday'];
                saturday = data['saturday'];

                daysAvailability = {
                    'sunday': sunday,
                    'monday': monday,
                    'tuesday': tuesday,
                    'wednesday': wednesday,
                    'thursday': thursday,
                    'friday': friday,
                    'saturday': saturday,
                }

                $.each(daysAvailability, function(day, availability) {

                    var $buttonGroup = $('#' + day).find('.btn-group');

                    if (availability !== undefined) {
                        if (availability['is_open']) {

                            $buttonGroup.find('button[name="open"]').click();

                        } else if (availability['is_unavailable']) {

                            $buttonGroup.find('button[name="unavailable"]').click();

                        } else {

                            $buttonGroup.find('button[name="time"]').click();

                            var startDouble = availability['start'];
                            var endDouble = availability['end'];

                            var startTime = hourDoubleToTime(startDouble);
                            var endTime = hourDoubleToTime(endDouble);

                            var $timeFields = $('#' + day).find('.time-fields');
                            var $startField = $timeFields.find('.timepicker-start').val(startTime);
                            var $endField = $timeFields.find('.timepicker-end').val(endTime);

                        }
                    }

                })

                var hours = data['hours'];
                var shifts = data['shifts'];

                var minHours = 0;
                var maxHours = 0;
                var minShifts = 0;
                var maxShifts = 0;
                if (hours !== undefined) {
                    minHours = hours['min'];
                    maxHours = hours['max'];
                }
                if (shifts !== undefined) {
                    minShifts = shifts['min'];
                    maxShifts = shifts['max'];
                }

                $('#hours-slider').bootstrapSlider('setValue', [minHours, maxHours], false, true);
                $('#shifts-slider').bootstrapSlider('setValue', [minShifts, maxShifts], false, true);

                $('#availability-update-button').prop('disabled', false);

                $('#avail-loading-indicator').remove();

            }
        })

    }

//updating availability

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

        $('#avail-box').append(alertBox).delay(5000).queue(function(next) {
            $(this).find('.alert').slideUp(500);
            next();
        });

    }

    function getDayAvailability(day) {

        var $buttonGroup = $('#' + day).find('.btn-group');
        var selectedButton = $buttonGroup.find('.selected-avail-btn').text().toLowerCase();

        var dayAvailability = {}

        if (selectedButton == 'open') {

            dayAvailability = {
                'isOpen': true,
                'isUnavailable': false,
                'start': 0,
                'end': 0
            };

        } else if (selectedButton == 'unavailable') {

            dayAvailability = {
                'isOpen': false,
                'isUnavailable': true,
                'start': 0,
                'end': 0
            };

        } else if (selectedButton == 'time') {

            var thisTD = $buttonGroup.parent();
            var thisTimeFields = thisTD.siblings('.time-fields');

            var startField = thisTimeFields.find('.timepicker-start');
            var endField = thisTimeFields.find('.timepicker-end');

            var startTime = startField.val();
            var endTime = endField.val();

            var startDouble = timeToHourDouble(startTime);
            var endDouble = timeToHourDouble(endTime);

            dayAvailability = {
                'isOpen': false,
                'isUnavailable': false,
                'start': startDouble,
                'end': endDouble
            };

        }

        return dayAvailability;

    }

    // when user clicks update button.
    $('#availability-update-button').on('click', function(e) {

        toggleLoading(true);

        var sunday = getDayAvailability('sunday');
        var monday = getDayAvailability('monday');
        var tuesday = getDayAvailability('tuesday');
        var wednesday = getDayAvailability('wednesday');
        var thursday = getDayAvailability('thursday');
        var friday = getDayAvailability('friday');
        var saturday = getDayAvailability('saturday');

        var hoursValues = $('#hours-slider').bootstrapSlider('getValue');
        var shiftsValues = $('#shifts-slider').bootstrapSlider('getValue');

        var minHours = hoursValues[0];
        var maxHours = hoursValues[1];
        var minShifts = shiftsValues[0];
        var maxShifts = shiftsValues[1];

        availability = {
            'sunday': sunday,
            'monday': monday,
            'tuesday': tuesday,
            'wednesday': wednesday,
            'thursday': thursday,
            'friday': friday,
            'saturday': saturday,

            'hours': {
                'min': minHours,
                'max': maxHours
            },
            'shifts': {
                'min': minShifts,
                'max': maxShifts
            }
        }

        var availabilityString = JSON.stringify(availability);
        ajaxUpdateAvailability(availabilityString);

    })

    // update availability with ajax
    function ajaxUpdateAvailability(data) {
        $.ajax({
            url: "ajax/availability/",
            type: "POST",
            data: data,
            timeout: 15000,
            success: function(data) {
                toggleLoading(false);
                showAlert(data, true);
            },
            error: function(xhr, textStatus, errorThrown) {
                toggleLoading(false);
                showAlert('Error: "' + textStatus + '"', false);
            },
            beforeSend: function(xhr, settings) {
                if (!this.crossDomain) {
                    xhr.setRequestHeader('X-CSRFToken', csrfToken);
                }
            }
        })
    }

    // call functions
    ajaxGetAvailabilityData();

})