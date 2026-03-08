import { requestJson } from "./client";

export type SecretStatusPayload = {
  status: string;
  checked_at: string;
  summary: {
    present: number;
    missing: number;
    invalid: number;
    connections_live: number;
    connections_partial: number;
    connections_missing: number;
    connections_planned: number;
  };
  secrets: Array<{
    name: string;
    provider: string;
    purpose: string;
    required_for: string;
    priority: string;
    scope: string;
    kind: string;
    present: boolean;
    status: string;
    evidence: string;
  }>;
  connections: Array<{
    target: string;
    label: string;
    provider: string;
    status: string;
    evidence: string;
    checked_at: string;
  }>;
  datastores: Array<{
    id: string;
    name: string;
    engine: string;
    status: string;
    evidence: string;
  }>;
};

export type SecretTestPayload = {
  status: string;
  result: {
    target: string;
    label: string;
    provider: string;
    status: string;
    evidence: string;
    checked_at: string;
  };
};

export function getSecretStatus(headers: Record<string, string>, signal?: AbortSignal) {
  return requestJson<SecretStatusPayload>("/api/control-ui/secrets/status", { headers, signal });
}

export function testSecretTarget(target: string, headers: Record<string, string>) {
  return requestJson<SecretTestPayload>(`/api/control-ui/secrets/test/${encodeURIComponent(target)}`, {
    method: "POST",
    headers,
  });
}
