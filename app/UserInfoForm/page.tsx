"use client";

import { UserInfoForm } from "@/components/user-info-form";

export default function UserInfoFormPage() {
  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center p-4">
      <UserInfoForm onClose={() => {}} />
    </div>
  );
}
