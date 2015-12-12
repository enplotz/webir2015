var Entity = function (id, cb) {
    var public = this;
    var __co = {};
    var __id;
    var __data;

    function __init() {
        var __id; 
        if (typeof id === 'number') {
            __id = id;  //new data, specified by ID
            $.post('http://localhost:8000/EntityByID', {
                class: 'Author',
                id: __id
            }, 'json').done(function (data) {
            __data = data;
            if (cb) cb(__data);
            });  
        } else {
            return;    
        }

    }
    __init();
}