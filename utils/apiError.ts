import axios from "axios";

const API_BASE =
  (typeof process !== "undefined" && process.env.NEXT_PUBLIC_API_URL) ||
  "http://localhost:8002";

export function getApiErrorMessage(err: unknown, fallback: string): string {
  if (axios.isAxiosError(err)) {
    if (!err.response) {
      return `Cannot reach the API at ${API_BASE}. Start the backend: cd Backend\\Backend then run python app\\main.py (port 8002).`;
    }
    const data = err.response.data as {
      detail?: string | Array<{ msg?: string } | string>;
    };
    const d = data?.detail;
    if (typeof d === "string") return d;
    if (Array.isArray(d)) {
      return d
        .map((x) =>
          typeof x === "object" && x !== null && "msg" in x
            ? String((x as { msg: string }).msg)
            : String(x)
        )
        .join(" ");
    }
  }
  if (err instanceof Error) return err.message;
  return fallback;
}
