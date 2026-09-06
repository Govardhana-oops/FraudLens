import React from "react";
import { Outlet } from "react-router-dom";
import { Sidebar } from "./Sidebar";
import { TopBar } from "./TopBar";

export function AppLayout() {
  return (
    <div className="flex h-screen w-screen overflow-hidden bg-[#050B12] text-slate-100 font-sans">
      <Sidebar />
      <div className="flex flex-1 flex-col overflow-hidden">
        <TopBar />
        <main className="flex-1 overflow-y-auto p-6 lg:p-8 bg-[#050B12] bg-[radial-gradient(#1E40541A_1px,transparent_1px)] [background-size:24px_24px]">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
