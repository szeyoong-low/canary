import { Link } from "react-router";

export default function Home() {
  return (
    <div className="flex justify-center">
      <div className="mx-10 md:mx-0 md:w-175 flex flex-col gap-4 text-justify">
        <p>
          <span className="emphasis">Canary's</span> vision is to be an agentic
          Jupyter notebook for financial analysts. It turns your questions about
          market movements and trade flows into professional reports with{" "}
          <Link to="/report/1" className="emphasis">
            beautiful charts
          </Link>{" "}
          and insightful analysis.
        </p>
      </div>
    </div>
  );
}
