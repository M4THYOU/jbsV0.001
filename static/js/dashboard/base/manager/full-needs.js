$(function() {

    // get CSRF token
    var csrfToken = $('input[name="csrfmiddlewaretoken"]').val();

    //needs model
    var needsModel = {
        'sunday': [
            "0", // 0-1,   12:00 am (midnight) - 1:00 am       index:0
            "0", // 1-2,   1:00 am - 2:00 am                   index:1
            "0", // 2-3,   2:00 am - 3:00 am                   index:2
            "0", // 3-4,   3:00 am - 4:00 am                   index:3
            "0", // 4-5,   4:00 am - 5:00 am                   index:4
            "0", // 5-6,   5:00 am - 6:00 am                   index:5
            "0", // 6-7,   6:00 am - 7:00 am                   index:6
            "0", // 7-8,   7:00 am - 8:00 am                   index:7
            "0", // 8-9,   8:00 am - 9:00 am                   index:8
            "0", // 9-10,  9:00 am - 10:00 am                  index:9
            "0", // 10-11, 10:00 am - 11:00 am                 index:10
            "0", // 11-12, 11:00 am - 12:00 pm                 index:11
            "0", // 12-13, 12:00 pm (noon) - 1:00 pm           index:12
            "0", // 13-14, 1:00 pm - 2:00 pm                   index:13
            "0", // 14-15, 2:00 pm - 3:00 pm                   index:14
            "0", // 15-16, 3:00 pm - 4:00 pm                   index:15
            "0", // 16-17, 4:00 pm - 5:00 pm                   index:16
            "0", // 17-18, 5:00 pm - 6:00 pm                   index:17
            "0", // 18-19, 6:00 pm - 7:00 pm                   index:18
            "0", // 19-20, 7:00 pm - 8:00 pm                   index:19
            "0", // 20-21, 8:00 pm - 9:00 pm                   index:20
            "0", // 21-22, 9:00 pm - 10:00 pm                   index:21
            "0", // 22-23, 10:00 pm - 11:00 pm                  index:22
            "0"  // 23-0,  11:00 pm - 12:00 pm (midnight)      index:23
        ],
        'monday': ["0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0"],
        'tuesday': ["0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0"],
        'wednesday': ["0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0"],
        'thursday': ["0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0"],
        'friday': ["0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0"],
        'saturday': ["0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0"],

        'sundayNoNeeds': false,
        'mondayNoNeeds': false,
        'tuesdayNoNeeds': false,
        'wednesdayNoNeeds': false,
        'thursdayNoNeeds': false,
        'fridayNoNeeds': false,
        'saturdayNoNeeds': false,

        'minShiftLength': "0",
        'maxShiftLength': "0"
    }

    // Initialize shift slider
    var $shiftSlider = $('.shift-slider');
    $shiftSlider.bootstrapSlider();

    var needsChartCanvas = $('#needsChart').get(0).getContext('2d');
    var needsChart = new Chart(needsChartCanvas, {
        type: 'line',

        data: {
            labels: [
                '12:00 AM - 1:00 AM', '1:00 AM - 2:00 AM', '2:00 AM - 3:00 AM', '3:00 AM - 4:00 AM', '4:00 AM - 5:00 AM',
                '5:00 AM - 6:00 AM', '6:00 AM - 7:00 AM', '7:00 AM - 8:00 AM', '8:00 AM - 9:00 AM', '9:00 AM - 10:00 AM',
                '10:00 AM - 11:00 AM', '11:00 AM - 12:00 PM', '12:00 PM - 1:00 PM', '1:00 PM - 2:00 PM',
                '2:00 PM - 3:00 PM', '3:00 PM - 4:00 PM', '4:00 PM - 5:00 PM', '5:00 PM - 6:00 PM', '6:00 PM - 7:00 PM',
                '7:00 PM - 8:00 PM', '8:00 PM - 9:00 PM', '9:00 PM - 10:00 PM', '10:00 PM - 11:00 PM',
                '11:00 PM - 12:00 PM'
            ],
            datasets: [
                {
                    label               : 'Employees Needed',
                    backgroundColor     : 'rgba(196, 93, 105, 0.3)',
                    fill                : true,
                    strokeColor         : 'rgba(60,141,188,0.8)',
                    pointColor          : '#3b8bba',
                    pointStrokeColor    : 'rgba(60,141,188,1)',
                    pointHighlightFill  : '#fff',
                    pointHighlightStroke: 'rgba(60,141,188,1)',
                    data                : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],

                    pointHitRadius: 15,
                    pointHoverRadius: 10,
                }
            ],

        },

        options: {
            scales: {
                yAxes: [{
                    scaleLabel: {
                        display: true,
                        labelString: 'Employees Needed'
                    },
                    ticks: {
                        min: 0,
                        max: 25,
                    }
                }]
            },
            legend: {
                display: false
            },
        }

    });

    var par = {
        chart: undefined,
        element: undefined,
        scale: undefined,
        datasetIndex: undefined,
        index: undefined,
        value: undefined,
        grabOffsetY: undefined,
    };

    function getEventPoints(event) {
        var retval = {
            point: [],
            type: event.type
        };

        if (event.type.startsWith('touch')) {
            for (var i = 0; i < event.changedTouches.length; i++) {
                var touch = event.changedTouches.item(i);
                retval.point.push({
                    x: touch.clientX,
                    y: touch.clientY
                })
            }
        } else if (event.type.startsWith('mouse')) {
            retval.point.push({
                x: event.layerX,
                y: event.layerY
            })
        }

        return retval;

    }

    d3.select(needsChart.chart.canvas).call(
        d3.drag().container(needsChart.chart.canvas)
        .on('start', function() {
            var e = d3.event.sourceEvent;

            par.scale = undefined;

            par.element = needsChart.getElementAtEvent(e)[0];

            if (typeof par.element !== 'undefined') {
                par.chart = par.element['_chart'];
                par.scale = par.element['_yScale'];

                par.datasetIndex = par.element['_datasetIndex'];
                par.index = par.element['_index'];

                par.grabOffsetY = par.scale.getPixelForValue(
                    par.chart.config.data.datasets[par.datasetIndex].data[par.index],
                    par.index,
                    par.datasetIndex,
                    false
                ) - getEventPoints(e).point[0].y
            }

        })
        .on('drag', function() {
            var e = d3.event.sourceEvent;

            if (par.datasetIndex == 1) {
                return;
            }

            if (typeof par.element !== 'undefined') {
                par.value = Math.floor(par.scale.getValueForPixel(par.grabOffsetY + getEventPoints(e).point[0].y) + 0.5);
                par.value = Math.max(0, Math.min(100, par.value));
                par.chart.config.data.datasets[par.datasetIndex].data[par.index] = par.value;
                needsChart.update(0);
            }

        })
        .on('end', function() {
            var val = par.value;

            if (val > 25) {
                needsChart.data.datasets[par.datasetIndex].data[par.index] = 25;
                val = 25;
            } else if (val < 0) {
                needsChart.data.datasets[par.datasetIndex].data[par.index] = 0;
                val = 0;
            }
            needsChart.update({duration: 0});

            var currentDay = $('#day-select').val();

            needsModel[currentDay][par.index] = val.toString();
            //console.log(par.index);
        })
    );

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

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

    $('#toggle-open-button').on('click', function(e) {
        var buttonVal = $(this).prop('value');

        var currentDay = $('#day-select').val();

        var newText;
        var oldBtnClass;
        var newBtnClass;
        var newValue;
        if (buttonVal === 'open') {
            newText = 'Closed';
            oldBtnClass = 'btn-success';
            newBtnClass = 'btn-danger';
            newValue = 'closed';

            needsChart.data.datasets[0].data = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];
            needsModel[currentDay] = ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0",
                                      "0", "0", "0", "0", "0", "0", "0", "0"];

            needsModel[currentDay + 'NoNeeds'] = true;

            $('.body-overlay-container').append('<div class="body-overlay"></div>');
        } else if (buttonVal === 'closed') {
            newText = 'Open';
            oldBtnClass = 'btn-danger';
            newBtnClass = 'btn-success';
            newValue = 'open';

            needsModel[currentDay + 'NoNeeds'] = false;

            $('.body-overlay').remove();
        } else {
            console.log('Invalid button value');
            return;
        }

        $(this).text(newText);
        $(this).removeClass(oldBtnClass);
        $(this).addClass(newBtnClass);
        $(this).prop('value', newValue);

        needsChart.update({
            duration: 400,
        });

    })

    $('#day-select').on('change', function(e) {
        var day = $(this).val();
        var currentNeedsModel = needsModel[day];
        var intCurrentNeedsModel = currentNeedsModel.map(Number);

        needsChart.data.datasets[0].data = intCurrentNeedsModel;
        needsChart.update({
            duration: 400,
        });

        var noNeeds = needsModel[day + 'NoNeeds'];

        var newText;
        var oldBtnClass;
        var newBtnClass;
        var newValue;
        if (noNeeds) {
            if ($('.body-overlay-container').find('.body-overlay').length === 0) {
                $('.body-overlay-container').append('<div class="body-overlay"></div>');
            }

            newText = 'Closed';
            oldBtnClass = 'btn-success';
            newBtnClass = 'btn-danger';
            newValue = 'closed';
        } else {
            $('.body-overlay').remove();

            newText = 'Open';
            oldBtnClass = 'btn-danger';
            newBtnClass = 'btn-success';
            newValue = 'open';
        }

        $('#toggle-open-button').text(newText);
        $('#toggle-open-button').removeClass(oldBtnClass);
        $('#toggle-open-button').addClass(newBtnClass);
        $('#toggle-open-button').prop('value', newValue);

    })

    // when user clicks update button.
    $('#needs-update-button').on('click', function(e) {

        // show loading indicator
        $('#needs-box').append('<div class="overlay" id="needs-loading-indicator"><i class="fa fa-refresh fa-spin"></i></div>')

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

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

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

        // Only need to do this for sunday because that is the only day shown on load.
        var hasNeeds = true;
        if (sunday.reduce((partialSum, a) => partialSum + a) == 0) {
            // Set day to noNeeds = true.
            $('#toggle-open-button').text('Closed');
            $('#toggle-open-button').removeClass('btn-success');
            $('#toggle-open-button').addClass('btn-danger');
            $('#toggle-open-button').prop('value', 'closed');

            $('.body-overlay-container').append('<div class="body-overlay"></div>');

            hasNeeds = false;
        }

        //Set the initial sunday chart values, if it is not noNeeds.
        if (hasNeeds) {
            needsChart.data.datasets[0].data = sunday;
            needsChart.update({
                duration: 400
            });
        }

        var minShiftLength = parseInt(needsModel['minShiftLength']);
        var maxShiftLength = parseInt(needsModel['maxShiftLength']);
        $shiftSlider.bootstrapSlider('setValue', [minShiftLength, maxShiftLength], false, true);

        $('.timepicker-start').trigger('change');

        $('#needs-loading-indicator').remove();
    }

    // get needs with ajax
    function ajaxGetNeedsData() {
        $.ajax({
            url: "/hive/ajax/needs/",
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

    // update needs with ajax
    function ajaxUpdateNeeds(data) {
        $.ajax({
            url: "/hive/ajax/needs/",
            type: "POST",
            data: data,
            timeout: 15000,
            success: function(data) {
                $('#needs-loading-indicator').remove()
                showAlert(data, true);
            },
            error: function(xhr, textStatus, errorThrown) {
                $('#needs-loading-indicator').remove()
                showAlert('Error: "' + errorThrown + '"', false);
            },
            beforeSend: function(xhr, settings) {
                if (!this.crossDomain) {
                    xhr.setRequestHeader('X-CSRFToken', csrfToken);
                }
            }
        })
    }

    ajaxGetNeedsData();

})