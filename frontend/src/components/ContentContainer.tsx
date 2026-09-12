import { type ContentContainerType } from "@/lib/reports";
import Chart from "./Chart";

export default function ContentContainer({
  container,
}: {
  container: ContentContainerType;
}) {
  return (
    <section className="flex w-full flex-col items-center gap-y-3">
      <p className="w-full text-sm">{container.prose}</p>

      <Chart config={container.chart} className="w-full" />
    </section>
  );
}
