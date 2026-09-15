import { Collapsible } from "@base-ui/react/collapsible";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  ChevronDown,
  Eye,
  EyeOff,
  Trash2,
  type LucideIcon,
} from "lucide-react";
import { useState } from "react";
import { useNavigate, useParams } from "react-router";
import { BounceLoader } from "react-spinners";
import { ConfirmDialog, ContentContainer, Prompt } from "@/components";
import { canaryThemeColour } from "@/shared/constants";
import { APIError, hasAtLeastRole, type ReportRole } from "@/shared/types";
import {
  generateReportContent,
  reportQueryKey,
  reportQueryOptions,
  renameReport,
  updateReportVisibility,
  deleteReport,
  REPORT_PREVIEWS_QUERY_KEY_PREFIX,
  type ContentContainerType,
  type Report as ReportType,
} from "@/lib/reports";
import { toast } from "@/lib/toast";

const EDIT_ROLE: ReportRole = "editor";
const OWNER_ROLE: ReportRole = "owner";

const FORBIDDEN: number = 403;

const TITLE_FORM_FIELD: string = "title";

const HOME_PATH: string = "/";

export default function Report() {
  // Guaranteed by the route segment; the check only narrows the type.
  const { reportID } = useParams();
  if (!reportID) {
    throw new Error("Missing `reportID` route parameter.");
  }

  // The component now owns fetching, so unlike with a route loader it must
  // render the pending and error states itself.
  const {
    data: report,
    isPending,
    isError,
    error,
  } = useQuery(reportQueryOptions(reportID));

  const queryClient = useQueryClient();
  const navigate = useNavigate();

  // The container the page should jump to once it renders. Naming the target
  // rather than assuming it is the last one keeps this working if containers
  // ever arrive out of order or get removed.
  // Starting at `null` means nothing steals focus on a first visit.
  const [containerToFocus, setContainerToFocus] = useState<string | null>(null);

  const generate = useMutation({
    mutationFn: (prompt: string) => generateReportContent(reportID, prompt),
    meta: { errorTitle: "Could not answer this prompt" },

    // Writes the saved container straight into the cached report instead of
    // invalidating it
    onSuccess: ({
      container,
      role,
    }: {
      container: ContentContainerType;
      role: ReportRole | null;
    }) => {
      queryClient.setQueryData(
        reportQueryKey(reportID),
        (previous: ReportType | undefined) =>
          previous && {
            ...previous,
            role,
            content_containers: [...previous.content_containers, container],
          },
      );

      setContainerToFocus(container.container_id);
    },

    onError: (error: Error) => {
      resyncIfForbidden(error);
    },
  });

  // Both metadata endpoints answer 204. Optimistic update: the cache is patched
  // before the request goes out and rolled back if it fails.
  const patchCachedReport = (
    patch: Partial<ReportType>,
  ): ReportType | undefined => {
    const previous: ReportType | undefined = queryClient.getQueryData(
      reportQueryKey(reportID),
    );

    queryClient.setQueryData(
      reportQueryKey(reportID),
      (report: ReportType | undefined) => report && { ...report, ...patch },
    );

    return previous; // Handed to `onError` as its third argument
  };

  // The `onMutate` form. A background refetch already in flight could land
  // after this patch but before the write succeeds, overwriting it with
  // pre-edit server state, so it is cancelled first. TanStack Query awaits
  // `onMutate`, and awaits the snapshot it resolves to before `onError`.
  const patchCachedReportAfterCancelling = async (
    patch: Partial<ReportType>,
  ): Promise<ReportType | undefined> => {
    await queryClient.cancelQueries({ queryKey: reportQueryKey(reportID) });

    return patchCachedReport(patch);
  };

  const rollBack = (previous: ReportType | undefined) => {
    queryClient.setQueryData(reportQueryKey(reportID), previous);
  };

  // A 403 means the cached role is out of date: the grant was changed by
  // someone else after this page last heard from the backend. Refetching is the
  // one case where this page wants a revalidation, because the alternative is
  // leaving a control on screen that can only keep failing.
  const resyncIfForbidden = (error: Error) => {
    if (error instanceof APIError && error.status === FORBIDDEN) {
      void queryClient.invalidateQueries({
        queryKey: reportQueryKey(reportID),
      });
    }
  };

  const rename = useMutation({
    mutationFn: (newTitle: string) => renameReport(reportID, newTitle),
    // The rollback below is silent on its own, so the failure has to be
    // announced. The toast itself is raised globally in `queryClient.ts`.
    meta: { errorTitle: "Could not rename this report" },
    onMutate: (newTitle: string) =>
      patchCachedReportAfterCancelling({ title: newTitle }),
    // The 204 carries no body, so the role is all there is to write back.
    onSuccess: (role: ReportRole | null) => {
      patchCachedReport({ role });
    },
    onError: (error, _newTitle, previous) => {
      rollBack(previous);
      resyncIfForbidden(error);
    },
  });

  // Not optimistic, unlike the two above. There is nothing to patch: the report
  // being edited ceases to exist, so the page waits for the 204 and then leaves.
  const remove = useMutation({
    mutationFn: () => deleteReport(reportID),
    meta: { errorTitle: "Could not delete this report" },
    onSuccess: () => {
      toast.success("Report deleted");

      void navigate(HOME_PATH);

      // Dropped rather than invalidated: refetching a deleted report would only
      // 404. Without this, a back-button visit would render the stale cache
      // entry before the failure came back.
      queryClient.removeQueries({ queryKey: reportQueryKey(reportID) });

      // The gallery is a separate cache entry and still lists this report.
      void queryClient.invalidateQueries({
        queryKey: REPORT_PREVIEWS_QUERY_KEY_PREFIX,
      });
    },
    onError: (error: Error) => {
      resyncIfForbidden(error);
    },
  });

  const changeVisibility = useMutation({
    mutationFn: (publiclyVisible: boolean) =>
      updateReportVisibility(reportID, publiclyVisible),
    meta: { errorTitle: "Could not change who can see this report" },
    onMutate: (publiclyVisible: boolean) =>
      patchCachedReportAfterCancelling({ public: publiclyVisible }),
    onSuccess: (role: ReportRole | null, publiclyVisible: boolean) => {
      patchCachedReport({ role });

      toast.success(
        publiclyVisible ? "Report published" : "Report is now private",
      );
    },
    onError: (error, _publiclyVisible, previous) => {
      rollBack(previous);
      resyncIfForbidden(error);
    },
  });

  if (isPending) {
    return (
      <div className="flex justify-center py-20">
        <BounceLoader color={canaryThemeColour} />
      </div>
    );
  }

  if (isError) {
    throw error;
  }

  return (
    <div className="flex justify-center">
      <div className="mx-10 w-full max-w-175 flex flex-col items-center gap-y-5">
        <Masthead
          canRename={hasAtLeastRole(report.role, EDIT_ROLE)}
          canChangeVisibility={hasAtLeastRole(report.role, OWNER_ROLE)}
          canDelete={hasAtLeastRole(report.role, OWNER_ROLE)}
          title={report.title}
          authors={report.authors}
          publiclyVisible={report.public}
          onRename={(newTitle: string) => {
            rename.mutate(newTitle);
          }}
          onToggleVisibility={() => {
            changeVisibility.mutate(!report.public);
          }}
          onDelete={() => {
            remove.mutate();
          }}
          isRenaming={rename.isPending}
          isChangingVisibility={changeVisibility.isPending}
          isDeleting={remove.isPending}
        />

        {report.content_containers.map((container) => (
          <ContentContainer
            key={container.container_id}
            container={container}
            shouldFocus={container.container_id === containerToFocus}
          />
        ))}

        <PreviewDisclaimer />

        {hasAtLeastRole(report.role, EDIT_ROLE) && (
          <Prompt
            onSubmit={(prompt: string) => {
              generate.mutate(prompt);
            }}
            isPending={generate.isPending}
          />
        )}
      </div>
    </div>
  );
}

function Masthead({
  canRename,
  canChangeVisibility,
  canDelete,
  title,
  authors,
  publiclyVisible,
  onRename,
  isRenaming,
  onToggleVisibility,
  isChangingVisibility,
  onDelete,
  isDeleting,
}: {
  canRename: boolean;
  canChangeVisibility: boolean;
  canDelete: boolean;
  title: string;
  authors: string[];
  publiclyVisible: boolean;
  onRename: (newTitle: string) => void;
  isRenaming: boolean;
  onToggleVisibility: () => void;
  isChangingVisibility: boolean;
  onDelete: () => void;
  isDeleting: boolean;
}) {
  const { Icon: VisibilityIcon, label: visibilityLabel } =
    describeVisibility(publiclyVisible);

  return (
    <header className="w-full flex flex-col items-center">
      <div className="flex items-center gap-x-2">
        {canRename ? (
          <form
            className="min-w-0"
            onSubmit={(event) => {
              event.preventDefault();

              const formData = new FormData(event.currentTarget);
              const submitted: FormDataEntryValue | null =
                formData.get(TITLE_FORM_FIELD);
              const newTitle: string =
                typeof submitted === "string" ? submitted.trim() : "";

              if (!newTitle || newTitle === title) {
                event.currentTarget.reset();
                return;
              }

              onRename(newTitle);
            }}
          >
            <h2 className="ReportTitle min-w-0">
              {/* A textarea, not an input, because inputs are single-line
                  and cannot wrap. `field-sizing-content` sizes it to its
                  content, so it grows in height once `max-w` stops it
                  growing in width. */}
              <textarea
                rows={1}
                name={TITLE_FORM_FIELD}
                aria-label="Report title"
                // Uncontrolled: typing re-renders nothing, optimistic cache
                // update keeps this in step anyway
                defaultValue={title}
                className="field-sizing-content max-w-full resize-none bg-transparent text-center focus:outline-none sm:max-w-150 md:max-w-175"
                disabled={isRenaming}
                // A textarea takes Enter as a newline, so submit by hand to
                // keep the single-line input's behaviour
                onKeyDown={(event) => {
                  if (event.key === "Enter") {
                    event.preventDefault();
                    event.currentTarget.form?.requestSubmit();
                  }
                }}
                // Clicking away commits, the same as pressing Enter.
                onBlur={(event) => {
                  event.currentTarget.form?.requestSubmit();
                }}
              />
            </h2>
          </form>
        ) : (
          <h2 className="ReportTitle min-w-0 max-w-full text-center sm:max-w-150 md:max-w-175">
            {title}
          </h2>
        )}

        {canChangeVisibility ? (
          <VisibilityControl
            publiclyVisible={publiclyVisible}
            onToggle={onToggleVisibility}
            isPending={isChangingVisibility}
          />
        ) : (
          <span
            role="img"
            aria-label={visibilityLabel}
            title={visibilityLabel}
            className="shrink-0 text-(--text-color-secondary)"
          >
            <VisibilityIcon size="1em" />
          </span>
        )}

        {canDelete && (
          <ConfirmDialog
            title="Delete this report?"
            description="This report and everything in it will be permanently deleted. This cannot be undone."
            confirmLabel="Delete"
            destructive
            onConfirm={onDelete}
            isPending={isDeleting}
            trigger={
              <button
                type="button"
                aria-label="Delete this report"
                title="Delete this report"
                disabled={isDeleting}
                className="flex shrink-0 text-(--text-color-secondary) cursor-pointer disabled:cursor-progress"
              >
                <Trash2 size="1em" />
              </button>
            }
          />
        )}
      </div>
      <p className="text-sm text-(--text-color-secondary) min-w-0 max-w-full text-center sm:max-w-150 md:max-w-175">
        {authors.join(", ")}
      </p>
    </header>
  );
}

function describeVisibility(publiclyVisible: boolean): {
  Icon: LucideIcon;
  label: string;
} {
  return publiclyVisible
    ? { Icon: Eye, label: "Public" }
    : { Icon: EyeOff, label: "Private" };
}

function VisibilityControl({
  publiclyVisible,
  onToggle,
  isPending,
}: {
  publiclyVisible: boolean;
  onToggle: () => void;
  isPending: boolean;
}) {
  const { Icon, label } = describeVisibility(publiclyVisible);
  const needsConfirmation: boolean = !publiclyVisible;

  // `type="button"` for the same reason: as a submit button inside a form, the
  // click would reach the form's `onSubmit` as well.
  const toggleButton = (onClick?: () => void) => (
    <button
      type="button"
      aria-label={`${label}. Change who can see this report`}
      title={`${label}ly visible`}
      disabled={isPending}
      className="flex shrink-0 text-(--text-color-secondary) cursor-pointer disabled:cursor-progress"
      onClick={onClick}
    >
      <Icon size="1em" />
    </button>
  );

  if (!needsConfirmation) {
    return toggleButton(onToggle);
  }

  return (
    <ConfirmDialog
      title="Publish this report?"
      description="Anyone will be able to view this report at its link and find it on the home page. You can make it private again at any time."
      confirmLabel="Publish"
      onConfirm={onToggle}
      isPending={isPending}
      // No `onClick`: opening the dialog is the whole of this button's job.
      trigger={toggleButton()}
    />
  );
}

function PreviewDisclaimer() {
  return (
    <Collapsible.Root
      defaultOpen
      className="w-full rounded-lg bg-(--background-color-secondary) px-4 py-3"
    >
      <Collapsible.Trigger className="group flex w-full cursor-pointer items-center justify-between gap-x-2 text-left text-sm font-medium">
        What Canary can answer
        <ChevronDown
          size="1.25em"
          className="transition-transform duration-(--transition-delay) group-data-panel-open:rotate-180"
        />
      </Collapsible.Trigger>

      <Collapsible.Panel className="flex flex-col gap-y-3 pt-3 text-sm text-(--text-color-secondary)">
        <p>
          This preview supports a limited selection of analysis. These examples
          are representative of what the agent can handle:
        </p>

        <ul className="flex list-disc flex-col gap-y-2 ps-5">
          <li>
            "Give me Apple's closing share price from January to March 2026."
          </li>
          <li>
            "Show me the daily returns on Apple's stock price as well as the
            volatility of this over a 5-day window in January 2026."
          </li>
          <li>
            "Compare the opening prices of Apple, Google, Microsoft, Nvidia,
            Tesla, JP Morgan, and Bank of America from January to March 2026. I
            want to use an index from the first trading day."
          </li>
          <li>
            "Break down the market capitalisation of all public companies by
            sector, industry, then company, and show it in a treemap."
          </li>
        </ul>
      </Collapsible.Panel>
    </Collapsible.Root>
  );
}
