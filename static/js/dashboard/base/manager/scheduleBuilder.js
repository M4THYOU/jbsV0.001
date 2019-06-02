$(function() {

    // TODO
    // - Save current schedule.

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
    var startDate = new Date(currentDate.getFullYear(), currentDate.getMonth() - 1, 1);
    var endDate = new Date(currentDate.getFullYear(), currentDate.getMonth() + 2, 0);
    $('#calendar').fullCalendar({
      dragRevertDuration: 0,
      validRange: {
        start: startDate,
        end: endDate
      },
      header    : {
        left  : 'prev,next today',
        center: 'title',
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
      drop      : function (currentDate, allDay) { // this function is called when something is dropped

        $('#modal-user-selector').modal('show');
        newShift = $(this);
        newShift_currentDate = currentDate;
        newShift_allDay = allDay;

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

        $('#modal-user-selector').modal('hide');

        // retrieve the dropped element's stored Event Object
        var originalEventObject = newShift.data('eventObject')
        console.log(originalEventObject);
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

        var savedShifts = $('#saved-shifts').find('#external-events');

        var shiftsDict = {};
        savedShifts.children().each(function(i, element) {
            var classes = element.className;

            var backgroundColor = element.style.backgroundColor;
            var borderColor = element.style.borderColor;
            var color = element.style.color;
            var position = element.style.position;

            var timeString = element.textContent;

            var elementDict = {
                'class': classes,

                'backgroundColor': backgroundColor,
                'borderColor': borderColor,
                'color': color,
                'position': position,

                'time': timeString
            }

            shiftsDict[i] = elementDict;
        })

        var shiftsDictString = JSON.stringify(shiftsDict);

        ajaxUpdateCurrentSavedShifts(shiftsDictString);

    })

    $('#save-schedule-button').on('click', function(e) {

        $('#calendar-box').append('<div class="overlay" id="calendar-loading-indicator"><i class="fa fa-refresh fa-spin"></i></div>');

        var events = $('#calendar').fullCalendar('clientEvents');

        var exactTimes = {};
        var positions = {};
        $.each(events, function(i, event) {
            var dateString = event.start.format('DD/MM/YYYY');
            var timeString = event.title.toLowerCase();

            var tooltip = event.tooltip.split(' | ');
            var email = nameEmailKey[tooltip[0]];
            var position = tooltip[1];

            if (exactTimes[dateString] == null) {
                exactTimes[dateString] = {[email]: timeString};
            } else {
                exactTimes[dateString][email] = timeString;
            }

            if (positions[dateString] == null) {
                positions[dateString] = {[email]: position};
            } else {
                positions[dateString][email] = position;
            }

        })

        var scheduleDict = {
            'exactTimes': exactTimes,
            'positions': positions
        }

        var scheduleDictString = JSON.stringify(scheduleDict);
        ajaxUpdateFullSchedule(scheduleDictString);

    })

    // get schedule with ajax
    function ajaxGetFullSchedule(startDate, endDate) {
        var startDateString = moment(startDate).format('DD-MM-YYYY');
        var endDateString = moment(endDate).format('DD-MM-YYYY');
        $.ajax({
            url: "/hive/ajax/full-schedule/" + startDateString + "/" + endDateString + "/",
            type: "GET",
            success: function(data) {
                emailNameKey = data['email_name_key'];
                nameEmailKey = data['name_email_key'];
                setUserList(emailNameKey);

                var exactTimes = data['exact_times'];
                var positions = data['positions'];

                $.each(exactTimes, function(dateString, workingUsersDict) {
                    $.each(emailNameKey, function(email, name) {
                        if (email in workingUsersDict) {

                            var timeString = workingUsersDict[email].toUpperCase();
                            var position = positions[dateString][email];
                            var name = emailNameKey[email];
                            var date = moment(dateString, 'DD/MM/YYYY').toDate();

                            addNewShift(date, name, position, timeString);

                        }
                    })
                })

                $('#calendar-loading-indicator').remove();

            }
        })

    }

    function ajaxUpdateFullSchedule(data) {
        $.ajax({
            url: "/hive/ajax/full-schedule/",
            type: "POST",
            timeout: 15000,
            data: data,
            success: function(data) {
                console.log(data);
                $('#calendar-loading-indicator').remove();
                showAlert(data, true, 'calendar-box')
            },
            error: function(xhr, textStatus, errorThrown) {
                console.log(errorThrown);
                $('#calendar-loading-indicator').remove();
                showAlert('Error: "' + textStatus + '"', false, 'calendar-box');
            },
            beforeSend: function(xhr, settings) {
                if (!this.crossDomain) {
                    xhr.setRequestHeader('X-CSRFToken', csrfToken);
                }
            }
        })
    }

    function ajaxGetCurrentSavedShifts() {
        $.ajax({
            url: "/hive/ajax/saved-shifts/",
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

    function ajaxUpdateCurrentSavedShifts(data) {
        $.ajax({
            url: "/hive/ajax/saved-shifts/",
            type: "POST",
            timeout: 15000,
            data: data,
            success: function(data) {
                $('#saved-shifts-loading-indicator').remove();
                showAlert(data, true, 'saved-shifts-box')
            },
            error: function(xhr, textStatus, errorThrown) {
                $('#saved-shifts-loading-indicator').remove();
                showAlert('Error: "' + textStatus + '"', false, 'saved-shifts-box');
            },
            beforeSend: function(xhr, settings) {
                if (!this.crossDomain) {
                    xhr.setRequestHeader('X-CSRFToken', csrfToken);
                }
            }
        })
    }

    ajaxGetFullSchedule(startDate, endDate);
    ajaxGetCurrentSavedShifts();

})