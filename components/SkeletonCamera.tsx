
import React, { useRef, useEffect, useState, RefObject } from "react";
import * as poseDetection from "@tensorflow-models/pose-detection";
import * as tf from "@tensorflow/tfjs-core";
import "@tensorflow/tfjs-backend-webgl";

// Standard MoveNet 17 keypoint skeleton connections
const SKELETON_CONNECTIONS = [
  // Torso
  [0, 1], [0, 2], [1, 3], [2, 4], // Head to shoulders
  [5, 6], // Shoulders
  [5, 7], [7, 9], // Left arm
  [6, 8], [8, 10], // Right arm
  [5, 11], [6, 12], // Shoulders to hips
  [11, 12], // Hips
  [11, 13], [13, 15], // Left leg
  [12, 14], [14, 16], // Right leg
  // Additional connections for completeness
  [1, 2], // Eyes
  [3, 5], // Left ear to left shoulder
  [4, 6], // Right ear to right shoulder
];

interface Keypoint {
  x: number;
  y: number;
  score?: number;
}

function getAngle(a: Keypoint, b: Keypoint, c: Keypoint): number {
  // Returns angle at point b (in degrees)
  const ab = [a.x - b.x, a.y - b.y];
  const cb = [c.x - b.x, c.y - b.y];
  const dot = ab[0] * cb[0] + ab[1] * cb[1];
  const magAb = Math.sqrt(ab[0] ** 2 + ab[1] ** 2);
  const magCb = Math.sqrt(cb[0] ** 2 + cb[1] ** 2);
  const angle = Math.acos(dot / (magAb * magCb));
  return (angle * 180) / Math.PI;
}

function getState(keypoints: Keypoint[]): string {
  // Use both legs for more robust detection
  const lHip = keypoints[11];
  const lKnee = keypoints[13];
  const lAnkle = keypoints[15];
  const rHip = keypoints[12];
  const rKnee = keypoints[14];
  const rAnkle = keypoints[16];
  if (!lHip || !lKnee || !lAnkle || !rHip || !rKnee || !rAnkle) return "unknown";
  const lAngle = getAngle(lHip, lKnee, lAnkle);
  const rAngle = getAngle(rHip, rKnee, rAnkle);
  const avgAngle = (lAngle + rAngle) / 2;
  if (avgAngle < 100) return "sitting";
  if (avgAngle > 160) return "standing";
  return "transition";
}


const stateColor: Record<string, string> = {
  standing: "#fff",
  sitting: "#FFD600",
  completed: "#00FF00",
  transition: "#FFD600",
  unknown: "#fff",
};


interface SkeletonCameraProps {
  onStateChange?: (state: string, repCount: number) => void;
}

export default function SkeletonCamera({ onStateChange }: SkeletonCameraProps) {

  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [state, setState] = useState<string>("unknown");
  const [repCount, setRepCount] = useState<number>(0);
  const [holdStart, setHoldStart] = useState<number | null>(null);
  const [lastState, setLastState] = useState<string>("standing");

  useEffect(() => {
    let detector: poseDetection.PoseDetector | undefined;
    let animationId: number | undefined;
    let prevState: string = "standing";
    let repCountLocal: number = 0;
    let holdStartLocal: number | null = null;

    async function run() {
      // 1. Request webcam access and assign stream to video
      if (videoRef.current) {
        try {
          const stream = await navigator.mediaDevices.getUserMedia({ video: true });
          videoRef.current.srcObject = stream;
        } catch (err) {
          setState("camera error");
          return;
        }
      }

      // 2. Wait for video to be ready
      const waitForVideo = () => {
        return new Promise<void>((resolve) => {
          if (!videoRef.current) return resolve();
          if (videoRef.current.readyState >= 3) return resolve();
          videoRef.current.onloadeddata = () => resolve();
        });
      };
      await waitForVideo();

      // 3. Set TensorFlow.js backend and wait for readiness
      await tf.setBackend('webgl');
      await tf.ready();

      // 4. Load pose detector
      detector = await poseDetection.createDetector(poseDetection.SupportedModels.MoveNet, {
        modelType: poseDetection.movenet.modelType.SINGLEPOSE_LIGHTWEIGHT,
        enableSmoothing: true,
      });

      // 5. Start detection loop
      // Rep counting state machine
      let lastPoseState: string = "unknown";
      let lastPoseChangeTime: number = Date.now();
      let sitHold: boolean = false;
      let standHold: boolean = false;
      let repInProgress: boolean = false;

      async function detect() {
        if (
          videoRef.current &&
          detector &&
          (videoRef.current as HTMLVideoElement).videoWidth > 0 &&
          (videoRef.current as HTMLVideoElement).videoHeight > 0
        ) {
          // Ensure canvas matches video size
          const video = videoRef.current as HTMLVideoElement;
          const canvas = canvasRef.current as HTMLCanvasElement;
          if (canvas && (canvas.width !== video.videoWidth || canvas.height !== video.videoHeight)) {
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
          }

          const poses = await detector.estimatePoses(video);
          if (poses && poses[0] && poses[0].keypoints) {
            const keypoints = poses[0].keypoints as Keypoint[];
            const currentState = getState(keypoints);
            setState(currentState);
            if (onStateChange) onStateChange(currentState, repCountLocal);

            // Debounce state changes (require state to be held for 500ms)
            const now = Date.now();
            if (currentState !== lastPoseState) {
              lastPoseChangeTime = now;
              lastPoseState = currentState;
            }

            // Sit-stand-sit rep logic with debounce
            if (currentState === "sitting" && now - lastPoseChangeTime > 500) {
              sitHold = true;
            }
            if (currentState === "standing" && now - lastPoseChangeTime > 500) {
              standHold = true;
            }
            // Rep is only counted when a full sit-stand-sit cycle is completed
            if (sitHold && standHold && currentState === "sitting" && !repInProgress) {
              repCountLocal += 1;
              setRepCount(repCountLocal);
              repInProgress = true;
              // Optionally, you can show a visual feedback here
            }
            // Reset for next rep when user stands again
            if (repInProgress && currentState === "standing" && now - lastPoseChangeTime > 500) {
              sitHold = false;
              standHold = false;
              repInProgress = false;
            }

            setHoldStart(holdStartLocal);
            setLastState(prevState);
            prevState = currentState;
            drawSkeleton(keypoints, currentState, video.videoWidth, video.videoHeight);
          }
        }
        animationId = requestAnimationFrame(detect);
      }
      detect();
    }
    run();
    return () => {
      if (animationId) cancelAnimationFrame(animationId);
      if (detector) detector.dispose();
      if (videoRef.current && (videoRef.current as HTMLVideoElement).srcObject) {
        const tracks = ((videoRef.current as HTMLVideoElement).srcObject as MediaStream).getTracks();
        tracks.forEach((track: MediaStreamTrack) => track.stop());
      }
    };
    // eslint-disable-next-line
  }, []);

  // JSX return for the component
  return (
    <div style={{ position: "relative", width: "100%", height: "80vh", maxWidth: "100vw", maxHeight: "100vh", display: "flex", justifyContent: "center", alignItems: "center" }}>
      <video
        ref={videoRef}
        style={{ position: "absolute", top: 0, left: 0, width: "100%", height: "100%", objectFit: "cover" }}
        autoPlay
        playsInline
        muted
      />
      <canvas
        ref={canvasRef}
        style={{ position: "absolute", top: 0, left: 0, width: "100%", height: "100%", pointerEvents: "none" }}
      />
      <div style={{ position: "absolute", top: 20, left: 20, color: "#fff", background: "rgba(0,0,0,0.5)", padding: 10, borderRadius: 8, fontSize: 20, zIndex: 2 }}>
        State: {state} | Reps: {repCount}
      </div>
    </div>
  );

  function drawSkeleton(keypoints: Keypoint[], state: string, width?: number, height?: number) {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.lineWidth = 4;
    ctx.strokeStyle = stateColor[state] || "#fff";

    // Draw connections (use scaled coordinates if needed)
    SKELETON_CONNECTIONS.forEach(([a, b]) => {
      const kpA = keypoints[a];
      const kpB = keypoints[b];
      if (kpA && kpB && (kpA.score ?? 0) > 0.3 && (kpB.score ?? 0) > 0.3) {
        ctx.beginPath();
        ctx.moveTo(kpA.x, kpA.y);
        ctx.lineTo(kpB.x, kpB.y);
        ctx.stroke();
      }
    });
    // Draw keypoints
    keypoints.forEach((kp: Keypoint) => {
      if ((kp.score ?? 0) > 0.3) {
        ctx.beginPath();
        ctx.arc(kp.x, kp.y, 6, 0, 2 * Math.PI);
        ctx.fillStyle = stateColor[state] || "#fff";
        ctx.fill();
        ctx.strokeStyle = "#222";
        ctx.lineWidth = 2;
        ctx.stroke();
      }
    });
  }

  return (
    <div style={{ position: "relative", width: "100%", height: "80vh", maxWidth: "100vw", maxHeight: "100vh", display: "flex", justifyContent: "center", alignItems: "center" }}>
      <video
        ref={videoRef}
        style={{ position: "absolute", top: 0, left: 0, width: "100%", height: "100%", objectFit: "cover" }}
        autoPlay
        playsInline
        muted
      />
      <canvas
        ref={canvasRef}
        style={{ position: "absolute", top: 0, left: 0, width: "100%", height: "100%", pointerEvents: "none" }}
      />
      <div style={{ position: "absolute", top: 20, left: 20, color: "#fff", background: "rgba(0,0,0,0.5)", padding: 10, borderRadius: 8, fontSize: 20, zIndex: 2 }}>
        State: {state} | Reps: {repCount}
      </div>
    </div>
  );
}
