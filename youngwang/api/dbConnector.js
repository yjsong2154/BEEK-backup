var mysql = require('mysql');
var connection = mysql.createConnection({
    // host: '106.254.0.183',
    host: 'localhost',
    port: 3306,
    user: 'root',
    password: 'Tpt!@#1134',
    database: 'youngwang'
});

module.exports = connection;