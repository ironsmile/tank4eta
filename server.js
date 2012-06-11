
var http = require('http');

world = {

  map : null,
  map_size : 3,
  
  init : function () {

    this.map = this.create_array(this.map_size, function(){
      return null;
    });

    for (var i = 0; i < this.map.length; i++) {
      this.map[i] = this.create_array(this.map_size, function(){
        return Math.floor(Math.random()*11); 
      });
    }

  },

  create_array : function (how_many, gen) {
    var arr = [];
    for(var i=0; i < how_many; i++) {
      arr[arr.length] = gen();
    }
    return arr;
  },

  show_map : function () {
    console.log(this.map);
  }
    
};

world.init();
world.show_map();

var server = http.Server(function (req, res) {

  res.writeHead(200, {'Content-Type': 'text/json'});
  req.on('data', function(data){
    console.log('Incoming: '+data.toString());
    res.end(data.toString());
  });
  //console.log(req);
  //res.end(req.toString());

});

server.listen(8080);


