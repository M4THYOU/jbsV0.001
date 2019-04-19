$(function() {

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

    $('#availability-update-button').on('click', function(e) {
        console.log('eee');
    })

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

                })

                var hours = data['hours'];
                var shifts = data['shifts'];

                var minHours = hours['min'];
                var maxHours = hours['max'];
                var minShifts = shifts['min'];
                var maxShifts = shifts['max'];

                $('#hours-slider').bootstrapSlider('setValue', [minHours, maxHours], false, true);
                $('#shifts-slider').bootstrapSlider('setValue', [minShifts, maxShifts], false, true);

                $('#availability-update-button').prop('disabled', false);

            }
        })

    }

    // update availability with ajax
    function ajaxUpdateAvailability() {
        $.ajax({
            url: "ajax/availability/",
            type: "POST",
            success: function(data) {
                console.log('x')
            }
        })
    }

    // call functions
    ajaxGetAvailabilityData();

})