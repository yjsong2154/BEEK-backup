/*global kakao*/

import React, { useState, useEffect } from "react";
import axios from "axios";
import styled from "styled-components";

const MainBox = styled.div`
  display: flex;
  flex-direction: column;
  height: 45%;
  width: 100%;
  justify-content: center;
  align-items: center;
`;

const InputBox = styled.div`
  display: flex;
  flex-direction: row;
  height: 10%;
  width: 100%;
  max-width: 800px;
`;

const InputSty = styled.input`
  display: flex;
  height: 100%;
  width: 70%;
  padding-left: 2%;
  background-color: #eeeeee;
  &:focus {
    outline: none;
  }
`;

const ButtonSty = styled.button`
  display: flex;
  height: 100%;
  width: 30%;
  justify-content: center;
  align-items: center;
`;

const Map = styled.div`
  display: flex;
  max-height: 600px;
  max-width: 800px;
  height: 90%;
  width: 100%;
`;

function MapInput(props) {
  const [addName, setAddName] = useState("");
  const [positions, setPositions] = useState([]);

  useEffect(() => {
    showMap();
  }, [positions]);

  const showMap = () => {
    // console.log('showMap')
    // console.log(positions)

    var container = document.getElementById("map");
    var options = {
      center: new kakao.maps.LatLng(33.450701, 126.570667),
      level: 3,
    };

    var map = new kakao.maps.Map(container, options);
    var bounds = new kakao.maps.LatLngBounds();

    for (var i = 0; i < positions.length; i++) {
      var marker = new kakao.maps.Marker({
        map: map,
        position: positions[i].latlng,
        title: positions[i].title,
      });
      bounds.extend(positions[i].latlng);
    }

    if (positions.length > 0) {
      marker.setMap(map);
      map.setBounds(bounds);
    }
  };

  const handleChangeInput = (e) => {
    setAddName(e.target.value);
  };

  const handleEnter = (e) => {
    if (e.key === "Enter") {
      handleClickInput();
    }
  };

  const apiCall = async (lat, lon) => {
    // console.log(lat,lon);
    const query = `http://106.254.0.183:3001/api/youngwang?name=${addName}&lat=${lat}&lon=${lon}&range=2`;
    console.log(query);
    const response = await axios.get(query);
    const result = response.data;
    // console.log(result);
    const dots = result.map((result) => {
      return {
        title: result.company_name,
        latlng: new kakao.maps.LatLng(result.latitude, result.longitude),
      };
    });
    props.setResult(result);
    setPositions(dots);
  };

  const handleClickInput = (e) => {
    var places = new kakao.maps.services.Places();
    var lat = 0,
      lon = 0;

    var callback = function (result, status) {
      if (status === kakao.maps.services.Status.OK) {
        lat = result[0].y;
        lon = result[0].x;
      }
      apiCall(lat, lon);
    };

    places.keywordSearch(addName, callback);
  };

  return (
    <MainBox>
      <InputBox>
        <InputSty
          value={addName}
          onKeyPress={handleEnter}
          onChange={handleChangeInput}
          placeholder="주소를 입력해 주세요"
        />
        <ButtonSty onClick={handleClickInput}>검색</ButtonSty>
      </InputBox>
      <Map id="map" />
    </MainBox>
  );
}

export default MapInput;
