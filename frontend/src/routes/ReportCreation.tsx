import { useFetcher } from "react-router";

export default function ReportCreation() {
  const fetcher = useFetcher();

  const isCreating: boolean = fetcher.state !== "idle";

  return (
    <div className="flex justify-center">
      <fetcher.Form method="post">
        <button
          type="submit"
          disabled={isCreating}
          className="rounded-xl border px-6 py-4 disabled:opacity-50"
        >
          {isCreating ? "Creating..." : "Create blank report"}
        </button>
      </fetcher.Form>
    </div>
  );
}
