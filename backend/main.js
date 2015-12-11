var express = require('express');
var compress = require('compression');
var bodyParser = require('body-parser');
var async = require('async');

var cors = require('cors');
var postgres = require('pg');
postgres.defaults.poolSize = 100;
var config = require('./config');

var app = express();

app.use(compress({
    level: 9
}));
app.use(cors()); //use cors for avoiding cross-reference exceptions 
app.use(bodyParser.urlencoded({ //accepts url-encoded POST parameters
    extended: true
}));
app.use(bodyParser.json()); //accepts json-encoded POST objects

app.post('/EntityByID', function (req, res) {
    if (!req.body.class || !req.body.id) return;
    postgres.connect(config.getDBAuth(), function (error, client, done) {
        if (error) {
            console.log("Postgres connection error.", error);
        } else {
            var query;
            if (req.body.class === 'Author') {
                query = 'SELECT * FROM author WHERE id=' + req.body.id;
            } else if (req.body.class === 'FOS') {

            } else if (req.body.class === 'Uni') {

            } else {

            }
            client.query(query, function (error, result) {
                res.send((error) ? ("" + error) : result.rows[0]);
                done();
            });
        }
    });
});

app.post('/ExtendedByID', function(req, res){ 
    if (!req.body.class || !req.body.obj) return; 
    postgres.connect(config.getDBAuth(), function (error, client, done) {
        if (error) { 
           console.log("Postgres connection error.", error);
        } else { 
            var query;
            if (req.body.class === 'Author') {          

				query = 'SELECT author.*, links FROM ('; 
				query += ' SELECT rel, array_agg(li) AS links FROM ('
 query += ' SELECT DISTINCT ON (direct.rel, li) direct.rel, CASE WHEN co.author1 = direct.rel THEN co.author2  WHEN co.author2 = direct.rel THEN co.author1 END AS li FROM (' 
query += 'SELECT CASE WHEN author1 =  '+req.body.obj.clicked+' THEN author2 ELSE author1  END AS rel FROM coauthor c WHERE c.author1= ' +req.body.obj.clicked+' OR c.author2='+req.body.obj.clicked+'  ORDER BY freq DESC LIMIT '+req.body.limit+' ) direct, coauthor co WHERE  (direct.rel NOT IN ('+req.body.obj.all.toString()+')) )'
query += '  snd WHERE (li IS NOT NULL) GROUP BY rel';
query += ' ) third, author WHERE author.id = rel' 
console.log(query); 
            } else if (req.body.class === 'FOS') {

            } else if (req.body.class === 'Uni') {

            } else {

            }
            client.query(query, function (error, result) {
                res.send((error) ? ("" + error) : result.rows);
                console.log(result.rows); 
                done();
            });
        }
    }); 
}); 
app.listen(8000);