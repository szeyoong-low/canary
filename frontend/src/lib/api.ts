import { type EChartsOption } from "echarts";
import { apiOrigin } from "@/lib/env";
import { AGENT_PATH, POST, PROMPT_FIELD } from "@/shared/constants";

const agentHeaders: Headers = new Headers({
  "Content-Type": "application/json",
});

export async function getChartFromPrompt({
  request,
}: {
  request: Request;
}): Promise<EChartsOption> {
  const form_data: FormData = await request.formData();

  const response: Response = await fetch(new URL(AGENT_PATH, apiOrigin), {
    method: POST,
    body: JSON.stringify({ prompt: form_data.get(PROMPT_FIELD) }),
    headers: agentHeaders,
  });

  if (!response.ok) {
    throw new Error(
      `Server error: ${String(response.status)}: ${response.statusText}`,
    );
  }

  // No validation will be done on the client's side. The backend is my own,
  // and output validation using Pydantic was already done there.
  return (await response.json()) as EChartsOption;
}
