import { createContext, useContext, useMemo, useState, type ReactNode } from "react";

type ControlSessionValue = {
  adminKey: string;
  autonomyKey: string;
  hasSession: boolean;
  hasAdminSession: boolean;
  setAdminKey: (value: string) => void;
  setAutonomyKey: (value: string) => void;
  clearSession: () => void;
  buildHeaders: () => Record<string, string>;
};

const ControlSessionContext = createContext<ControlSessionValue | null>(null);

type ControlSessionProviderProps = {
  children: ReactNode;
  initialAdminKey?: string;
  initialAutonomyKey?: string;
};

export function ControlSessionProvider({
  children,
  initialAdminKey = "",
  initialAutonomyKey = "",
}: ControlSessionProviderProps) {
  const [adminKey, setAdminKey] = useState(initialAdminKey);
  const [autonomyKey, setAutonomyKey] = useState(initialAutonomyKey);

  const value = useMemo<ControlSessionValue>(
    () => ({
      adminKey,
      autonomyKey,
      hasSession: Boolean(adminKey.trim() || autonomyKey.trim()),
      hasAdminSession: Boolean(adminKey.trim()),
      setAdminKey,
      setAutonomyKey,
      clearSession: () => {
        setAdminKey("");
        setAutonomyKey("");
      },
      buildHeaders: () => {
        const headers: Record<string, string> = {};
        if (adminKey.trim()) {
          headers["X-Admin-Key"] = adminKey.trim();
        }
        if (autonomyKey.trim()) {
          headers["X-Autonomy-Key"] = autonomyKey.trim();
        }
        return headers;
      },
    }),
    [adminKey, autonomyKey],
  );

  return <ControlSessionContext.Provider value={value}>{children}</ControlSessionContext.Provider>;
}

export function useControlSession() {
  const context = useContext(ControlSessionContext);
  if (!context) {
    throw new Error("useControlSession must be used within ControlSessionProvider");
  }
  return context;
}
