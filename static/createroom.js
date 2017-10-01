$(document).ready(function() {
    // Use a "/test" namespace.
    // An application can open a connection on multiple namespaces, and
    // Socket.IO will multiplex all those connections on a single
    // physical channel. If you don't care about multiple channels, you
    // can set the namespace to an empty string.
    namespace = '/test';

    // Connect to the Socket.IO server.
    // The connection URL has the following format:
    //     http[s]://<domain>:<port>[/<namespace>]
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace);
    console.log(location.protocol + '//' + document.domain + ':' + location.port + namespace)

    // Event handler for new connections.
    // The callback function is invoked when a connection with the
    // server is established.
    socket.on('connect', function() {
        socket.emit('my_event', { data: 'I\'m connected!' });
    });

    socket.on('redirect', function(data) {
        window.location = data.url;
    });

    // Event handler for server sent data.
    // The callback function is invoked whenever the server emits data
    // to the client. The data is then displayed in the "Received"
    // section of the page.
    socket.on('my_response', function(msg) {
        $('#log').append('<br>' + $('<div/>').text('Received #' + msg.count + ': ' + msg.data).html());
    });

    console.log(socket);


    var question_table = new Vue({
        el: "#question_table",
        data: {
            rows: [
                { Question: "", Answer: "" },
            ]
        },
        methods: {
            addRow: function() {
                this.rows.push({ Question: "", Answer: "" });
            },
            removeRow: function(index) {
                this.rows.splice(index, 1);
            }
        }
    });

    $('form#create').submit(function(event) {
        var Questions = [];
        var Answers = [];
        for (i = 0; i < question_table.rows.length; i++) {
            Questions.push(String(question_table.rows[i].Question));
            Answers.push(String(question_table.rows[i].Answer));
        }
        console.log(Questions);
        console.log(Answers);
        socket.emit('create_room', { room: localStorage.getItem("roomNameStorage"), title: $('#room_title').val(), questions: Questions, solutions: Answers });
        window.location.href="/";
        return false;
    })







})
