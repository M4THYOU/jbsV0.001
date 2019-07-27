$(function() {

    // set the day schedule widget's date.
    function setDayScheduleDate(date) {
        var day = date.getDate();
        var month = date.toLocaleString('en-us', {month: 'long'});
        var year = date.getFullYear();

        var monthYear = month + ' ' + year;

        $('#day-schedule-day').text(day);
        $('#day-schedule-month-year').text(monthYear);
    }

    // get this day's schedule with ajax
    function ajaxGetDaySchedule(date) {
        var dateString = moment(date).format('DD-MM-YYYY');

        $.ajax({
            url: "ajax/day-schedule/" + dateString + "/",
            type: "GET",
            success: function(data) {

                var exactTimes = data['exact_times']
                var positions = data['positions']

                var htmlToAppend = ''
                $.each(exactTimes, function(fullName, time) {
                    var timeParts = time.split('-');
                    var startTime = timeParts[0].trim();
                    var endTime = timeParts[1].trim();
                    var html = (
                        '<tr>' +
                            '<td>' + fullName + '</td>' +
                            '<td>' + positions[fullName] + '</td>' +
                            '<td style="text-align: center">' +
                                '<span class="badge bg-green">' + startTime.toUpperCase() + '</span>'+
                                '<span class="badge bg-red">' + endTime.toUpperCase() + '</span>' +
                            '</td>' +
                        '</tr>'
                    );

                    htmlToAppend += html;
                })

                $('#day-schedule-loading-indicator').remove();
                $('#schedule-day-table').append(htmlToAppend);

            },
            error: function(xhr, textStatus, errorThrown) {
                $('#day-schedule-loading-indicator').remove();
            }
        })

    }

    // call functions
    var currentDate = new Date();
    setDayScheduleDate(currentDate);
    ajaxGetDaySchedule(currentDate);

    // For MixPanel
    $('#go-to-schedule-builder').on('click', function() {
        mixpanel.track('DASHBOARD | Schedule builder Button Click');
    })

})