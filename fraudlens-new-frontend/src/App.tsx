import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AppProvider } from "@/context/AppContext";
import { AppLayout } from "@/layouts/AppLayout";

import { LandingPage } from "@/pages/LandingPage";
import { DashboardPage } from "@/pages/DashboardPage";
import { DocumentScreeningPage } from "@/pages/DocumentScreeningPage";
import { LiveVerificationPage } from "@/pages/LiveVerificationPage";
import { EvidenceDossierPage } from "@/pages/EvidenceDossierPage";
import { DatabasePage } from "@/pages/DatabasePage";
import { SynchronizationPage } from "@/pages/SynchronizationPage";
import { AuditLogsPage } from "@/pages/AuditLogsPage";
import { SystemHealthPage } from "@/pages/SystemHealthPage";
import { SettingsPage } from "@/pages/SettingsPage";
import { AboutPage } from "@/pages/AboutPage";

export default function App() {
  return (
    <AppProvider>
      <BrowserRouter>
        <Routes>
          {/* Landing Page (Public / Overview) */}
          <Route path="/" element={<LandingPage />} />

          {/* Console Application Pages within AppLayout */}
          <Route element={<AppLayout />}>
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/screening" element={<DocumentScreeningPage />} />
            <Route path="/live-verification" element={<LiveVerificationPage />} />
            <Route path="/evidence" element={<EvidenceDossierPage />} />
            <Route path="/database" element={<DatabasePage />} />
            <Route path="/sync" element={<SynchronizationPage />} />
            <Route path="/audit" element={<AuditLogsPage />} />
            <Route path="/health" element={<SystemHealthPage />} />
            <Route path="/settings" element={<SettingsPage />} />
            <Route path="/about" element={<AboutPage />} />
          </Route>

          {/* Catch-all Redirect */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AppProvider>
  );
}
