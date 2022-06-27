import React from "react";
import { ResponsiveLine } from "@nivo/line";
import styled from "styled-components";

const MainField = styled.div`
  display: flex;
  width: 100%;
  justify-content: center;
  align-items: center;
  flex-direction: column;
  margin-bottom: 20px;
`;
const GraphField = styled.div`
  height: 400px;
  width: 95%;
  background-color: mintcream;
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

function LineGrahp(props) {
  const data = props.data;
  const name = props.name;
  const type = props.type;

  const axis = type
    ? null
    : {
        tickSize: 5,
        tickPadding: 5,
        tickRotation: 0,
      };

  return (
    <MainField>
      <Name>{name}</Name>
      <GraphField>
        <ResponsiveLine
          data={data}
          margin={{ top: 40, right: 140, bottom: 40, left: 60 }}
          xScale={{ type: "point" }}
          yScale={{
            type: "linear",
            min: "auto",
            max: "auto",
            stacked: false,
            reverse: true,
          }}
          colors={{ scheme: "set1" }}
          lineWidth={3}
          enableGridY={false}
          pointSize={1}
          pointColor={{ theme: "background" }}
          pointBorderWidth={2}
          pointBorderColor={{ from: "serieColor" }}
          pointLabelYOffset={-12}
          useMesh={true}
          enableSlices="x"
          crosshairType="x"
          sliceTooltip={({ slice }) => {
            // console.log(slice.points[0].data.x)
            return (
              <div
                style={{
                  background: "rgba(255, 255, 255, 0.9)",
                  padding: "9px 12px",
                  border: "1px solid #ccc",
                }}
              >
                <div>&lt;{slice.points[0].data.x}&gt; count 횟수</div>
                {slice.points.map((point) =>
                  point.data.count ? (
                    <div
                      key={point.id}
                      style={{
                        color: point.serieColor,
                        padding: "3px 0",
                      }}
                    >
                      <div>
                        {point.serieId} : {point.data.count} 회
                      </div>
                    </div>
                  ) : null
                )}
              </div>
            );
          }}
          axisTop={null}
          axisRight={null}
          axisBottom={axis}
          axisLeft={{
            tickSize: 5,
            tickPadding: 5,
            tickRotation: 0,
            tickValues: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            // legend: name,
            // legendPosition: 'middle',
            // legendOffset: -40
          }}
          legends={[
            {
              anchor: "bottom-right",
              direction: "column",
              justify: false,
              translateX: 100,
              translateY: 0,
              itemsSpacing: 0,
              itemDirection: "left-to-right",
              itemWidth: 80,
              itemHeight: 20,
              itemOpacity: 0.75,
              symbolSize: 12,
              symbolShape: "circle",
              symbolBorderColor: "rgba(0, 0, 0, .5)",
              effects: [
                {
                  on: "hover",
                  style: {
                    itemBackground: "rgba(0, 0, 0, .03)",
                    itemOpacity: 1,
                  },
                },
              ],
            },
          ]}
        />
      </GraphField>
    </MainField>
  );
}

export default LineGrahp;
