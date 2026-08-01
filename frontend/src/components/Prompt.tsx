import { ArrowRight } from "lucide-react";
import { type FetcherWithComponents } from "react-router";
import { BounceLoader } from "react-spinners";
import { canaryThemeColour, PROMPT_FIELD } from "@/shared/constants";

export default function Prompt({
  fetcher,
}: {
  fetcher: FetcherWithComponents<any>;
}) {
  return (
    <fetcher.Form method="POST" className="PromptBox">
      <textarea
        className="PromptTextarea"
        name={PROMPT_FIELD}
        placeholder="Ask a question here"
      />
      <div className="self-end">
        {fetcher.state === "idle" ? (
          <button className="cursor-pointer" type="submit">
            <ArrowRight />
          </button>
        ) : (
          <BounceLoader
            color={canaryThemeColour}
            size={"1em"}
            className="cursor-progress mx-2"
          />
        )}
      </div>
    </fetcher.Form>
  );
}
