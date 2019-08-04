$(function() {

    // get CSRF token
    var csrfToken = $('input[name="csrfmiddlewaretoken"]').val();

    function init_events(ele) {
      ele.each(function () {

        // create an Event Object (http://arshaw.com/fullcalendar/docs/event_data/Event_Object/)
        // it doesn't need to have a start or end
        var eventObject = {
          title: $.trim($(this).text()) // use the element's text as the event title
        }

        // store the Event Object in the DOM element so we can get to it later
        $(this).data('eventObject', eventObject)

        // make the event draggable using jQuery UI
        $(this).draggable({
          zIndex        : 1070,
          revert        : true, // will cause the event to go back to its
          revertDuration: 0  //  original position after the drag
        })

      })
    }

    init_events($('#external-events div.external-event'))

    /* initialize the calendar
     -----------------------------------------------------------------*/
    //Date for the calendar events (dummy data)
    var currentDate = new Date()
    var startDate = new Date(2020, 0, 1);
    var endDate = new Date(2020, 0, 0);
    $('#calendar').fullCalendar({
      dragRevertDuration: 0,
      validRange: {
        start: startDate,
        end: endDate
      },
      header: {
        left  : '',
        center: 'title',
        right : ''
      },
      buttonText: {
        today: 'today',
        month: 'month',
        week : 'week',
        day  : 'day'
      },
      editable  : true,
      eventDurationEditable: false,
      droppable : true, // this allows things to be dropped onto the calendar !!!
      defaultDate: new Date(2020, 0, 1),
      drop      : function (currentDate, allDay) { // this function is called when something is dropped

        $('#modal-user-selector').modal('show');
        newShift = $(this);
        newShift_currentDate = currentDate;
        newShift_allDay = allDay;

        var dateString = moment(currentDate).format('DD/MM/YYYY');
        mixpanel.track('DEMO | New shift dropped', {'dateString': dateString});

      },
      viewRender: function(view, element) {
        addAutoScheduleButton();
      },
      eventRender: function(event, element) {
        // Append name and position to the event.
        element.find('.fc-title').append('<br/>' + event.description);

        // Add tooltip to the event
        element.attr('title', event.tooltip);
      },
      eventDragStart: function(event, element) {
        fcEventMoving = true;
      },
      eventDragStop: function(event, element) {
        fcEventMoving = false;

        var trash = $('#trash-container');
        var offset = trash.offset();

        var x1 = offset.left;
        var x2 = offset.left + trash.outerWidth(true);
        var y1 = offset.top;
        var y2 = offset.top + trash.outerHeight(true);

        if (element.pageX >= x1 && element.pageX <= x2 &&
            element.pageY >= y1 && element.pageY <= y2) {

            $('#calendar').fullCalendar('removeEvents', [event._id])

            mixpanel.track('DEMO | Shift deleted');

        }

        if (trash.hasClass('hovered-trash')) {
          trash.removeClass('hovered-trash');
        }

      }
    })

    /* ADDING EVENTS */
    var currColor = '#3c8dbc' //Red by default
    //Color chooser button
    var colorChooser = $('#color-chooser-btn')
    $('#color-chooser > li > a').click(function (e) {
      e.preventDefault()
      //Save color
      currColor = $(this).css('color')
      //Add color effect to button
      $('#add-new-event').css({ 'background-color': currColor, 'border-color': currColor })
    })
    $('#add-new-event').click(function (e) {
      e.preventDefault();
      //Get value and make sure it is not null

      var startTimeString = $('#timepicker-start').val();
      var endTimeString = $('#timepicker-end').val();
      if (startTimeString.length == 0 || endTimeString.length == 0) {
        return;
      }

      var fullTimeString = startTimeString + " - " + endTimeString;

      mixpanel.track('DEMO | Add saved shift Button Click', {'timeString': fullTimeString});

      var doReturn = false;
      $('#external-events').children('.external-event').each(function(i, x) {
        if ($(this).text() == fullTimeString) {
            doReturn = true;
            return false;
        }
      })

      if (doReturn) {
        return;
      }

      //Create events
      var event = $('<div />');
      event.css({
        'background-color': currColor,
        'border-color'    : currColor,
        'color'           : '#fff'
      }).addClass('external-event')
      event.html(fullTimeString);
      $('#external-events').append(event);

      //Add draggable funtionality
      init_events(event);

    })

/* XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX */

    // get CSRF token
    var csrfToken = $('input[name="csrfmiddlewaretoken"]').val();

    var emailNameKey;
    var nameEmailKey;
    var newShift;
    var newShift_allDay;
    var newShift_currentDate;

    var fcEventMoving = false;

    // show error or success box for post requests.
    function showAlert(bodyText, isSuccess, boxId) {

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

        $('#' + boxId).append(alertBox).delay(5000).queue(function(next) {
            $(this).find('.alert').slideUp(500);
            next();
        });

    }

    // initialize start time picker
    $('#timepicker-start').timepicker({
      defaultTime: '9:00 AM',
      minuteStep: 5,
      showInputs: false
    })
    // initialize end time picker
    $('#timepicker-end').timepicker({
      defaultTime: '5:00 PM',
      minuteStep: 5,
      showInputs: false
    })

    $(document).mousemove(function(e) {
        if (fcEventMoving) {

            var trash = $('#trash-container');
            var offset = trash.offset();

            var x1 = offset.left;
            var x2 = offset.left + trash.outerWidth(true);
            var y1 = offset.top;
            var y2 = offset.top + trash.outerHeight(true);

            if (e.pageX >= x1 && e.pageX <= x2 &&
                e.pageY >= y1 && e.pageY <= y2) {

                if (!trash.hasClass('hovered-trash')) {
                    trash.addClass('hovered-trash');
                }

            } else {
                if (trash.hasClass('hovered-trash')) {
                    trash.removeClass('hovered-trash');
                }
            }

        }
    })

    $('#add-shift-button').on('click', function(e) {

        var name = $('#employee-select').val();
        var position = $('#employee-position').val().trim();

        if (position == "" || name == null) {
            return;
        }

        var dateString = moment(newShift_currentDate).format('DD/MM/YYYY');
        mixpanel.track('DEMO | New shift add Button Click', {'dateString': dateString});

        $('#modal-user-selector').modal('hide');

        // retrieve the dropped element's stored Event Object
        var originalEventObject = newShift.data('eventObject')
        // we need to copy it, so that multiple events don't have a reference to the same object
        var copiedEventObject = $.extend({}, originalEventObject)

        // assign it the date that was reported
        copiedEventObject.start           = newShift_currentDate;
        copiedEventObject.allDay          = newShift_allDay;
        copiedEventObject.backgroundColor = newShift.css('background-color');
        copiedEventObject.borderColor     = newShift.css('border-color');
        copiedEventObject.description     = name + '<br/>' + position;
        copiedEventObject.tooltip         = name + ' | ' + position;

        // render the event on the calendar
        // the last `true` argument determines if the event "sticks" (http://arshaw.com/fullcalendar/docs/event_rendering/renderEvent/)
        $('#calendar').fullCalendar('renderEvent', copiedEventObject, true);

        $('#employee-position').val('');

    })

    // set the list of users in modal
    function setUserList(emailNameKey) {
        $.each(emailNameKey, function(email, name) {
            var newSelectElement = '<option>' + name + '</option>';
            $('#employee-select').append(newSelectElement);
        })

        $('#add-shift-button').prop('disabled', false);
    }

    // initialize trash can droppable
    $('#trash-container').droppable({
        classes: {
            'ui-droppable-hover': 'hovered-trash',
        },
        drop: function(event, ui) {
            $(ui.draggable).remove();
        },
    })

    function addNewShift(date, name, position, timeString) {
        var event = {
            title: timeString,
            start: date,
            allDay: true,
            description: name + '<br/>' + position,
            tooltip: name + ' | ' + position
        };

        $('#calendar').fullCalendar('renderEvent', event, true);

    }

    $('#saved-shifts-save-button').on('click', function(e) {

        $('#saved-shifts-box').append('<div class="overlay" id="saved-shifts-loading-indicator"><i class="fa fa-refresh fa-spin"></i></div>')

        mixpanel.track('DEMO | Save shifts Button Click');

        setTimeout(function() {
            $('#saved-shifts-loading-indicator').remove();
            showAlert('Saved shifts successfully updated.', true, 'saved-shifts-box')
        }, 1000);

    })

    $('#save-schedule-button').on('click', function(e) {

        $('#calendar-box').append('<div class="overlay" id="calendar-loading-indicator"><i class="fa fa-refresh fa-spin"></i></div>');

        mixpanel.track('DEMO | Save schedule Button Click');

        setTimeout(function() {
            $('#calendar-loading-indicator').remove();
            $('#modal-demo-done').modal('show');
        }, 1000);

    })

//////////////////////////////////////////////////////////////////
    $emailField = $('#email');

    function validateEmail(email) {
        var re = /\S+@\S+\.\S+/;
        return re.test(email);
    }

    function validateEmailField(email) {
        var isValid = true;

        if (email == "") {
            isValid = false;
            $emailField.css('border-color', 'red');
        } else if (!validateEmail(email)) {
            isValid = false;
            $emailField.css('border-color', 'red');
        } else {
            $emailField.css('border-color', '');
        }

        // I am not checking whether it is a valid email or not. Business decision. Let them give us whatever data they want.
        return isValid;

    }

    $emailField.on('input', function(e) {
        validateEmailField($emailField.val().trim());
    })

    $('#demo-button').on('click', function(e) {
        emailText = $emailField.val().trim();

        isValid = validateEmailField(emailText);

        if (isValid) {
            postEmail(emailText);
            mixpanel.track('DEMO | Valid demo complete submit email Button Click', {'email': emailText});
        } else {
            mixpanel.track('DEMO | Invalid demo complete submit email Button Click', {'email': emailText});
        }
    })

    function toggleLoading(isNowLoading) {

        if (isNowLoading) {
            $('#modal-demo-done').append('<div class="overlay" id="email-submit-loading-indicator"><i class="fa fa-refresh fa-spin"></i></div>');
            $emailField.prop('disabled', true);
            $('#demo-button').prop('disabled', true);
        } else {
            $('#email-submit-loading-indicator').remove();
            $emailField.prop('disabled', false);
            $('#demo-button').prop('disabled', false);
        }

    }

    function showEmailSuccess(message) {
        formContainer = $('#email-submit-body');
        //formContainer.css('display', 'inline-block');
        formContainer.html('<h4 id="modal-subtitle"><b>' + message + '</b></h4>');
    }

    // update availability with ajax
    function postEmail(email) {
        toggleLoading(true);

        $.ajax({
            url: "/ajax/submit-email/",
            type: "POST",
            data: {'email': email},
            timeout: 15000,
            success: function(data) {
                toggleLoading(false);
                var message = data + ' <a href="/about-hive/" id="learn-more">Learn More</a>'
                showEmailSuccess(message);
                createOnClick();
            },
            error: function(xhr, textStatus, errorThrown) {
                toggleLoading(false);
            },
            beforeSend: function(xhr, settings) {
                if (!this.crossDomain) {
                    xhr.setRequestHeader('X-CSRFToken', csrfToken);
                }
            }
        })
    }
//////////////////////////////////////////////////////////////////

    // get schedule with ajax
    function ajaxGetUserList() {
        $.ajax({
            url: "/hive/ajax/demo/users/",
            type: "GET",
            success: function(data) {
                emailNameKey = data['email_name_key'];
                nameEmailKey = data['name_email_key'];
                setUserList(emailNameKey);

                $('#calendar-loading-indicator').remove();

            }
        })

    }

    function ajaxGetCurrentSavedShifts() {
        $.ajax({
            url: "/hive/ajax/demo/shifts/",
            type: "GET",
            success: function(data) {
                var shiftsList = data['shifts'];

                var allNewShifts = ''
                $.each(shiftsList, function(i, shiftDict) {
                    var classes = shiftDict['class'];

                    var backgroundColor = shiftDict['backgroundColor'];
                    var borderColor = shiftDict['borderColor'];
                    var color = shiftDict['color'];
                    var position = shiftDict['position'];

                    var timeString = shiftDict['time'];

                    //Create events
                    var event = $('<div />');
                    event.css({
                      'background-color': backgroundColor,
                      'border-color'    : borderColor,
                      'color'           : '#fff'
                    }).addClass('external-event')
                    event.html(timeString);
                    $('#external-events').append(event);

                    //Add draggable funtionality
                    init_events(event);

                })

                var eventContainer = $('#saved-shifts-box').find('#external-events');
                eventContainer.append(allNewShifts);
                $('.external-event').draggable({
                    zIndex        : 1070,
                    revert        : true, // will cause the event to go back to its
                    revertDuration: 0  //  original position after the drag
                });

                $('#saved-shifts-save-button').prop('disabled', false);
                $('#add-new-event').prop('disabled', false);
                $('#saved-shifts-loading-indicator').remove();

            }
        })
    }

    // get schedule with ajax
    function ajaxGetAutoSchedule(dateList) {
        $.ajax({
            url: "/hive/ajax/demo/schedule/",
            type: "GET",
            success: function(data) {
                var exactTimes = data['exactTimes'];
                var positions = data['positions'];

                dateList.forEach(function(dateString, index) {
                    var currentExactTimes = exactTimes[dateString];
                    var currentPositions = positions[dateString];

                    $.each(emailNameKey, function(email, name) {
                        if (email in currentExactTimes) {
                            var timeString = currentExactTimes[email].toUpperCase();
                            var position = currentPositions[email];
                            var date = moment(dateString, 'DD/MM/YYYY').toDate()

                            addNewShift(date, name, position, timeString);
                        }
                    })
                })

                $('#calendar-loading-indicator').remove();

            }
        })

    }

    ajaxGetUserList()
    ajaxGetCurrentSavedShifts();

/* XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX */

    function addAutoScheduleButton() {
        var calRows = $('.fc-day-grid');

        calRows.children().each(function(i, element) {
            var rowContent = $(this).find('.fc-content-skeleton');
            var rowHeaders = rowContent.find('thead');
            var dateRow = rowHeaders.find('tr');

            var firstOfRowDate = dateRow.children().first().data('date');
            var lastOfRowDisabled = dateRow.children().last().hasClass('fc-disabled-day');

            var startRowDate = moment(firstOfRowDate, 'YYYY-MM-DD');
            var startOfWeek = moment().startOf('week');
            if (startRowDate >= startOfWeek && !lastOfRowDisabled) {
                $(this).prepend('<button class="auto-button">Auto</button>');
            }

        })

    }

    $('.auto-button').on('click', function(e) {
        $('#calendar-box').append('<div class="overlay" id="calendar-loading-indicator"><i class="fa fa-refresh fa-spin"></i></div>');

        var $this = $(this);

        var rowContent = $this.siblings('.fc-content-skeleton');
        var rowHeaders = rowContent.find('thead');
        var dateRow = rowHeaders.find('tr');

        var weekDays = [];
        dateRow.children().each(function(i, element) {
            var currentDateMoment = moment($(this).data('date'), 'YYYY-MM-DD');
            var formattedDateString = moment(currentDateMoment).format('DD/MM/YYYY');
            weekDays.push(formattedDateString);
        })

        $('#calendar').fullCalendar('removeEvents', function(e) {
            var eventDate = e.start.add(1, 'd').toDate();
            var eventDateString = moment(eventDate).format('DD/MM/YYYY');

            if (weekDays.includes(eventDateString)) {
                return true;
            } else {
                return false;
            }
        })

        ajaxGetAutoSchedule(weekDays);

        mixpanel.track('DEMO | AI Button Click');

    })

// Metric Tracking with MixPanel ///////////////////////////////////////////////////////////////////////////////////////

    function createOnClick() {
        $('#learn-more').on('click', function() {
            mixpanel.track('DEMO | Demo complete learn more Button Click');
        })
    }

})