import React from 'react';
import styled from 'styled-components';

const MainBox = styled.button`
	display : block;
	flex-direction : column;
	width : 94%;
	background-color : white;
	margin : auto;
	margin-bottom:5px;
	border : 2px solid brown;
	padding : 5px;
	&:hover{
		opacity : 0.9;
	}
	&:active{
		transform: scale(0.98);
	}
`

const TextBox = styled.div`
	text-align : left;
	font-size : 17px;
	width : 100%;
	padding : 2px
`

function MapResultBox(props) {
	const setId = props.setId;
	const setIsModalOn = props.setIsModalOn;
	const phone = (props.phone ? props.phone : '정보 없음')

	const onClick = () => {
		setIsModalOn(true);
		setId([props.name, props.add, phone, props.kind,props.owner,props.lat,props.lon])
	}

	return (
		<MainBox onClick = {onClick}>
			<TextBox>이름 : {props.name} </TextBox>
			<TextBox>주소 : {props.add}</TextBox>
			<TextBox>전화번호 : {phone}</TextBox>
		</MainBox>
	);
}

export default MapResultBox;
