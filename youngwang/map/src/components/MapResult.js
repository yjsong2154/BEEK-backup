import React from 'react';
import MapResultBox from './MapResultBox.js';
import styled from 'styled-components';

const MainBox = styled.div`
	display : flex;
	flex-direction : column;
	height : 55%;
	width : 100%;
	background-color : #faf099;
	max-width : 800px;
	justify-content:center;
	align-items:center;
`
const TextBox = styled.div`
	display : flex;
	height : 7%;
	width : 96%;
	align-items:center;
`

const ResultScroll = styled.div`
	height : 93%;
	width : 100%;
	overflow-y: auto;
	-ms-overflow-style: none;
	&::-webkit-scrollbar{
        display:none;
    }
`
const NoResult = styled.div`
	display : block;
	flex-direction : column;
	width : 94%;
	background-color : white;
	margin : auto;
	margin-bottom:5px;
	border : 2px solid brown;
	padding : 5px;
`
const TextBoxNoResult = styled.div`
	font-size : 17px;
	width : 100%;
	padding : 2px
`

function MapResult(props) {
	const result = props.result;
	const setId = props.setId;
	const setIsModalOn = props.setIsModalOn;

	return (
		<MainBox>
			<TextBox>검색 결과</TextBox>
			<ResultScroll>
			{result.length ? result.map((result) => {
				return (
					<MapResultBox
						name={result.company_name}
						add={result.address}
						phone={result.tel}
						kind={result.industrial_name}
						owner={result.owner}
						lat={result.latitude}
						lon={result.longitude}
						key={result.id}
						setId = {setId}
						setIsModalOn={setIsModalOn}
					/>
				);
			}):<NoResult><TextBoxNoResult>결과 없음</TextBoxNoResult></NoResult>}
			</ResultScroll>
		</MainBox>
	);
}

export default MapResult;
