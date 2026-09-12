import { useFetcher } from "react-router";
import { OptionCard } from "@/components";

export default function ReportCreation() {
  const fetcher = useFetcher();

  const isCreating: boolean = fetcher.state !== "idle";

  return (
    <div className="flex flex-col gap-y-5 items-center">
      <fetcher.Form method="post">
        <OptionCard type="submit" pending={isCreating}>
          {isCreating ? "Creating..." : "Create blank report"}
        </OptionCard>
      </fetcher.Form>

      <OptionCard type="button" disabled>
        Start from a template
      </OptionCard>
    </div>
  );
}
