import React, { useState } from "react";
import styled from "styled-components";
import Select from "react-select";

function filter(alltag) {
  var option = [];

  for (var item of alltag) {
    var dic = {};
    dic["value"] = item.name;
    dic["label"] = item.name;
    option.push(dic);
  }

  return option;
}

function TopInput(props) {
  // const selectAllOption = {
  //     value: "<SELECT_ALL>",
  //     label: "모든 키워드 검색"
  // };
  const alltag = props.alltag;
  const options = filter(alltag);
  // const getOptions = () => [selectAllOption, ...options];

  const yester = new Date();
  yester.setDate(yester.getDate() - 1);
  const yesterdate = `${yester.getFullYear()}-${
    yester.getMonth() + 1
  }-${yester.getDate()}`;
  const twoday = new Date();
  twoday.setDate(twoday.getDate() - 2);
  const twodaydate = `${twoday.getFullYear()}-${
    twoday.getMonth() + 1
  }-${twoday.getDate()}`;

  const [startdate, setStartdate] = useState(twodaydate);
  const [enddate, setEnddate] = useState(yesterdate);
  const [keyword, setKeyword] = useState([]);

  const handleChangeStart = (e) => {
    setStartdate(e.target.value);
  };
  const handleChangeEnd = (e) => {
    setEnddate(e.target.value);
  };
  const handleChangeTag = (e) => {
    setKeyword(e);
  };
  const handleClick = (e) => {
    const regex = /\d{4}-\d{1,2}-\d{1,2}/;
    // if(keyword.length === 0){
    //     alert('키워드 입력값이 없습니다.')
    // }else
    if (!(regex.test(startdate) && regex.test(enddate))) {
      alert("날짜 입력이 잘못되었습니다. \nyyyy-mm-dd 형식으로 입력해 주세요.");
    } else if (Date.parse(enddate) - Date.parse(startdate) > 31536000001) {
      alert("검색 범위를 1년 이내로 해주세요.");
    } else if (Date.parse(enddate) - Date.parse(startdate) < 1) {
      alert("검색 범위가 잘못되었습니다.");
    } else {
      props.searchStart(startdate);
      props.searchEnd(enddate);
      props.searchTag(keyword);
    }
  };
  const weekClick = (e) => {
    const week = new Date();
    week.setDate(week.getDate() - 7);
    const weekdate = `${week.getFullYear()}-${
      week.getMonth() + 1
    }-${week.getDate()}`;
    setStartdate(weekdate);
  };
  const monthClick = (e) => {
    const month = new Date();
    month.setMonth(month.getMonth() - 1);
    const monthdate = `${month.getFullYear()}-${
      month.getMonth() + 1
    }-${month.getDate()}`;
    setStartdate(monthdate);
  };
  const monthsixClick = (e) => {
    const monthsix = new Date();
    monthsix.setMonth(monthsix.getMonth() - 6);
    const monthsixdate = `${monthsix.getFullYear()}-${
      monthsix.getMonth() + 1
    }-${monthsix.getDate()}`;
    setStartdate(monthsixdate);
  };
  const yearClick = (e) => {
    const year = new Date();
    year.setFullYear(year.getFullYear() - 1);
    const yeardate = `${year.getFullYear()}-${
      year.getMonth() + 1
    }-${year.getDate()}`;
    setStartdate(yeardate);
  };
  const customStyles = {
    control: (provided, state) => ({
      ...provided,
      background: "#fff",
      borderColor: "#9e9e9e",
      minHeight: "60px",
      height: "66px",
      boxShadow: state.isFocused ? null : null,
    }),
    valueContainer: (provided, state) => ({
      ...provided,
      height: "60px",
      padding: "0 6px",
      overflow: "auto",
      scrollbarWidth: "none",
      MsOverflowStyle: "none",
      "::-webkit-scrollbar": {
        display: "none",
      },
    }),
    input: (provided, state) => ({
      ...provided,
      margin: "0px",
    }),
    indicatorSeparator: (state) => ({
      display: "none",
    }),
    indicatorsContainer: (provided, state) => ({
      ...provided,
      height: "30px",
    }),
  };
  const isOptionSelected = (option) => {
    console.log(option);
    return false;
  };

  return (
    <MainField>
      <Margin>
        <DateInputField>
          <DateInput>
            <DateField
              type="text"
              value={startdate}
              onChange={handleChangeStart}
              placeholder={yesterdate}
            />{" "}
            부터
            <DateField
              type="text"
              value={enddate}
              onChange={handleChangeEnd}
              placeholder={yesterdate}
            />{" "}
            까지
          </DateInput>
          <DateButtons>
            <DateButton onClick={weekClick}>최근 1주</DateButton>
            <DateButton onClick={monthClick}>최근 1달</DateButton>
            <DateButton onClick={monthsixClick}>최근 6달</DateButton>
            <DateButton onClick={yearClick}>최근 1년</DateButton>
          </DateButtons>
        </DateInputField>
        <TagInput>
          <ForWidth>
            <Select
              defaultValue={[]}
              placeholder={"키워드 검색 (입력이 없으면 모두 검색)"}
              options={options}
              isMulti
              name="colors"
              className="basic-multi-select"
              classNamePrefix="select"
              onChange={handleChangeTag}
              closeMenuOnSelect={false}
              styles={customStyles}
              hideSelectedOptions={false}
              // isOptionSelected={isOptionSelected}
            />
          </ForWidth>
        </TagInput>
        <InputButton onClick={handleClick}>검색 하기</InputButton>
      </Margin>
    </MainField>
  );
}

const MainField = styled.div`
  display: flex;
  height: 100%;
  width: 100%;
  background-color: skyblue;
  justify-content: center;
  align-items: center;
`;
const Margin = styled.div`
  display: flex;
  height: 100%;
  width: 98%;
  justify-content: center;
  align-items: center;

  @media ${(props) => props.theme.mobile} {
    flex-direction: column;
  }
`;
const DateInputField = styled.div`
  display: flex;
  height: 100%;
  width: 45%;
  justify-content: center;
  align-items: center;
  flex-direction: column;
  min-height: 100px;
  @media ${(props) => props.theme.mobile} {
    width: 90%;
  }
`;
const DateInput = styled.div`
  display: flex;
  height: 50%;
  width: 100%;
  justify-content: center;
  align-items: center;
`;
const DateField = styled.input`
  width: 35%;
`;
const DateButtons = styled.div`
  display: flex;
  height: 50%;
  width: 100%;
  justify-content: space-around;
  align-items: center;
`;
const DateButton = styled.button`
  height: 70%;
  width: 20%;
  align-items: center;
  border-radius: 4px;
  background-color: aliceblue;
  @media ${(props) => props.theme.mobile} {
    width: 25%;
  }
`;
const TagInput = styled.div`
  display: flex;
  height: 100%;
  width: 45%;
  justify-content: center;
  align-items: center;
  @media ${(props) => props.theme.mobile} {
    width: 95%;
  }
`;
const InputButton = styled.button`
  position: relative;
  display: inline-block;
  padding: 0.25em 0.5em;
  text-decoration: none;
  color: #fff;
  background: #fd9535; /*button color*/
  border-bottom: solid 2px #d27d00; /*daker color*/
  border-radius: 4px;
  box-shadow: inset 0 2px 0 rgba(255, 255, 255, 0.2),
    0 2px 2px rgba(0, 0, 0, 0.19);
  font-weight: bold;

  width: 10%;
  height: 50%;
  justify-content: center;
  align-items: center;

  &:active {
    border-bottom: solid 2px #fd9535;
    box-shadow: 0 0 2px rgba(0, 0, 0, 0.3);
  }
  @media ${(props) => props.theme.mobile} {
    width: 70%;
    margin-bottom: 5%;
  }
`;
const ForWidth = styled.div`
  width: 90%;
  margin: 10px auto;
`;

export default TopInput;
