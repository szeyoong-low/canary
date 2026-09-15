import {
  isRouteErrorResponse,
  useRouteError,
  useNavigate,
  Link,
} from "react-router";

export default function ErrorBoundary() {
  const error: unknown = useRouteError();

  if (isRouteErrorResponse(error)) {
    return (
      <ErrorCard
        title={`${String(error.status)} ${error.statusText}`}
        description={String(error.data)}
      />
    );
  } else if (error instanceof Error) {
    return <ErrorCard description={error.message} />;
  } else {
    return <ErrorCard />;
  }
}

function ErrorCard({
  title,
  description,
}: {
  title?: string;
  description?: string;
}) {
  const navigate = useNavigate();

  return (
    <div className="flex items-center justify-center px-4 mt-8">
      <div className="flex min-w-3xs max-w-xl flex-col gap-5 rounded-lg border border-(--border-color-primary) p-6">
        <h2 className="ReportTitle">{title ?? "Error"}</h2>
        <p className="text-justify">{description ?? ""}</p>

        <hr className="" />

        <div className="flex flex-col items-start gap-3">
          <button
            className="SlidingUnderline font-medium"
            onClick={() => void navigate(-1)}
          >
            Previous page
          </button>
          <Link to="/" className="SlidingUnderline">
            Home
          </Link>
        </div>
      </div>
    </div>
  );
}
