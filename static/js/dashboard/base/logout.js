$(function() {

    firebase.auth().signOut().then(function() {
        console.log('signed out');
    }).catch(function(error) {
        console.log(error);
    })

})