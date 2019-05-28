$(function() {

    // get CSRF token
    var csrfToken = $('input[name="csrfmiddlewaretoken"]').val();

    //needs model
    var needsModel = {
        'sunday': [
            "", // 0-1,   12:00 am (midnight) - 1:00 am       index:0
            "", // 1-2,   1:00 am - 2:00 am                   index:1
            "", // 2-3,   2:00 am - 3:00 am                   index:2
            "", // 3-4,   3:00 am - 4:00 am                   index:3
            "", // 4-5,   4:00 am - 5:00 am                   index:4
            "", // 5-6,   5:00 am - 6:00 am                   index:5
            "", // 6-7,   6:00 am - 7:00 am                   index:6
            "", // 7-8,   7:00 am - 8:00 am                   index:7
            "", // 8-9,   8:00 am - 9:00 am                   index:8
            "", // 9-10,  9:00 am - 10:00 am                  index:9
            "", // 10-11, 10:00 am - 11:00 am                 index:10
            "", // 11-12, 11:00 am - 12:00 pm                 index:11
            "", // 12-13, 12:00 pm (noon) - 1:00 pm           index:12
            "", // 13-14, 1:00 pm - 2:00 pm                   index:13
            "", // 14-15, 2:00 pm - 3:00 pm                   index:14
            "", // 15-16, 3:00 pm - 4:00 pm                   index:15
            "", // 16-17, 4:00 pm - 5:00 pm                   index:16
            "", // 17-18, 5:00 pm - 6:00 pm                   index:17
            "", // 18-19, 6:00 pm - 7:00 pm                   index:18
            "", // 19-20, 7:00 pm - 8:00 pm                   index:19
            "", // 20-21, 8:00 pm - 9:00 pm                   index:20
            "", // 21-22, 9:00 pm - 10:00 pm                   index:21
            "", // 22-23, 10:00 pm - 11:00 pm                  index:22
            ""  // 23-0,  11:00 pm - 12:00 pm (midnight)      index:23
        ],
        'monday': ["","","","","","","","","","","","","","","","","","","","","","","",""],
        'tuesday': ["","","","","","","","","","","","","","","","","","","","","","","",""],
        'wednesday': ["","","","","","","","","","","","","","","","","","","","","","","",""],
        'thursday': ["","","","","","","","","","","","","","","","","","","","","","","",""],
        'friday': ["","","","","","","","","","","","","","","","","","","","","","","",""],
        'saturday': ["","","","","","","","","","","","","","","","","","","","","","","",""],

        'sundayNoNeeds': false,
        'mondayNoNeeds': false,
        'tuesdayNoNeeds': false,
        'wednesdayNoNeeds': false,
        'thursdayNoNeeds': false,
        'fridayNoNeeds': false,
        'saturdayNoNeeds': false,

        'minShiftLength': "",
        'maxShiftLength': ""
    }

    // initialize each start time picker
    $('.timepicker-start').timepicker({
      defaultTime: '9:00 AM',
      minuteStep: 60,
      showInputs: false
    })
    // initialize each end time picker
    $('.timepicker-end').timepicker({
      defaultTime: '10:00 AM',
      minuteStep: 60,
      showInputs: false
    })

    // initialize each slider
    var $slider = $('.slider');
    $slider.bootstrapSlider();

    var $shiftSlider = $('.shift-slider');
    $shiftSlider.bootstrapSlider();

    // handle the slider value updating badge
    $slider.on('change', function(e) {
        var newValue = $(this).bootstrapSlider('getValue');
        var badge = $(this).parent().find('.number-needed');

        badge.text(newValue)

        if (newValue > 0) {
            badge.addClass('bg-green');
        } else {
            badge.removeClass('bg-green');
        }

        var currentDay = $(this).parent().parent().parent().attr('id');

        var startTimeString = $(this).parent().parent().find('.timepicker-start').val();
        var startTime = moment(startTimeString, 'hh:mm A'); //string to moment
        var startHour = moment(startTime).format('H'); //moment to string
        var hourInt = parseInt(startHour); // string to int

        needsModel[currentDay][hourInt] = newValue.toString();

    });

    // handle the SHIFT slider value updating badge
    $shiftSlider.on('change', function(e) {
        var newValues = $(this).bootstrapSlider('getValue');
        var newMinValue = newValues[0];
        var newMaxValue = newValues[1];

        var badges = $(this).parent().parent().find('.badges');
        var minBadge = badges.children('.min');
        var maxBadge = badges.children('.max');

        minBadge.text(newMinValue + ' hrs');
        maxBadge.text(newMaxValue + ' hrs');

        needsModel['minShiftLength'] = newMinValue.toString();
        needsModel['maxShiftLength'] = newMaxValue.toString();

    });

    // handle not open checkbox change
    $('.not-open-checkbox').on('change', function(e) {
        $this = $(this);

        var $tr = $this.parent().parent().parent().parent();

        var timeFields = $tr.find('.time-fields');
        var startField = timeFields.find('.timepicker-start');
        var endField = timeFields.find('.timepicker-end');

        var sliderContainer = $tr.find('.employee-slider-container');
        var slider = sliderContainer.find('input.slider');

        if (this.checked) {

            startField.prop('disabled', true);
            endField.prop('disabled', true);

            slider.bootstrapSlider('setValue', 0, false, true);
            slider.bootstrapSlider('disable');

            var dayName = $tr.attr('id');
            needsModel[dayName] = ["0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0"]

        } else {

            startField.prop('disabled', false);
            slider.bootstrapSlider('enable');

        }
    })

    // handle time change
    $('.timepicker-start').on('change', function(e) {
        $this = $(this);

        var startTime = moment($this.val(), 'hh:mm A');
        var endTime = moment(startTime).add(1, 'hours');

        var endTimeString = moment(endTime).format('h:mm A');
        var endPicker = $this.parent().parent().find('.timepicker-end');

        endPicker.val(endTimeString);

        // update the current day's slider and badge with the value from the model
        var startHour = moment(startTime).format('H');
        var hourInt = parseInt(startHour);
        var currentDay = $this.parent().parent().parent().parent();

        var currentValueString = needsModel[currentDay.attr('id')][hourInt];

        var slider = currentDay.find('input.slider');

        if (!currentValueString) {
            slider.bootstrapSlider('setValue', 0, false, true);
            return;
        }

        slider.bootstrapSlider('setValue', parseInt(currentValueString), false, true);


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
            $('#needs-box').append('<div class="overlay" id="needs-loading-indicator"><i class="fa fa-refresh fa-spin"></i></div>')
        } else {
            $('#needs-loading-indicator').remove()
        }

    }

    function refreshNeedsModel() {

        var dayNeeds = [needsModel['sunday'], needsModel['monday'], needsModel['tuesday'], needsModel['wednesday'],
                        needsModel['thursday'], needsModel['friday'], needsModel['saturday']];

        var intNeeds = []
        dayNeeds.forEach(function(dayNeed, index) {
            var currentNeed = dayNeed;
            currentNeed.forEach(function(hour, index) {
                this[index] = parseInt(hour);
            }, currentNeed)

            intNeeds.push(currentNeed);
        })

        var sunday = intNeeds[0];
        var monday = intNeeds[1];
        var tuesday = intNeeds[2];
        var wednesday = intNeeds[3];
        var thursday = intNeeds[4];
        var friday = intNeeds[5];
        var saturday = intNeeds[6];

        if (sunday.reduce((partialSum, a) => partialSum + a) == 0) {
            var $sundayDiv = $('#needs-box').find('#sunday');
            var $checkbox = $sundayDiv.find('.not-open-checkbox');
            $checkbox.prop('checked', true);
            $checkbox.trigger('change');
        }
        if (monday.reduce((partialSum, a) => partialSum + a) == 0) {
            var $sundayDiv = $('#needs-box').find('#monday');
            var $checkbox = $sundayDiv.find('.not-open-checkbox');
            $checkbox.prop('checked', true);
            $checkbox.trigger('change');
        }
        if (tuesday.reduce((partialSum, a) => partialSum + a) == 0) {
            var $sundayDiv = $('#needs-box').find('#tuesday');
            var $checkbox = $sundayDiv.find('.not-open-checkbox');
            $checkbox.prop('checked', true);
            $checkbox.trigger('change');
        }
        if (wednesday.reduce((partialSum, a) => partialSum + a) == 0) {
            var $sundayDiv = $('#needs-box').find('#wednesday');
            var $checkbox = $sundayDiv.find('.not-open-checkbox');
            $checkbox.prop('checked', true);
            $checkbox.trigger('change');
        }
        if (thursday.reduce((partialSum, a) => partialSum + a) == 0) {
            var $sundayDiv = $('#needs-box').find('#thursday');
            var $checkbox = $sundayDiv.find('.not-open-checkbox');
            $checkbox.prop('checked', true);
            $checkbox.trigger('change');
        }
        if (friday.reduce((partialSum, a) => partialSum + a) == 0) {
            var $sundayDiv = $('#needs-box').find('#friday');
            var $checkbox = $sundayDiv.find('.not-open-checkbox');
            $checkbox.prop('checked', true);
            $checkbox.trigger('change');
        }
        if (saturday.reduce((partialSum, a) => partialSum + a) == 0) {
            var $sundayDiv = $('#needs-box').find('#saturday');
            var $checkbox = $sundayDiv.find('.not-open-checkbox');
            $checkbox.prop('checked', true);
            $checkbox.trigger('change');
        }

        var minShiftLength = parseInt(needsModel['minShiftLength']);
        var maxShiftLength = parseInt(needsModel['maxShiftLength']);
        $shiftSlider.bootstrapSlider('setValue', [minShiftLength, maxShiftLength], false, true);

        $('.timepicker-start').trigger('change');
        toggleLoading(false);
    }

    // get needs with ajax
    function ajaxGetNeedsData() {
        $.ajax({
            url: "ajax/needs/",
            type: "GET",
            success: function(data) {

                var sunday = data['needs']['sunday'];
                var monday = data['needs']['monday'];
                var tuesday = data['needs']['tuesday'];
                var wednesday = data['needs']['wednesday'];
                var thursday = data['needs']['thursday'];
                var friday = data['needs']['friday'];
                var saturday = data['needs']['saturday'];

                var sundayNoNeeds = (sunday.reduce((partialSum, a) => partialSum + a) == 0) ? true : false;
                var mondayNoNeeds = (monday.reduce((partialSum, a) => partialSum + a) == 0) ? true : false;
                var tuesdayNoNeeds = (tuesday.reduce((partialSum, a) => partialSum + a) == 0) ? true : false;
                var wednesdayNoNeeds = (wednesday.reduce((partialSum, a) => partialSum + a) == 0) ? true : false;
                var thursdayNoNeeds = (thursday.reduce((partialSum, a) => partialSum + a) == 0) ? true : false;
                var fridayNoNeeds = (friday.reduce((partialSum, a) => partialSum + a) == 0) ? true : false;
                var saturdayNoNeeds = (saturday.reduce((partialSum, a) => partialSum + a) == 0) ? true : false;

                sunday.forEach(function(part, index) {
                    this[index] = part.toString();
                }, sunday)
                monday.forEach(function(part, index) {
                    this[index] = part.toString();
                }, monday)
                tuesday.forEach(function(part, index) {
                    this[index] = part.toString();
                }, tuesday)
                wednesday.forEach(function(part, index) {
                    this[index] = part.toString();
                }, wednesday)
                thursday.forEach(function(part, index) {
                    this[index] = part.toString();
                }, thursday)
                friday.forEach(function(part, index) {
                    this[index] = part.toString();
                }, friday)
                saturday.forEach(function(part, index) {
                    this[index] = part.toString();
                }, saturday)

                var minShiftLength = data['shiftLength']['min'];
                var maxShiftLength = data['shiftLength']['max'];

                var newNeedsModel = {
                    'sunday': sunday,
                    'monday': monday,
                    'tuesday': tuesday,
                    'wednesday': wednesday,
                    'thursday': thursday,
                    'friday': friday,
                    'saturday': saturday,

                    'sundayNoNeeds': sundayNoNeeds,
                    'mondayNoNeeds': mondayNoNeeds,
                    'tuesdayNoNeeds': tuesdayNoNeeds,
                    'wednesdayNoNeeds': wednesdayNoNeeds,
                    'thursdayNoNeeds': thursdayNoNeeds,
                    'fridayNoNeeds': fridayNoNeeds,
                    'saturdayNoNeeds': saturdayNoNeeds,

                    'minShiftLength': minShiftLength.toString(),
                    'maxShiftLength': maxShiftLength.toString()
                }

                needsModel = newNeedsModel;

                refreshNeedsModel();

                $('#needs-update-button').prop('disabled', false);

            }
        })

    }

//updating needs

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

    // when user clicks update button.
    $('#needs-update-button').on('click', function(e) {

        toggleLoading(true);

        var sunday = needsModel['sunday'];
        var monday = needsModel['monday'];
        var tuesday = needsModel['tuesday'];
        var wednesday = needsModel['wednesday'];
        var thursday = needsModel['thursday'];
        var friday = needsModel['friday'];
        var saturday = needsModel['saturday'];

        sunday.forEach(function(hour, index) {
                this[index] = parseInt(hour);
        }, sunday)
        monday.forEach(function(hour, index) {
                this[index] = parseInt(hour);
        }, monday)
        tuesday.forEach(function(hour, index) {
                this[index] = parseInt(hour);
        }, tuesday)
        wednesday.forEach(function(hour, index) {
                this[index] = parseInt(hour);
        }, wednesday)
        thursday.forEach(function(hour, index) {
                this[index] = parseInt(hour);
        }, thursday)
        friday.forEach(function(hour, index) {
                this[index] = parseInt(hour);
        }, friday)
        saturday.forEach(function(hour, index) {
                this[index] = parseInt(hour);
        }, saturday)

        var minShiftLength = parseInt(needsModel['minShiftLength']);
        var maxShiftLength = parseInt(needsModel['maxShiftLength']);

        var needs = {
            'needs': {
                'sunday': sunday,
                'monday': monday,
                'tuesday': tuesday,
                'wednesday': wednesday,
                'thursday': thursday,
                'friday': friday,
                'saturday': saturday
            },

            'shiftLength': {
                'min': minShiftLength,
                'max': maxShiftLength
            }
        };

        var needsString = JSON.stringify(needs);
        ajaxUpdateNeeds(needsString);

    })

    // update needs with ajax
    function ajaxUpdateNeeds(data) {
        $.ajax({
            url: "ajax/needs/",
            type: "POST",
            data: data,
            timeout: 15000,
            success: function(data) {
                toggleLoading(false);
                showAlert(data, true);
            },
            error: function(xhr, textStatus, errorThrown) {
                toggleLoading(false);
                showAlert('Error: "' + errorThrown + '"', false);
            },
            beforeSend: function(xhr, settings) {
                if (!this.crossDomain) {
                    xhr.setRequestHeader('X-CSRFToken', csrfToken);
                }
            }
        })
    }

    // call functions
    ajaxGetNeedsData();

})