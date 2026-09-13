import { useState } from "react";
import { ArrowRight, Sparkles } from "lucide-react";
import { BounceLoader } from "react-spinners";
import { canaryThemeColour } from "@/shared/constants";
import { readPromptDraft, writePromptDraft } from "@/lib/promptDraft";

const PROMPT_FORM_FIELD: string = "prompt";

export default function Prompt({
  onSubmit,
  isPending,
}: {
  onSubmit: (prompt: string) => void;
  isPending: boolean;
}) {
  // Read once at mount (not on every render) and never set afterwards, so
  // the textarea stays uncontrolled and typing costs no re-renders
  const [restoredDraft] = useState(readPromptDraft);

  return (
    <div className="w-full">
      <AskCanary />

      <form
        className="PromptBox"
        onSubmit={(event) => {
          // Without a router form action, the browser would navigate away on
          // submit. The mutation owns the request instead.
          event.preventDefault();

          const formData = new FormData(event.currentTarget);
          const prompt: FormDataEntryValue | null =
            formData.get(PROMPT_FORM_FIELD);

          onSubmit(typeof prompt === "string" ? prompt : "");
        }}
      >
        <textarea
          className="PromptTextarea"
          name={PROMPT_FORM_FIELD}
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
          {!isPending ? (
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
      </form>
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
