$(function() {

    var momentToday = moment().startOf('day')

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

        if (currentDate < momentToday) {
            return;
        }

        $('#modal-user-selector').modal('show');
        newShift = $(this);
        newShift_currentDate = currentDate;
        newShift_allDay = allDay;

      },
      eventDrop: function(data, b, revertFunc) {

        function checkDoubleTrue(value) {
            return value;
        }

        var doubleTrue = [];
        $('#calendar').fullCalendar('clientEvents', function(event) {
            if (event.start.isSame(data.start, 'day')) {
                doubleTrue.push(true);
            }
        })

        if (doubleTrue.every(checkDoubleTrue) && doubleTrue.length > 1) {
            revertFunc();
        }

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

      },
      eventConstraint: {
        start: momentToday,
        end: endDate
      }
    })

/* XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX */

    // get CSRF token
    var csrfToken = $('input[name="csrfmiddlewaretoken"]').val();

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

    $('#add-time-off-button').on('click', function(e) {

        var reason = $('#reason-field').val().trim();

        if (reason == "") {
            return;
        }

        $('#modal-user-selector').modal('hide');

        var returnEarly = false;
        $('#calendar').fullCalendar('clientEvents', function(event) {
            if (event.start.isSame(newShift_currentDate, 'day')) {
                returnEarly = true;
            }
        })

        if (returnEarly) {
            return;
        }

        // retrieve the dropped element's stored Event Object
        var originalEventObject = newShift.data('eventObject')
        // we need to copy it, so that multiple events don't have a reference to the same object
        var copiedEventObject = $.extend({}, originalEventObject)

        // assign it the date that was reported
        copiedEventObject.start           = newShift_currentDate;
        copiedEventObject.allDay          = newShift_allDay;
        copiedEventObject.backgroundColor = newShift.css('background-color');
        copiedEventObject.borderColor     = newShift.css('border-color');
        copiedEventObject.description     = 'Pending';
        copiedEventObject.tooltip         = reason;
        copiedEventObject.isTimeOff       = true;
        copiedEventObject.statusDict      = {'approved': false, 'denied': false, 'expired': false, 'pending': true};

        // render the event on the calendar
        // the last `true` argument determines if the event "sticks" (http://arshaw.com/fullcalendar/docs/event_rendering/renderEvent/)
        $('#calendar').fullCalendar('renderEvent', copiedEventObject, true);

        $('#reason-field').val('');

    })

    function addNewShift(date, position, timeString) {
        var event = {
            title: timeString,
            start: date,
            allDay: true,
            editable: false,
            description: position,
            tooltip: position,
            isTimeOff: false
        };

        $('#calendar').fullCalendar('renderEvent', event, true);

    }

    function addNewTimeOff(date, reason, status) {
        // isEditable if date > today...
        var red = '#dd4b39';
        var yellow = '#f39c12';
        var green = '#00a65a';

        var backgroundColor = red;
        var statusString = 'Denied'
        if (status['pending']) {
            backgroundColor = yellow;
            statusString = 'Pending';
        } else if (status['approved']) {
            backgroundColor = green;
            statusString = 'Approved';
        } else if (status['denied'] || status['expired']) {
            backgroundColor = red;
            statusString = 'Denied';
        }

        if (momentToday >= moment(date) && status['pending']) {
            backgroundColor = red;
            statusString = 'Expired';
        }

        var event = {
            title: 'Time Off',
            start: date,
            allDay: true,
            editable: false,
            backgroundColor: backgroundColor,
            borderColor: backgroundColor,
            description: statusString,
            tooltip: reason,
            isTimeOff: true,
            statusDict: status,
        };

        $('#calendar').fullCalendar('renderEvent', event, true);

    }

    $('#save-schedule-button').on('click', function(e) {

        $('#calendar-box').append('<div class="overlay" id="calendar-loading-indicator"><i class="fa fa-refresh fa-spin"></i></div>');

        var events = $('#calendar').fullCalendar('clientEvents');
        var timeOffDict = {
            'reasons': {},
            'statuses': {}
        }

        $.each(events, function(i, event) {

            var dateString = event.start.format('DD/MM/YYYY');

            if (event.isTimeOff) {
                var reason = event.tooltip;
                var status = event.statusDict;

                timeOffDict['reasons'][dateString] = reason;
                timeOffDict['statuses'][dateString] = status;
            }

        })

        var timeOffDictString = JSON.stringify(timeOffDict);
        ajaxUpdateUserSchedule(timeOffDictString);

    })

    // get schedule with ajax
    function ajaxGetUserSchedule(startDate, endDate) {
        var startDateString = moment(startDate).format('DD-MM-YYYY');
        var endDateString = moment(endDate).format('DD-MM-YYYY');

        $.ajax({
            url: "/hive/ajax/user-schedule/" + startDateString + "/" + endDateString + "/",
            type: "GET",
            success: function(data) {

                var exactTimes = data['exact_times'];
                var positions = data['positions'];

                var timeOffReasons = data['time_off_reasons'];
                var timeOffStatuses = data['time_off_statuses'];

                $.each(exactTimes, function(dateString, time) {

                    var date = moment(dateString, 'DD/MM/YYYY').toDate();
                    var timeString = time.toUpperCase();
                    var position = positions[dateString];

                    addNewShift(date, position, timeString)
                })

                $.each(timeOffReasons, function(dateString, reason) {

                    var date = moment(dateString, 'DD/MM/YYYY').toDate();
                    var status = timeOffStatuses[dateString];

                    addNewTimeOff(date, reason, status)

                })

                $('#calendar-loading-indicator').remove();
                $('#add-time-off-button').prop('disabled', false);;

            }
        })

    }

    function ajaxUpdateUserSchedule(data) {
        $.ajax({
            url: "/hive/ajax/user-time-off/",
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
                showAlert('Error: "' + errorThrown + '"', false, 'calendar-box');
            },
            beforeSend: function(xhr, settings) {
                if (!this.crossDomain) {
                    xhr.setRequestHeader('X-CSRFToken', csrfToken);
                }
            }
        })
    }

    ajaxGetUserSchedule(startDate, endDate);

})