export interface ClassNameProps {
  className?: string;
}

interface DemoParams {
  demoID: string;
}

export function isDemoParams(params: unknown): params is DemoParams {
  return (
    typeof params === "object" &&
    params !== null &&
    "demoID" in params &&
    typeof params.demoID === "string"
  );
}
