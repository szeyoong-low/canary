import { type EChartsOption } from "echarts";
import { type Params, useLoaderData, useParams } from "react-router";
import { Chart } from "@/components";
import { demoTitles } from "@/shared/constants";
import { isDemoParams } from "@/shared/types";

export default function Demo() {
  const params: Params = useParams();
  if (!isDemoParams(params)) {
    throw new Error("Can't parse demo ID");
  }
  const demoID: number = parseInt(params.demoID, 10);
  if (Number.isNaN(demoID)) {
    throw new Error("Demo ID is an integer");
  }

  return (
    <div className="flex flex-col items-center">
      <div>
        <h2 className="page-title text-xl">{demoTitles[demoID]}</h2>
      </div>
      <Chart config={useLoaderData<EChartsOption>()} />
    </div>
  );
}
