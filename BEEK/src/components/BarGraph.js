import React from "react";
import { ResponsiveBar } from "@nivo/bar";
import styled from "styled-components";

const GraphField = styled.div`
  height: 300px;
  width: 95%;
  background-color: mintcream;
`;
const MainField = styled.div`
  display: flex;
  width: 100%;
  justify-content: center;
  align-items: center;
  flex-direction: column;
  margin-bottom: 20px;
  margin-top: 20px;
`;
const Name = styled.div`
  height: 20px;
  width: 95%;
  text-align: center;
  padding-top: 10px;
  padding-bottom: 10px;
  font-weight: bold;
  background-color: blue;
  color: yellow;
`;

function BarGrahp(props) {
  const data = props.data;
  const name = props.name;
  // console.log(data)

  return (
    <MainField>
      <Name>{name}</Name>
      <GraphField>
        <ResponsiveBar
          data={data}
          keys={["count"]}
          indexBy="name"
          margin={{ top: 50, right: 130, bottom: 70, left: 60 }}
          padding={0.25}
          groupMode="grouped"
          valueScale={{ type: "linear" }}
          indexScale={{ type: "band", round: true }}
          colors={{ scheme: "nivo" }}
          defs={[
            {
              id: "dots",
              type: "patternDots",
              background: "inherit",
              color: "#38bcb2",
              size: 4,
              padding: 1,
              stagger: true,
            },
            {
              id: "lines",
              type: "patternLines",
              background: "inherit",
              color: "#eed312",
              rotation: -45,
              lineWidth: 6,
              spacing: 10,
            },
          ]}
          borderColor={{ from: "color", modifiers: [["darker", "1.7"]] }}
          axisTop={null}
          axisRight={null}
          axisLeft={{
            tickSize: 5,
            tickPadding: 5,
            tickRotation: 0,
          }}
          axisBottom={{
            tickSize: 5,
            tickPadding: 5,
            tickRotation: 45,
          }}
          labelSkipWidth={27}
          labelSkipHeight={12}
          labelTextColor={{ from: "color", modifiers: [["darker", 1.6]] }}
          legends={[
            {
              dataFrom: "keys",
              anchor: "bottom-right",
              direction: "column",
              justify: false,
              translateX: 112,
              translateY: 0,
              itemsSpacing: 2,
              itemWidth: 94,
              itemHeight: 20,
              itemDirection: "left-to-right",
              itemOpacity: 0.85,
              symbolSize: 16,
              effects: [
                {
                  on: "hover",
                  style: {
                    itemOpacity: 1,
                  },
                },
              ],
            },
          ]}
          role="application"
          ariaLabel="Nivo bar chart demo"
          barAriaLabel={function (e) {
            return (
              e.id + ": " + e.formattedValue + " in country: " + e.indexValue
            );
          }}
          animate={false}
        />
      </GraphField>
    </MainField>
  );
}

export default BarGrahp;
