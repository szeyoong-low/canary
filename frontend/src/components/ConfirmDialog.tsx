import { AlertDialog } from "@base-ui/react/alert-dialog";
import { type ReactElement } from "react";

/**
 * Guards an irreversible action behind a confirmation step.
 *
 * An alert dialog rather than a plain dialog: it traps focus, cannot be
 * dismissed by clicking the backdrop or pressing Escape, and is announced to
 * screen readers as requiring a response.
 */
export default function ConfirmDialog({
  trigger,
  title,
  description,
  confirmLabel,
  onConfirm,
  isPending = false,
}: {
  // The caller's own button. Base UI merges the trigger's behaviour onto this
  // element via `render`, so appearance and accessible name stay with caller
  trigger: ReactElement;
  title: string;
  description: string;
  confirmLabel: string;
  onConfirm: () => void;
  isPending?: boolean;
}) {
  return (
    <AlertDialog.Root>
      <AlertDialog.Trigger render={trigger} />

      <AlertDialog.Portal>
        <AlertDialog.Backdrop className="AlertDialogBackdrop" />

        <AlertDialog.Popup className="AlertDialogPopup">
          <AlertDialog.Title className="AlertDialogTitle">
            {title}
          </AlertDialog.Title>
          <AlertDialog.Description className="AlertDialogDescription">
            {description}
          </AlertDialog.Description>

          <div className="AlertDialogActions">
            <AlertDialog.Close
              className="AlertDialogButton"
              disabled={isPending}
            >
              Cancel
            </AlertDialog.Close>

            {/* Deliberately not an `AlertDialog.Close`. Closing on click would
                hide the pending state and leave nowhere to retry from if the
                request fails. The caller navigates away on success instead,
                which unmounts this. */}
            <button
              type="button"
              className="AlertDialogButton"
              data-destructive
              disabled={isPending}
              onClick={onConfirm}
            >
              {confirmLabel}
            </button>
          </div>
        </AlertDialog.Popup>
      </AlertDialog.Portal>
    </AlertDialog.Root>
  );
}
