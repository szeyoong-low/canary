import { useAuth0 } from "@auth0/auth0-react";
import { Collapsible } from "@base-ui/react/collapsible";
import { type EChartsOption } from "echarts";
import { ChevronDown } from "lucide-react";
import {
  type FetcherWithComponents,
  useFetcher,
  useLoaderData,
} from "react-router";
import { Chart, ContentContainer, Prompt } from "@/components";
import { type getFullReport } from "@/lib/reports";

export default function Report() {
  // The route loader has already resolved before this renders, so the report
  // is always present. No loading branch is needed.
  const report = useLoaderData<typeof getFullReport>();

  const fetcher: FetcherWithComponents<EChartsOption> =
    useFetcher<EChartsOption>();
  const { isAuthenticated } = useAuth0();

  return (
    <div className="flex justify-center">
      <div className="mx-10 sm:w-150 md:w-175 flex flex-col items-center gap-y-5">
        <Masthead title={report.title} authors={report.authors} />

        {report.content_containers.map((container) => (
          <ContentContainer
            key={container.container_id}
            container={container}
          />
        ))}

        <PreviewDisclaimer />

        {fetcher.data === undefined ? (
          isAuthenticated && <Prompt fetcher={fetcher} />
        ) : (
          <Chart config={fetcher.data} />
        )}
      </div>
    </div>
  );
}

function Masthead({ title, authors }: { title: string; authors: string[] }) {
  return (
    <header className="w-full flex flex-col items-center">
      <h2 className="text-xl font-medium ReportTitle">{title}</h2>
      <p className="text-sm opacity-70">{authors.join(", ")}</p>
    </header>
  );
}

function PreviewDisclaimer() {
  return (
    <Collapsible.Root
      defaultOpen
      className="w-full rounded-lg bg-(--background-color-secondary) px-4 py-3"
    >
      <Collapsible.Trigger className="group flex w-full cursor-pointer items-center justify-between gap-x-2 text-left text-sm font-medium">
        What Canary can answer
        <ChevronDown
          size="1.25em"
          className="transition-transform duration-(--transition-delay) group-data-panel-open:rotate-180"
        />
      </Collapsible.Trigger>

      <Collapsible.Panel className="flex flex-col gap-y-3 pt-3 text-sm opacity-70">
        <p>
          This preview supports a limited selection of analysis. These examples
          are representative of what the agent can handle:
        </p>

        <ul className="flex list-disc flex-col gap-y-2 ps-5">
          <li>
            "Give me Apple's closing share price from January to March 2026."
          </li>
          <li>
            "Show me the daily returns on Apple's stock price as well as the
            volatility of this over a 5-day window in January 2026."
          </li>
          <li>
            "Compare the opening prices of Apple, Google, Microsoft, Nvidia,
            Tesla, JP Morgan, and Bank of America from January to March 2026. I
            want to use an index from the first trading day."
          </li>
          <li>
            "Break down the market capitalisation of all public companies by
            sector, industry, then company, and show it in a treemap."
          </li>
        </ul>
      </Collapsible.Panel>
    </Collapsible.Root>
  );
}
