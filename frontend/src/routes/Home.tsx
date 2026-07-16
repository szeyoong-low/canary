import { NavLink } from "react-router";
import { BounceLoader } from "react-spinners";
import { canaryThemeColour, demoTitles } from "@/shared/constants";

function DemoLinkedList({ demos }: { demos: string[] }) {
  return (
    <ul>
      {demos.map((title, i) => (
        <li key={i} className="flex items-center">
          <NavLink to={`/demo/${String(i)}`}>
            {({ isPending }) => (
              <span>
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
    <div>
      <p>Canary is here</p>
      <DemoLinkedList demos={demoTitles} />
    </div>
  );
}
