import { Link } from "react-router";
import { ArrowRight } from "lucide-react";
import { reportBrowserPath } from "@/shared/constants";
import { ReportGallery } from "@/components";

export default function Home() {
  return (
    <div className="flex flex-col items-center gap-4">
      <div className="mx-10 md:mx-0 md:w-175 flex flex-col gap-4 text-justify">
        <Hero />
        {/* <hr className="SectionDivider" /> */}
        <CallToAction />
      </div>

      <ReportGallery className="w-full max-w-250 px-10" />
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
        movements into compelling, elegant reports that readers can engage with.
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
