import { Link } from "react-router";

export default function Home() {
  return (
    <div className="flex justify-center">
      <div className="mx-10 md:mx-0 md:w-175 flex flex-col gap-4 text-justify">
        <Hero />
        <hr className="SectionDivider" />
        <CallToAction />
      </div>
    </div>
  );
}

function Hero() {
  return (
    <div className="Hero">
      <h2>
        <div className="flex items-center">
          <span className="text-theme">Canary</span>
          <img src="favicon.svg" alt="" className="HeroBird" />
        </div>
        crystallises <br />
        chaos <br />
        into <br />
        charts.
      </h2>
    </div>
  );
}

function CallToAction() {
  return (
    <div className="flex flex-col gap-2">
      <p>
        <span className="emphasis">Canary</span> is an agentic Jupyter Notebook
        for financial analysts.
      </p>
      <p>
        It turns your questions about market movements and trade flows into
        professional reports with compelling, elegant charts.
      </p>
      <Link to="/report/1" className="CallToAction">
        Create yours today
      </Link>
    </div>
  );
}
