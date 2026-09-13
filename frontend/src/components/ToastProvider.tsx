import { Toast } from "@base-ui/react/toast";
import {
  CircleAlert,
  CircleCheck,
  Info,
  X,
  type LucideIcon,
} from "lucide-react";
import { type ReactNode } from "react";
import { toastManager, type ToastType } from "@/lib/toast";

const iconByType: Record<ToastType, LucideIcon> = {
  error: CircleAlert,
  success: CircleCheck,
  info: Info,
};

// `type` is a free-form string on the toast object, so anything not raised
// through `useToast` simply renders without an icon.
function toastIcon(type: string | undefined): LucideIcon | undefined {
  return type && type in iconByType ? iconByType[type as ToastType] : undefined;
}

// `Toast.Root` needs a toast object from the manager, but the manager is only
// readable inside `Toast.Provider`. A component cannot consume a context it
// renders itself, so the mapping lives in this child instead of with
// ToastProvider below.
function ToastList() {
  const { toasts } = Toast.useToastManager();

  return toasts.map((toast) => {
    const Icon = toastIcon(toast.type);

    return (
      <Toast.Root key={toast.id} toast={toast} className="ToastRoot">
        {Icon && <Icon className="ToastIcon" size="1.25em" aria-hidden />}
        <Toast.Content className="ToastContent">
          <Toast.Title className="ToastTitle" />
          <Toast.Description />
        </Toast.Content>
        <Toast.Close className="ToastClose" aria-label="Dismiss">
          <X size="1em" />
        </Toast.Close>
      </Toast.Root>
    );
  });
}

export default function ToastProvider({ children }: { children: ReactNode }) {
  return (
    <Toast.Provider toastManager={toastManager}>
      {children}

      <Toast.Portal>
        <Toast.Viewport className="ToastViewport">
          <ToastList />
        </Toast.Viewport>
      </Toast.Portal>
    </Toast.Provider>
  );
}
