import { useAuth0 } from "@auth0/auth0-react";
import { Collapsible } from "@base-ui/react/collapsible";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ChevronDown } from "lucide-react";
import { useParams } from "react-router";
import { BounceLoader } from "react-spinners";
import { ContentContainer, Prompt } from "@/components";
import { canaryThemeColour } from "@/shared/constants";
import {
  generateReportContent,
  reportQueryKey,
  reportQueryOptions,
  type ContentContainerType,
  type Report as ReportType,
} from "@/lib/reports";

export default function Report() {
  // Guaranteed by the route segment; the check only narrows the type.
  const { reportID } = useParams();
  if (!reportID) {
    throw new Error("Missing `reportID` route parameter.");
  }

  const { isAuthenticated } = useAuth0();

  // The component now owns fetching, so unlike with a route loader it must
  // render the pending and error states itself.
  const {
    data: report,
    isPending,
    isError,
    error,
  } = useQuery(reportQueryOptions(reportID));

  const queryClient = useQueryClient();

  const generate = useMutation({
    mutationFn: (prompt: string) => generateReportContent(reportID, prompt),

    // Writes the saved container straight into the cached report instead of
    // invalidating it
    onSuccess: (container: ContentContainerType) => {
      queryClient.setQueryData(
        reportQueryKey(reportID),
        (previous: ReportType | undefined) =>
          previous && {
            ...previous,
            content_containers: [...previous.content_containers, container],
          },
      );
    },
  });

  if (isPending) {
    return (
      <div className="flex justify-center py-20">
        <BounceLoader color={canaryThemeColour} />
      </div>
    );
  }

  if (isError) {
    throw error;
  }

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

        {isAuthenticated && (
          <Prompt
            onSubmit={(prompt: string) => {
              generate.mutate(prompt);
            }}
            isPending={generate.isPending}
          />
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
