/*global kakao*/

import React, { useState, useEffect } from "react";
import MapInput from "./MapInput.js";
import MapResult from "./MapResult.js";
import styled from "styled-components";
import { Modal, Button } from "antd";
import "antd/dist/antd.css";

function MapPage() {
  const [result, setResult] = useState([]);
  const [isFirst, setIsFirst] = useState(true);
  const [id, setId] = useState("");
  const [isModalOn, setIsModalOn] = useState(false);
  const [mapState, setMapState] = useState("");
  const [markerState, setMarkerState] = useState("");

  useEffect(() => {
    if (id === "" && isFirst === true) {
    } else if (id === "" && isFirst === false) {
    } else if (id !== "" && isFirst === true) {
      showMap();
    } else {
      updateMap();
    }
  }, [id]);

  const showMap = () => {
    var mapContainer = document.getElementById("map2"),
      mapOption = {
        center: new kakao.maps.LatLng(id[5], id[6]),
        level: 3,
      };

    var map = new kakao.maps.Map(mapContainer, mapOption);

    var markerPosition = new kakao.maps.LatLng(id[5], id[6]);

    var marker = new kakao.maps.Marker({
      position: markerPosition,
    });

    marker.setMap(map);
    // console.log(map)
    setMapState(map);
    setMarkerState(marker);
    setIsFirst(false);
  };

  const updateMap = () => {
    // mapState
  };

  const handleCancel = () => {
    setIsModalOn(false);
  };

  return (
    <MotherBackground>
      <Modal
        title={id[0]}
        visible={isModalOn}
        onOk={handleCancel}
        onCancel={handleCancel}
        footer={[
          <Button key="back" type="primary" onClick={handleCancel}>
            닫기
          </Button>,
        ]}
      >
        <Map id="map2" />
        <p>주소 : {id[1]}</p>
        <p>전화번호 : {id[2]}</p>
        <p>종류 : {id[3]}</p>
        <p>대표 : {id[4]}</p>
      </Modal>
      <MapInput setResult={setResult} />
      <MapResult result={result} setId={setId} setIsModalOn={setIsModalOn} />
    </MotherBackground>
  );
}

const MotherBackground = styled.div`
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
  justify-content: center;
  align-items: center;
`;
const Map = styled.div`
  /* display : flex;
	max-height : 600px;
	max-width : 800px; */
  /* height : 90%;
	width : 100%; */
  height: 200px;
  width: 400px;
`;

export default MapPage;
