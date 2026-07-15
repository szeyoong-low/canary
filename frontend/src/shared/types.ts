interface TitleHandle {
  title: string;
}

export function isTitleHandle(handle: unknown): handle is TitleHandle {
  return (
    typeof handle === "object" &&
    handle !== null &&
    "title" in handle &&
    typeof handle.title === "string"
  );
}

export interface ClassNameProps {
  className?: string;
}
