import React from "react";
import { Outlet } from "react-router-dom";
import { Sidebar } from "./Sidebar";

export function AppLayout() {
  return (
    <div className="flex h-screen w-screen overflow-hidden bg-[#070A0F] text-slate-100 font-sans">
      <Sidebar />
      <div className="flex flex-1 flex-col overflow-hidden">
        <main className="flex-1 overflow-y-auto p-8 bg-[radial-gradient(#1e293b12_1px,transparent_1px)] [background-size:24px_24px]">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
