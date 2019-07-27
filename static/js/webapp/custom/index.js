$(function() {

    // get CSRF token
    var csrfToken = $('input[name="csrfmiddlewaretoken"]').val();

    $salaryField = $('#annual-pay-field');
    $managerCountField = $('#number-managers-field');
    $scheduleHoursField = $('#hours-scheduling-field');

    function validateCalculatorInputs(salaryVal, managersVal, hoursVal) {

        var isValid = true;

        if (salaryVal == "") {
            $salaryField.css('border-color', 'red');
            isValid = false;
        } else if (!$.isNumeric(salaryVal)) {
            $salaryField.css('border-color', 'red');
            isValid = false;
        } else {
            $salaryField.css('border-color', '');
        }

        if (managersVal == "") {
            $managerCountField.css('border-color', 'red');
            isValid = false;
        } else if (!$.isNumeric(managersVal)) {
            $managerCountField.css('border-color', 'red');
            isValid = false;
        } else if (parseFloat(managersVal) < 1) {
            $managerCountField.css('border-color', 'red');
            isValid = false;
        } else {
            $managerCountField.css('border-color', '');
        }

        if (hoursVal == "") {
            $scheduleHoursField.css('border-color', 'red');
            isValid = false;
        } else if (!$.isNumeric(hoursVal)) {
            $scheduleHoursField.css('border-color', 'red');
            isValid = false;
        } else if (parseFloat(hoursVal) < 1) {
            $scheduleHoursField.css('border-color', 'red');
            isValid = false;
        }  else {
            $scheduleHoursField.css('border-color', '');
        }

        return isValid

    }

    function salaryToHourly(salary) {
        var salaryFloat = parseFloat(salary);

        // Assumes working 50 weeks in a year, 35 hours per week.
        var workWeeks = 50;
        var weekHours = 35;
        var hourlyFloat = salaryFloat / (workWeeks * weekHours);

        return hourlyFloat;
    }

    function calculateAnnualSpending() {
        salaryVal = $salaryField.val();
        managersVal = $managerCountField.val();
        hoursVal = $scheduleHoursField.val();

        var isValid = validateCalculatorInputs(salaryVal, managersVal, hoursVal);
        if (!isValid) {
            return;
        }

        var hourlyRate = salaryToHourly(salaryVal);
        var managersFloat = parseFloat(managersVal);
        var hoursFloat = parseFloat(hoursVal);

        var annualSpending = hourlyRate * managersFloat * hoursFloat * 52;
        var roundedAnnualSpending = (Math.round(annualSpending*Math.pow(10,2))/Math.pow(10,2)).toFixed(2)
        var formattedAnnualSpending = roundedAnnualSpending.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");

        $('#price-calculation').text(formattedAnnualSpending);

    }

    $salaryField.on('input', function(e) {
        var newVal = $salaryField.val();
        mixpanel.track('INDEX | Calculator manager pay changed', {'newValue': newVal});

        calculateAnnualSpending();
    })
    $managerCountField.on('input', function(e) {
        var newVal = $managerCountField.val();
        mixpanel.track('INDEX | Calculator manager count changed', {'newValue': newVal});

        calculateAnnualSpending();
    })
    $scheduleHoursField.on('input', function(e) {
        var newVal = $scheduleHoursField.val();
        mixpanel.track('INDEX | Calculator manager hours changed', {'newValue': newVal});

        calculateAnnualSpending();
    })

    calculateAnnualSpending();

    ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

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
            mixpanel.track('INDEX | Valid email submit', {'email': emailText});
            postEmail(emailText);
        } else {
            mixpanel.track('INDEX | Invalid email submit', {'email': emailText});
        }
    })

    function toggleLoading(isNowLoading) {

        if (isNowLoading) {
            $('#email-submit-form').append('<div class="loader"></div>');
            $emailField.prop('disabled', true);
            $('#demo-button').prop('disabled', true);
        } else {
            $('.loader').remove();
            $emailField.prop('disabled', false);
            $('#demo-button').prop('disabled', false);
        }

    }

    function showEmailSuccess(message) {
        formContainer = $('#email-submit-form');
        formContainer.css('display', 'inline-block');
        formContainer.html('<p style="color: white;">' + message + '</p>');
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
                var message = data + ' <a href="/hive/demo/" id="email-submit-try-demo">Try the Demo</a>'
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

// Metric Tracking with MixPanel ///////////////////////////////////////////////////////////////////////////////////////

    $('#opening-demo-button').on('click', function() {
        mixpanel.track('INDEX | Opening Demo Button Click');
    })

    $('#jbs-can-help-button').on('click', function() {
        var salary = $salaryField.val();
        var managerCount = $managerCountField.val();
        var hoursSpent = $scheduleHoursField.val();

        var annualSpend = $('#price-calculation').text();

        mixpanel.track('INDEX | JBS can help Button Click', {'calcSalary': salary, 'calcManagerCount': managerCount, 'calcHoursSpent': hoursSpent, 'calcAnnualSpend': annualSpend});
    })

    function createOnClick() {
        $('#email-submit-try-demo').on('click', function() {
            mixpanel.track('INDEX | Email submit try demo Button Click');
        })
    }

})