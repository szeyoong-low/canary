import { type ContentContainerType } from "@/lib/reports";
import Chart from "./Chart";

export default function ContentContainer({
  container,
}: {
  container: ContentContainerType;
}) {
  // Each block is rendered only if it is still there. A container outlives the
  // blocks it points at, so one of these being absent is an ordinary state.
  return (
    <section className="flex w-full flex-col items-center gap-y-3">
      {container.prose !== null && (
        <p className="w-full text-justify">{container.prose}</p>
      )}

      {container.chart !== null && (
        <Chart config={container.chart} className="w-full aspect-video" />
      )}
    </section>
  );
}
