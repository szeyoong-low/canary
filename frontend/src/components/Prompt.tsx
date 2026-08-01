import { ArrowRight } from "lucide-react";
import { useFetcher } from "react-router";

export default function Prompt() {
  let fetcher = useFetcher();
  return (
    <fetcher.Form method="POST" action="" className="PromptBox">
      <textarea
        className="PromptTextarea"
        name="prompt"
        placeholder="Ask a question here"
      />
      <button className="PromptSubmit" type="submit">
        <ArrowRight />
      </button>
    </fetcher.Form>
  );
}
