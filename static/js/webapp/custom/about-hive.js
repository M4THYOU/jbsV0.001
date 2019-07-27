$(function() {

// Metric Tracking with MixPanel ///////////////////////////////////////////////////////////////////////////////////////

    $('#try-demo').on('click', function() {
        mixpanel.track('ABOUT-HIVE | Try demo Button Click');
    })

})