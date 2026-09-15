import { useEffect, useRef } from "react";
import { type ContentContainerType } from "@/lib/reports";
import Chart from "./Chart";

const REDUCED_MOTION_QUERY: string = "(prefers-reduced-motion: reduce)";

export default function ContentContainer({
  container,
  shouldFocus = false,
}: {
  container: ContentContainerType;
  shouldFocus?: boolean;
}) {
  const section = useRef<HTMLElement>(null);

  // Runs after React has committed this section to the DOM, which is why the
  // focusing lives here rather than in the mutation's `onSuccess` (at that
  // point the node does not exist yet).
  useEffect(() => {
    if (!shouldFocus || !section.current) {
      return;
    }

    // Focus first, so a keyboard user's next Tab continues from the new
    // content and screen readers move here. `preventScroll` suppresses the
    // instant jump `focus` would otherwise do, leaving the scroll below in
    // charge of how it looks.
    section.current.focus({ preventScroll: true });

    const prefersReducedMotion: boolean =
      window.matchMedia(REDUCED_MOTION_QUERY).matches;

    section.current.scrollIntoView({
      behavior: prefersReducedMotion ? "auto" : "smooth",
      block: "start",
    });
  }, [shouldFocus]);

  // Each block is rendered only if it is still there. A container outlives the
  // blocks it points at, so one of these being absent is an ordinary state.
  return (
    <section
      ref={section}
      // Focusable by script but not by Tab, so the section does not become an
      // extra stop in the tab order for everyone else.
      tabIndex={-1}
      // The scroll margin clears the sticky nav, which would otherwise cover
      // the top of this section, plus a little breathing room.
      className="flex w-full scroll-mt-[calc(var(--header-height)+1.25rem)] flex-col items-center gap-y-3 outline-none"
    >
      {container.prose !== null && (
        <p className="w-full text-justify">{container.prose}</p>
      )}

      {container.chart !== null && (
        <div className="min-h-100 w-full aspect-video">
          <Chart config={container.chart} />
        </div>
      )}
    </section>
  );
}
