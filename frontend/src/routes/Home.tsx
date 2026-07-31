import { Link, NavLink } from "react-router";
import { BounceLoader } from "react-spinners";
import { canaryThemeColour, demoTitles } from "@/shared/constants";

function DemoLinkedList({ demos }: { demos: string[] }) {
  return (
    <ul className="list-disc">
      {demos.map((title: string, i: number) => (
        <li key={i}>
          <NavLink to={`/demo/${String(i)}`}>
            {({ isPending }: { isPending: boolean }) => (
              <span className="flex flex-row items-center">
                {title}
                {isPending && (
                  <BounceLoader
                    color={canaryThemeColour}
                    size={"1em"}
                    className="mx-2"
                  />
                )}
              </span>
            )}
          </NavLink>
        </li>
      ))}
    </ul>
  );
}

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
          Ask away{" "}
          <Link to="/demo/ask" className="text-theme font-medium">
            here
          </Link>
          !
        </p>
        <p>
          It is able to fetch third-party data and transform it into a variety
          of charts, including time series and treemaps.
        </p>
        <DemoLinkedList demos={demoTitles} />
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
