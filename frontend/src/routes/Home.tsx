import { Link } from "react-router";
import { ArrowRight, TriangleAlert } from "lucide-react";
import { reportBrowserPath } from "@/shared/constants";
import { ReportGallery } from "@/components";

export default function Home() {
  return (
    <div className="flex flex-col items-center gap-4">
      <div className="mx-10 md:mx-0 md:w-175 flex flex-col gap-4 text-justify">
        <DeprecationBanner />
        <Hero />
        {/* <hr className="SectionDivider" /> */}
        <CallToAction />
      </div>

      <ReportGallery className="w-full max-w-250 px-10" />
    </div>
  );
}

function DeprecationBanner() {
  return (
    <div
      role="note"
      className="flex w-full items-center gap-x-3 rounded-lg bg-(--background-color-secondary) px-5 py-4 text-base font-medium"
    >
      {/* shrink-0 stops the icon from being squashed when the text wraps */}
      <TriangleAlert size="1.5em" className="shrink-0" />
      {/* Wrapped in <p> so the text and link flow as one flex item */}
      <p>
        Canary has been deprecated: read{" "}
        <a
          href="https://github.com/szeyoong-low/canary/wiki/Deprecation"
          className="underline"
        >
          here
        </a>{" "}
        to learn more.
      </p>
    </div>
  );
}

function Hero() {
  return (
    <div className="Hero">
      <h2>
        <div className="HeroBrandName flex items-center">
          <span className="text-theme">Canary</span>
          <span className="HeroBird" />
        </div>
        <span>
          crystallises chaos{" "}
          <span className="md:hidden">
            <br />
          </span>{" "}
          into charts.
        </span>
      </h2>
    </div>
  );
}

function CallToAction() {
  return (
    <div className="flex flex-col gap-3">
      <p>
        Leverage an agentic Jupyter Notebook to turn your instincts about market
        movements into compelling, elegant, and interactive reports that readers
        can engage with.
      </p>
      <div className="CallToAction">
        <div className="SlidingUnderline">
          <Link to={reportBrowserPath}>
            Make your best case today <ArrowRight className="inline" />
          </Link>
        </div>
      </div>
    </div>
  );
}
