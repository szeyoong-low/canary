import { useAuth0 } from "@auth0/auth0-react";
import { Link } from "react-router";
import { BounceLoader } from "react-spinners";
import { canaryThemeColour, reportBrowserPath } from "@/shared/constants";
import { type ClassNameProps } from "@/shared/types";
import { mergeClassName } from "@/lib/mergeClassName";
import {
  type ReportPreview,
  type ReportPreviewFilters,
  reportPreviewsQueryOptions,
  type ReportPreviewPage,
} from "@/lib/reports";
import Chart from "./Chart";
import {
  useInfiniteQuery,
  type UseInfiniteQueryResult,
  type InfiniteData,
} from "@tanstack/react-query";

const ANY_GRANT: ReportPreviewFilters = {
  publiclyVisible: false,
  minimumReportRole: "viewer",
};

const THUMBNAIL_DIMENSIONS: string = "h-75 w-full";

const PUBLIC_ONLY: ReportPreviewFilters = {
  publiclyVisible: true,
  minimumReportRole: null,
};

function useReportPreviews(
  filters: ReportPreviewFilters,
): UseInfiniteQueryResult<InfiniteData<ReportPreviewPage>> {
  const { isAuthenticated } = useAuth0();

  return useInfiniteQuery(reportPreviewsQueryOptions(filters, isAuthenticated));
}

export default function ReportGallery({ className }: ClassNameProps) {
  const { isAuthenticated } = useAuth0();

  return (
    <div className={mergeClassName("flex flex-col gap-y-5 mb-5", className)}>
      {isAuthenticated && (
        <span>
          <hr className="SectionDivider" />
          <PreviewList
            heading="Your reports"
            filters={ANY_GRANT}
            emptyMessage="You have not been given access to any reports yet."
          />
        </span>
      )}

      <hr className="SectionDivider" />

      <PreviewList
        heading="Discover insights shared by others"
        filters={PUBLIC_ONLY}
        emptyMessage="No public reports have been published yet."
      />
    </div>
  );
}

function PreviewList({
  heading,
  filters,
  emptyMessage,
}: {
  heading: string;
  filters: ReportPreviewFilters;
  emptyMessage: string;
}) {
  const {
    data,
    isPending,
    isError,
    refetch,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
  } = useReportPreviews(filters);

  // The cache stores one entry per page fetched; the grid wants them as a
  // single run of cards.
  const previews: ReportPreview[] =
    data?.pages.flatMap((page) => page.previews) ?? [];

  return (
    <section className="flex flex-col gap-y-4">
      <h2 className="ReportTitle">{heading}</h2>

      {isPending && (
        <div className="flex justify-center py-10">
          <BounceLoader color={canaryThemeColour} />
        </div>
      )}

      {isError && (
        <div className="flex flex-col items-start gap-y-2">
          <p className="text-sm">These reports could not be loaded.</p>
          <button
            type="button"
            className="SlidingUnderline cursor-pointer text-sm"
            onClick={() => void refetch()}
          >
            Try again
          </button>
        </div>
      )}

      {!isPending && !isError && previews.length === 0 && (
        <p className="text-sm">{emptyMessage}</p>
      )}

      {previews.length > 0 && (
        <ul className="grid grid-cols-1 sm:grid-cols-2 gap-10">
          {previews.map((preview) => (
            <ReportCard key={preview.report_id} preview={preview} />
          ))}
        </ul>
      )}

      {/* Driven by `next_cursor` being non-null, so the button takes itself off
          the page once the last page is in. */}
      {hasNextPage && (
        <button
          type="button"
          disabled={isFetchingNextPage}
          onClick={() => void fetchNextPage()}
          className="SlidingUnderline self-center cursor-pointer disabled:cursor-progress mt-3"
        >
          {isFetchingNextPage ? "Loading..." : "Load more"}
        </button>
      )}
    </section>
  );
}

function ReportCard({ preview }: { preview: ReportPreview }) {
  return (
    <li>
      <Link
        to={`${reportBrowserPath}/${preview.report_id}`}
        className="HoverCard flex h-full flex-col gap-y-2 rounded-lg border border-(--border-color-primary) p-4 transition-colors hover:bg-(--background-color-secondary)"
      >
        {preview.chart !== null ? (
          // `pointer-events-none` so a click on the canvas reaches the link
          // instead of being taken by ECharts' own interaction layer.
          <div
            className={mergeClassName(
              THUMBNAIL_DIMENSIONS,
              "pointer-events-none",
            )}
          >
            <Chart config={preview.chart} />
          </div>
        ) : (
          <div
            className={mergeClassName(
              THUMBNAIL_DIMENSIONS,
              "flex items-center justify-center rounded-lg border border-dashed border-(--border-color-primary) opacity-50",
            )}
          >
            <span className="text-sm">No chart yet</span>
          </div>
        )}

        <span className="line-clamp-1 font-medium font-(family-name:--title-font-family)">
          {preview.title}
        </span>
        <span className="line-clamp-1 text-sm text-(--text-color-secondary)">
          {preview.authors.join(", ")}
        </span>
      </Link>
    </li>
  );
}
