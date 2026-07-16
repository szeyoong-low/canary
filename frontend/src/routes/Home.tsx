import { NavLink } from "react-router";
import { BounceLoader } from "react-spinners";
import { canaryThemeColour, demoTitles } from "@/shared/constants";

function DemoLinkedList({ demos }: { demos: string[] }) {
  return (
    <ul className="list-disc">
      {demos.map((title, i) => (
        <li key={i}>
          <NavLink to={`/demo/${String(i)}`}>
            {({ isPending }) => (
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
    <div className="mx-10 flex flex-col gap-4">
      <p><span className="text-theme font-medium">Canary's</span> vision is be an AI agent that turns users' questions 
        about finance, business, and economics into beautiful charts and
        insightful analysis.</p>
      <p>Currently, the backend is able to fetch third-party data and
        transform data into a variety of charts.</p>
      <DemoLinkedList demos={demoTitles} />
      <p>For the latest progress and upcoming features, see the <a href="https://github.com/szeyoong-low/canary" className="text-theme font-medium">GitHub repository</a>.</p>
    </div>
  );
}
