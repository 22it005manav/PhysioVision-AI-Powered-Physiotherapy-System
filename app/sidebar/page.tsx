"use client";

import { useState } from "react";
import { Sidebar } from "@/components/sidebar";

export default function SidebarPage() {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  return (
    <div className="min-h-screen bg-slate-950 p-4">
      <Sidebar sidebarOpen={sidebarOpen} setSidebarOpen={setSidebarOpen} />
    </div>
  );
}
