import { requestJson } from "./client";

export type SettingRow = {
  key: string;
  value: string;
  description: string;
  updated_at: string;
};

export function getSettings(headers: Record<string, string>, signal?: AbortSignal) {
  return requestJson<SettingRow[]>("/api/settings", { headers, signal });
}

export function updateSetting(
  key: string,
  payload: { value: string; description: string },
  headers: Record<string, string>,
) {
  return requestJson<{ key: string; value: string }>(`/api/settings/${encodeURIComponent(key)}`, {
    method: "PUT",
    headers,
    body: payload,
  });
}
