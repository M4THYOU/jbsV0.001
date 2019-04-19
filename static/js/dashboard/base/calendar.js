$(function() {

    var schedule = {};
    var timeOff = {};

    var scheduleObjects = {};
    var timeOffObjects = {};

    $calendar = $('#calendar');

    // Initialize datepicker
    $calendar.datepicker({
        format: 'dd/mm/yyyy',
        startDate: startDate,
        endDate: endDate,
        maxViewMode: 0,
        beforeShowDay: updateCellType
    })

    // month change function - hides the arrow to continue viewing more months (which are not selectable).
    $calendar.on('changeMonth', function(e) {
        var selectedMonth = new Date(e.date).getMonth();
        var currentMonth = currentDate.getMonth();

        if (selectedMonth == currentMonth - 1) {
            $('th.prev').css('visibility', 'hidden');
        } else if (selectedMonth == currentMonth + 1) {
            $('th.next').css('visibility', 'hidden');
        } else {
            $('th.prev').css('visibility', 'visible');
            $('th.next').css('visibility', 'visible');
        }

    });

    // date change function - updates the description box with data from the selected date.
    $calendar.on('changeDate', function(e) {
        var selectedDate = e.date;

        var schedule = window.schedule;
        var timeOff = window.timeOff;

        var scheduleObjects = window.scheduleObjects;
        var timeOffObjects = window.timeOffObjects;

        if (schedule === undefined || timeOff === undefined || scheduleObjects === undefined || timeOffObjects === undefined) {
            return
        }

        if (scheduleObjects[selectedDate]) {

            var exactTimes = schedule['exact_times'];
            var positions = schedule['positions'];

            var selectedDateString;
            for (var dateString in exactTimes) {
                var dateObject = getRealDate(dateString);

                if (selectedDate.getTime() == dateObject.getTime()) {
                    selectedDateString = dateString;
                }

            }

            if (selectedDateString !== undefined) {
                var time = exactTimes[selectedDateString];
                var position = positions[selectedDateString];
                $('#calendar-status').empty();
                $('#calendar-status').append('<p>'+ position + '</p>');
                $('#calendar-status').append('<p>' + time + '</p>');
            }

        } else if (timeOffObjects[selectedDate]) {

            var statuses = timeOff['statuses'];

            var selectedDateString;
            for (var dateString in statuses) {
                var dateObject = getRealDate(dateString);

                if (selectedDate.getTime() == dateObject.getTime()) {
                    selectedDateString = dateString;
                }

            }

            if (selectedDateString !== undefined) {
                var statusDict = statuses[selectedDateString];
                var status = 'Error getting time off status';
                var color = 'red';

                if (statusDict['approved']) {
                    status = 'Approved';
                    color = '#2dbe2d' // green
                } else if (statusDict['denied']) {
                    status = 'Denied'
                    color = '#ed4337' // red
                } else if (statusDict['pending']) {
                    status = 'Pending'
                    color = '#f7d222' // yellow
                } else if (statusDict['expired']) {
                    status = 'Expired'
                    color = '#ed4337' // red
                }

                $('#calendar-status').empty();
                $('#calendar-status').append('<p>Time Off Request</p>');
                $('#calendar-status').append('<p style="color: ' + color + '">' + status + '</p>');

            }

        } else {
            $('#calendar-status').empty();
            $('#calendar-status').append('<p>Select a date for more information.</p>');
            $('#calendar-status').append('<p>No events</p>');
        }

    })

    // convert list of date strings to dict of date objects
    function getRealDates(dateStrings) {
        var realDates = {};

        for (var i = 0; i < dateStrings.length; i++) {
            var newDate = getRealDate(dateStrings[i]);
            realDates[newDate] = true;
        }

        return realDates
    }

    function getRealDate(dateString) {
        var parts = dateString.split('/');

        var day = parts[0];
        var month = parts[1];
        var year = parts[2];

        var newDate = new Date(year, month - 1, day);

        return newDate;
    }

    // get schedule with ajax
    function ajaxGetCalendarData() {
        $.ajax({
            url: "ajax/schedule-timeoff/",
            type: "GET",
            success: function(data) {
                var schedule = data['schedule'];
                var timeOff = data['time_off'];

                window.schedule = schedule;
                window.timeOff = timeOff;

                var schedule_exactTimes = schedule['exact_times'];
                var schedule_positions = schedule['positions'];

                var timeOff_reasons = timeOff['reasons'];
                var timeOff_statuses = timeOff['statuses'];

                var scheduleDates = [];
                $.each(schedule_exactTimes, function(date, time) {
                    scheduleDates.push(date);
                })
                var realScheduleObjects = getRealDates(scheduleDates);

                var timeOffDates = [];
                $.each(timeOff_statuses, function(date, status) {
                    timeOffDates.push(date);
                })
                var realTimeOffObjects = getRealDates(timeOffDates);

                window.scheduleObjects = realScheduleObjects;
                window.timeOffObjects = realTimeOffObjects;

                $calendar.datepicker('update');

            }
        })

    }

    // change calendar cell before showing it
    function updateCellType(date) {

        var schedule = window.scheduleObjects;
        var timeOff = window.timeOffObjects;

        if (schedule === undefined || timeOff === undefined) {
            return
        }

        if (schedule[date]) {
            return 'working';
        } else if (timeOff[date]) {
            return 'timeOff';
        }

    }

    // call functions
    ajaxGetCalendarData();

    var currentDate = new Date();
    var startDate = new Date(currentDate.getFullYear(), currentDate.getMonth() - 1, 1);
    var endDate = new Date(currentDate.getFullYear(), currentDate.getMonth() + 2, 0);

})