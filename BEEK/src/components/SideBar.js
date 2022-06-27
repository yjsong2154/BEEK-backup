import React from "react";
import styled from "styled-components";

const BackField = styled.div`
  display: flex;
  height: 100%;
  width: 100%;
  background-color: white;
  justify-content: center;
  align-items: center;
`;
// const NewField = styled.div`
//     display:flex;
//     height : 30%;
//     width : 100%;
//     align-items : center;
//     justify-content : space-between;
//     flex-direction : column;
// `
const RankField = styled.div`
  display: flex;
  height: 500px;
  width: 100%;
  padding-top: 20px;
  align-items: center;
  justify-content: space-between;
  flex-direction: column;
`;
const RankBox = styled.div`
  display: flex;
  height: 9%;
  width: 90%;
`;
const RankPic = styled.img`
  height: 100%;
  width: 20%;
  object-fit: contain;
`;
const RankText = styled.div`
  display: flex;
  height: 100%;
  width: 70%;
  margin: auto;
  font-size: 3.5vh;
  font-weight: bold;
  align-items: center;
`;

function SideBar(props) {
  const data = props.data;

  const uppic = "./image/uppic1.png";
  const downpic = "./image/downpic1.png";
  const newpic = "./image/newpic1.png";
  const samepic = "./image/samepic1.png";

  let pic = [];
  for (let item of data) {
    if (item.change === 0) {
      pic.push(samepic);
    } else if (item.change === 1) {
      pic.push(uppic);
    } else if (item.change === 2) {
      pic.push(downpic);
    } else {
      pic.push(newpic);
    }
  }

  return (
    <BackField>
      {/* <NewField>신규 진입</NewField> */}
      <RankField>
        <RankBox>
          <RankPic src={pic[0]} />
          <RankText>{data[0].name}</RankText>
        </RankBox>
        <RankBox>
          <RankPic src={pic[1]} />
          <RankText>{data[1].name}</RankText>
        </RankBox>
        <RankBox>
          <RankPic src={pic[2]} />
          <RankText>{data[2].name}</RankText>
        </RankBox>
        <RankBox>
          <RankPic src={pic[3]} />
          <RankText>{data[3].name}</RankText>
        </RankBox>
        <RankBox>
          <RankPic src={pic[4]} />
          <RankText>{data[4].name}</RankText>
        </RankBox>
        <RankBox>
          <RankPic src={pic[5]} />
          <RankText>{data[5].name}</RankText>
        </RankBox>
        <RankBox>
          <RankPic src={pic[6]} />
          <RankText>{data[6].name}</RankText>
        </RankBox>
        <RankBox>
          <RankPic src={pic[7]} />
          <RankText>{data[7].name}</RankText>
        </RankBox>
        <RankBox>
          <RankPic src={pic[8]} />
          <RankText>{data[8].name}</RankText>
        </RankBox>
        <RankBox>
          <RankPic src={pic[9]} />
          <RankText>{data[9].name}</RankText>
        </RankBox>
      </RankField>
    </BackField>
  );
}

export default SideBar;
