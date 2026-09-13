import { useFetcher } from "react-router";
import { FilePlus2, LayoutTemplate } from "lucide-react";
import { OptionCard } from "@/components";

export default function ReportCreation() {
  const fetcher = useFetcher();

  const isCreating: boolean = fetcher.state !== "idle";

  return (
    <div className="flex flex-col items-center gap-y-10 px-6 py-16">
      <header className="flex flex-col items-center gap-y-2 text-center">
        <h2 className="PageHeading">Start a new report</h2>
        <p className="PageSubheading">
          Begin with a blank canvas, or leverage an existing report.
        </p>
      </header>

      <div className="flex flex-col md:flex-row items-stretch gap-4">
        <fetcher.Form method="post">
          <OptionCard type="submit" pending={isCreating} className="h-full">
            <span className="flex items-center gap-x-2">
              <FilePlus2 size={18} />
              {isCreating ? "Creating..." : "Blank report"}
            </span>
            <span className="OptionCardHint">Start from scratch</span>
          </OptionCard>
        </fetcher.Form>

        <OptionCard type="button" disabled>
          <span className="flex items-center gap-x-2">
            <LayoutTemplate size={18} />
            Start from existing report
          </span>
          <span className="OptionCardHint">Coming soon.</span>
        </OptionCard>
      </div>
    </div>
  );
}
