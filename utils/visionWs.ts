/**
 * WebSocket URL for Backend_Vision (Python). This is separate from the FastAPI
 * backend and MongoDB — exercise pages need `python main.py` in Backend_Vision.
 */
export const VISION_WS_URL =
  (typeof process !== "undefined" &&
    process.env.NEXT_PUBLIC_VISION_WS_URL?.trim()) ||
  "ws://localhost:8765";

export const VISION_SERVER_HELP =
  "Start the vision server: open a terminal, cd Backend_Vision, then run: python main.py (keeps ws://localhost:8765 open).";
