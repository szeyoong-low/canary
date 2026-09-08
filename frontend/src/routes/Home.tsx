import { Link } from "react-router";

export default function Home() {
  return (
    <div className="flex justify-center">
      <div className="mx-10 md:mx-0 md:w-175 flex flex-col gap-4 text-justify">
        <Hero />
        <CallToAction />
      </div>
    </div>
  );
}

function Hero() {
  return (
    <div className="font-(family-name:--title-font-family) font-medium">
      <h2>
        <span className="text-theme">Canary</span>
        <img src="favicon.svg" />
        <br />
        crystallises <br />
        chaos <br />
        into <br />
        charts
      </h2>
    </div>
  );
}

function CallToAction() {
  return (
    <div>
      <p>
        <span className="emphasis">Canary</span> is an agentic Jupyter Notebook
        for financial analysts.
      </p>
      <p>
        It turns your questions about market movements and trade flows into
        professional reports with compelling, elegant charts.
        <br />
      </p>
      <Link to="/report/1" className="emphasis">
        Create yours today
      </Link>
    </div>
  );
}
