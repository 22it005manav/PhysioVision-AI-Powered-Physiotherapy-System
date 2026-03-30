"use client";

import React, { useState } from "react";
import { Sidebar } from "@/components/sidebar";
import SkeletonCamera from "@/components/SkeletonCamera";

export default function WarriorPose() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  return (
    <div className="flex min-h-screen overflow-hidden bg-black">
      <Sidebar sidebarOpen={sidebarOpen} setSidebarOpen={setSidebarOpen} />
      <div className="flex-1 container mx-auto px-10 py-[1.4%] bg-black">
        <div className="h-16 w-full bg-gray-800 rounded-lg mb-4 flex items-center justify-center">
          <h1 className="text-4xl font-bold text-white">Warrior Pose Exercise</h1>
        </div>
        <div className="flex flex-col items-center justify-center h-[80vh] bg-gray-900 rounded-lg overflow-hidden relative">
          <SkeletonCamera />
        </div>
      </div>
    </div>
  );
}
// ...existing code...