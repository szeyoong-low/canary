import { useState } from "react";
import { type EChartsOption } from "echarts";
import { ArrowRight, Sparkles } from "lucide-react";
import { type FetcherWithComponents } from "react-router";
import { BounceLoader } from "react-spinners";
import { canaryThemeColour, PROMPT_FIELD } from "@/shared/constants";
import { readPromptDraft, writePromptDraft } from "@/lib/promptDraft";

export default function Prompt({
  fetcher,
}: {
  fetcher: FetcherWithComponents<EChartsOption>;
}) {
  // Read once at mount (not on every render) and never set afterwards, so
  // the textarea stays uncontrolled and typing costs no re-renders
  const [restoredDraft] = useState(readPromptDraft);

  return (
    <div className="w-full">
      <AskCanary />

      <fetcher.Form method="POST" className="PromptBox">
        <textarea
          className="PromptTextarea"
          name={PROMPT_FIELD}
          placeholder="What are you curious about?"
          // Restores a draft left behind by a sign-in redirect
          defaultValue={restoredDraft}
          // Saved as it is typed, because the redirect can be triggered from the
          // header's sign-in button as well as from submitting.
          onChange={(event) => {
            writePromptDraft(event.target.value);
          }}
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
    </div>
  );
}

function AskCanary() {
  return (
    <div className="flex gap-x-2 items-center py-2">
      <p className="page-title text-xl">Ask Canary</p>
      <Sparkles className="text-theme" />
    </div>
  );
}
