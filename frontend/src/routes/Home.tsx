export default function Home() {
  return (
    <div className="flex justify-center">
      <div className="mx-10 md:mx-0 md:w-175 flex flex-col gap-4 text-justify">
        <p>
          <span className="text-theme font-medium">Canary's</span> vision is to
          be an agentic Jupyter notebook for financial analysts. It turns your
          questions about market movements and trade flows into professional
          reports with beautiful charts and insightful analysis.
        </p>
        <p>
          For the latest progress and upcoming features, see the{" "}
          <a
            href="https://github.com/szeyoong-low/canary"
            className="text-theme font-medium"
          >
            GitHub repository
          </a>
          .
        </p>
      </div>
    </div>
  );
}
