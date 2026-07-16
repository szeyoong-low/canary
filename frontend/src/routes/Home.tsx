import { Link } from "react-router";
import { demoTitles } from "@/shared/constants";

function DemoLinkedList({demos}: {demos: string[]}) {
  return (
    <ul>
      {demos.map((title, i) => (
        <li key={i}>
          <Link to={`/demo/${i}`}>{title}</Link>
        </li>
      ))}
    </ul>
  );
}

export default function Home() {
  return (
    <div>
      <p>Canary is here</p>
      <DemoLinkedList demos={demoTitles}/>
    </div>
  );
}
