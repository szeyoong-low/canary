import { ArrowRight } from "lucide-react";
import { useFetcher } from "react-router";
import { BounceLoader } from "react-spinners";
import { canaryThemeColour } from "@/shared/constants";

export default function Prompt() {
  let fetcher = useFetcher();
  return (
    <fetcher.Form method="POST" className="PromptBox">
      <textarea
        className="PromptTextarea"
        name="prompt"
        placeholder="Ask a question here"
      />
      <div className="PromptSubmit">
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
