var express = require('express');
var router = express.Router();
var mysqlDB = require('../../dbConnector')

router.get('/', function(req, res, next) {
  var name = req.query.name;
  var lat = req.query.lat;
  var lon = req.query.lon;
  var range = req.query.range;

  var latUp = parseFloat(lat)+(0.01*parseFloat(range));
  var latDown = parseFloat(lat)-(0.01*parseFloat(range));
  var lonUp = parseFloat(lon)+(0.01*parseFloat(range));
  var lonDown = parseFloat(lon)-(0.01*parseFloat(range));

  if (lat == '' || lon == ''){
    res.send({resultCd:'E', msg: "위도 경도 값 없음"});
  }else if (name == ''){
    res.send({resultCd:'E', msg: "주소 값 없음"})
  }

  //escape 추가 필요
  var queryCord = 'select * from company where (latitude between '+ latDown +' and '+latUp+') and (longitude between '+ lonDown +' and '+lonUp+')';
  var queryName = 'SELECT * FROM company WHERE address LIKE \'%' + name + '%\'';
  // var query = 'select * from company where (latitude between 36.8 and 37.1) and (longitude between 127.0 and 127.2)'

  // changed return search result
  mysqlDB.query(
    queryCord + queryName, function (err, result){
      var cordResult = result[0];
      var nameResult = result[1];

      if(err){
        res.send({resultCd:'E', msg: "예기치 않은 오류가 발생하여 대회 생성에 실패하였습니다."});
        throw err;
      }else if(nameResult.length > 0){
        res.send(nameResult);
      }else{
        res.send(cordResult);
      }
    }
  );
});

module.exports = router;
