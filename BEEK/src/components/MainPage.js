import React, { useState, useEffect } from "react";
import axios from "axios";
import styled from "styled-components";
import LineGrahp from "./LineGraph";
import BarGrahp from "./BarGraph";
import SideBar from "./SideBar";
import TopInput from "./TopInput";

function Pretreatment(input, inputrange = 10) {
  let weekNameList = [];
  const weekAllNameList = input.map((elem) => elem.name);
  for (
    let i = weekAllNameList.length - 1;
    i > weekAllNameList.length - inputrange - 1;
    i--
  ) {
    weekNameList.push(weekAllNameList[i]);
  }
  // console.log(weekNameList)

  const dateAllNameList = input.map((elem) => elem.date);
  let dateNameList = dateAllNameList.sort().reduce((accumulator, current) => {
    const length = accumulator.length;
    if (length === 0 || accumulator[length - 1] !== current) {
      accumulator.push(current);
    }
    return accumulator;
  }, []);
  // console.log(dateNameList);

  let weekRankList = [];
  for (let name of weekNameList) {
    let weekRankData = [];
    for (let date of dateNameList) {
      let picked = input.filter((elem) => {
        return elem.name === name && elem.date === date;
      });
      // console.log(picked);
      if (picked.length === 0) {
        weekRankData.push({ x: date.substr(5, 5), y: 10, count: null });
      } else {
        weekRankData.push({
          x: date.substr(5, 5),
          y: picked[0].rank,
          count: picked[0].count,
        });
      }
    }
    weekRankList.push({ id: name, data: weekRankData });
  }
  return weekRankList;
}

function MainPage() {
  const logo = "/image/logo1.png";

  const [isLoading, setIsLoading] = useState(true);
  const [isSearching, setIsSearching] = useState(true);
  const [dayrank, setDayrank] = useState("");
  const [daydata, setDaydata] = useState("");
  const [weekdata, setWeekdata] = useState("");
  const [monthdata, setMonthdata] = useState("");
  const [yeardata, setYeardata] = useState("");
  const [alltag, setAlltag] = useState("");

  const [startdate, setStartdate] = useState("");
  const [enddate, setEnddate] = useState("");
  const [keyword, setKeyword] = useState([]);
  const [searchdata, setSearchdata] = useState("");
  const [searchBardata, setSearchBardata] = useState("");

  useEffect(() => {
    if (isLoading === true) {
      apiCall();
    } else if (startdate !== "") {
      searchCall();
    }
  }, [startdate, enddate, keyword]);

  const apiCall = async () => {
    const response = await axios.get(
      "http://www.talpiot-api.kro.kr:55555/rank/view"
    );
    const alldata = response.data.data;
    // console.log(alldata);

    const today = alldata[0].today;
    const todayRank = today.map((elem) => ({
      change: elem.change,
      name: elem.name,
    }));
    setDayrank(todayRank);
    const todayCount = today.map((elem) => ({
      name: elem.name,
      count: elem.count,
    }));
    setDaydata(todayCount);

    const week = alldata[1].week;
    const weekRankList = Pretreatment(week);
    // console.log(weekRankList);
    setWeekdata(weekRankList);

    const month = alldata[2].month;
    const monthRankList = Pretreatment(month);
    setMonthdata(monthRankList);

    const year = alldata[3].year;
    const yearRankList = Pretreatment(year);
    // console.log(yearRankList)
    setYeardata(yearRankList);

    const tagResponse = await axios.get("http://106.254.0.183:55555/crd/list");
    const tagdata = tagResponse.data.data;
    setAlltag(tagdata);

    // console.log(weekRankList);
    setIsSearching(false);
    setIsLoading(false);
  };

  const searchCall = async () => {
    setIsSearching(true);

    var params = new URLSearchParams();
    params.append("date1", startdate);
    params.append("date1", enddate);
    if (keyword.length > 0) {
      for (var item of keyword) {
        // console.log(item.value)
        params.append("keyword", item.value);
      }
    }
    var request = {
      params: params,
    };

    const searchResponse = await axios.get(
      "http://106.254.0.183:55555/rank/search",
      request
    );
    const searchAlldata = searchResponse.data.data[0];
    const searchBardata = searchResponse.data.data[1];

    // console.log(searchBardata);
    const searchCount = searchBardata.map((elem) => ({
      name: elem.name,
      count: elem.count,
    }));
    setSearchBardata(searchCount);

    const leng = keyword.length ? keyword.length : alltag.length;
    const searchList = Pretreatment(searchAlldata, leng);
    setSearchdata(searchList);

    // console.log(searchList);

    setIsSearching(false);
  };

  const toHome = () => {
    setStartdate("");
    setEnddate("");
    setKeyword([]);
    setSearchdata("");
  };

  return (
    <MotherBackground>
      {isLoading ? (
        <div>loading...</div>
      ) : (
        <>
          <Side>
            <SideBar data={dayrank} />
          </Side>
          <LogoArea onClick={toHome}>
            <Logo src={logo} />
          </LogoArea>
          {/* <LogoArea onClick={toHome}>버튼</LogoArea> */}
          <TopBar>
            <TopInput
              alltag={alltag}
              searchStart={setStartdate}
              searchEnd={setEnddate}
              searchTag={setKeyword}
            />
          </TopBar>
          {isSearching ? (
            <div>loading...</div>
          ) : (
            <>
              {searchdata ? (
                <>
                  <Graph1>
                    <BarGrahp data={searchBardata} name={"검색 결과의 합"} />
                  </Graph1>
                  <Graph2>
                    <LineGrahp
                      data={searchdata}
                      name={"날자별 검색 결과"}
                      type={0}
                    />
                  </Graph2>
                </>
              ) : (
                <>
                  <Graph1>
                    <BarGrahp data={daydata} name={"오늘의 검색순위"} />
                  </Graph1>
                  <Graph2>
                    <LineGrahp
                      data={weekdata}
                      name={"최근 7일 검색순위"}
                      type={0}
                    />
                  </Graph2>
                  <Graph3>
                    <LineGrahp
                      data={monthdata}
                      name={"최근 1개월 검색순위"}
                      type={0}
                    />
                  </Graph3>
                  <Graph4>
                    <LineGrahp
                      data={yeardata}
                      name={"최근 1년 검색순위"}
                      type={1}
                    />
                  </Graph4>
                </>
              )}
            </>
          )}
        </>
      )}
    </MotherBackground>
  );
}

const MotherBackground = styled.div`
  display: grid;
  grid-template-columns: 1fr 4fr;
  grid-template-areas:
    "logo topbar"
    "side graph1"
    "side graph2"
    "empty graph3"
    "empty graph4";
  width: 100%;
  word-break: keep-all;
  max-width: 1800px;

  @media ${(props) => props.theme.laptop} {
    grid-template-columns: 1fr;
    grid-template-areas:
      "logo"
      "topbar"
      "graph1"
      "graph2"
      "graph3"
      "graph4";
    width: 100%;
  }
`;
const Side = styled.div`
  display: flex;
  grid-area: side;
  background-color: white;
  margin-bottom: auto;

  @media ${(props) => props.theme.laptop} {
    display: none;
  }
`;
const Graph1 = styled.div`
  display: flex;
  grid-area: graph1;
  justify-content: center;
  align-items: center;
  min-height: 300px;
`;
const Graph2 = styled.div`
  display: flex;
  grid-area: graph2;
  justify-content: center;
  align-items: center;
  min-height: 300px;
`;
const Graph3 = styled.div`
  display: flex;
  grid-area: graph3;
  justify-content: center;
  align-items: center;
  min-height: 300px;
`;
const Graph4 = styled.div`
  display: flex;
  grid-area: graph4;
  justify-content: center;
  align-items: center;
  min-height: 300px;
  //
`;
// const GraphAll = styled.div`
//   display: flex;
//   grid-column-start: 2;
//   grid-column-end: 4;
//   grid-row-start: 2;
//   grid-row-end: 4;
//   justify-content: center;
//   align-items: center;
//   min-height: 600px;
//   @media ${(props) => props.theme.laptop} {
//     grid-column-start: 1;
//     grid-column-end: 3;
//     grid-row-start: 3;
//     grid-row-end: 5;
//   }
//   @media ${(props) => props.theme.tablet} {
//     grid-column-start: 1;
//     grid-column-end: 2;
//     grid-row-start: 3;
//     grid-row-end: 4;
//   }
//   @media ${(props) => props.theme.mobile} {
//     grid-column-start: 1;
//     grid-column-end: 2;
//     grid-row-start: 3;
//     grid-row-end: 4;
//   }
// `;
const TopBar = styled.div`
  display: flex;
  grid-area: topbar;
  justify-content: center;
  align-items: center;
`;
const LogoArea = styled.button`
  grid-area: logo;
  padding: 0;
  border: none;
  background-color: white;
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100px;
  @media ${(props) => props.theme.laptop} {
    height: 50px;
  }
`;
const Logo = styled.img`
  height: 90%;
  width: 90%;
  object-fit: contain;

  @media ${(props) => props.theme.laptop} {
    height: 100%;
    width: 10%;
  }

  @media ${(props) => props.theme.tablet} {
    height: 100%;
    width: 20%;
  }
`;

export default MainPage;
