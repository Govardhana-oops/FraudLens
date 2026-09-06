import React, { createContext, useContext, useState, useEffect, useCallback, useMemo } from "react";
import type {
  UnifiedScreeningDossier,
  AuditLogEntry,
  ConsoleSettings,
  DocumentType,
  SyncStatusReport,
} from "@/types";
import { api } from "@/services/api";

interface OperationalStats {
  totalScreened: number;
  validCount: number;
  reviewRequiredCount: number;
  expiredCount: number;
  avgLatencyMs: number;
}

interface AppContextType {
  records: UnifiedScreeningDossier[];
  currentResult: UnifiedScreeningDossier | null;
  stats: OperationalStats;
  auditLogs: AuditLogEntry[];
  settings: ConsoleSettings;
  isLiveConnected: boolean;
  isScreening: boolean;
  isSyncing: boolean;
  lastSyncedAt: string | null;

  executeScreening: (
    documentFile: File,
    liveFaceFile: File | null,
    docType: DocumentType
  ) => Promise<UnifiedScreeningDossier>;
  addScreeningRecord: (record: UnifiedScreeningDossier) => void;
  deleteRecord: (screeningId: string) => void;
  clearCurrentResult: () => void;
  clearAllData: () => void;
  updateSettings: (newSettings: ConsoleSettings) => void;
  fetchAuditLogs: () => Promise<void>;
  triggerSync: () => Promise<SyncStatusReport>;
  refreshData: () => Promise<void>;
}

const STORAGE_RECORDS_KEY = "fraudlens_screening_records_v2";
const STORAGE_AUDIT_KEY = "fraudlens_audit_logs_v2";
const STORAGE_SETTINGS_KEY = "fraudlens_console_settings_v2";

const DEFAULT_SETTINGS: ConsoleSettings = {
  officerId: "CP-0082",
  officerName: "Officer J. Vance",
  checkpointId: "GATE-04",
  checkpointName: "Terminal B - Primary Inspection",
  ocrConfidenceThreshold: 0.7,
  tamperingSensitivity: 0.35,
  faceMatchThreshold: 0.75,
  apiBaseUrl: api.getBaseUrl(),
};

const AppContext = createContext<AppContextType | undefined>(undefined);

export function AppProvider({ children }: { children: React.ReactNode }) {
  // 1. Initial State from localStorage (Defaults to 0 / Empty)
  const [records, setRecords] = useState<UnifiedScreeningDossier[]>(() => {
    try {
      const saved = localStorage.getItem(STORAGE_RECORDS_KEY);
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  });

  const [currentResult, setCurrentResult] = useState<UnifiedScreeningDossier | null>(null);

  const [auditLogs, setAuditLogs] = useState<AuditLogEntry[]>(() => {
    try {
      const saved = localStorage.getItem(STORAGE_AUDIT_KEY);
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  });

  const [settings, setSettings] = useState<ConsoleSettings>(() => {
    try {
      const saved = localStorage.getItem(STORAGE_SETTINGS_KEY);
      if (saved) {
        const parsed = JSON.parse(saved);
        // If loaded on cloud but settings were saved as localhost, upgrade to current base URL
        if (
          typeof window !== "undefined" &&
          window.location.hostname !== "localhost" &&
          window.location.hostname !== "127.0.0.1" &&
          parsed.apiBaseUrl === "http://localhost:8000"
        ) {
          parsed.apiBaseUrl = api.getBaseUrl();
        }
        return { ...DEFAULT_SETTINGS, ...parsed };
      }
      return DEFAULT_SETTINGS;
    } catch {
      return DEFAULT_SETTINGS;
    }
  });

  const [isLiveConnected, setIsLiveConnected] = useState<boolean>(false);
  const [isScreening, setIsScreening] = useState<boolean>(false);
  const [isSyncing, setIsSyncing] = useState<boolean>(false);
  const [lastSyncedAt, setLastSyncedAt] = useState<string | null>(null);

  // Persist records
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_RECORDS_KEY, JSON.stringify(records));
    } catch (e) {
      console.error("Failed to save records to localStorage", e);
    }
  }, [records]);

  // Persist audit logs
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_AUDIT_KEY, JSON.stringify(auditLogs));
    } catch (e) {
      console.error("Failed to save audit logs to localStorage", e);
    }
  }, [auditLogs]);

  // Persist settings
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_SETTINGS_KEY, JSON.stringify(settings));
      api.setBaseUrl(settings.apiBaseUrl);
    } catch (e) {
      console.error("Failed to save settings to localStorage", e);
    }
  }, [settings]);

  // Check Backend Live Health
  const checkHealth = useCallback(async () => {
    try {
      const health = await api.getHealth();
      setIsLiveConnected(health.status === "HEALTHY" || health.status === "healthy");
    } catch {
      setIsLiveConnected(false);
    }
  }, []);

  useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, 15000);
    return () => clearInterval(interval);
  }, [checkHealth]);

  // Compute 100% Dynamic Operational Metrics (Zero Hardcoding)
  const stats: OperationalStats = useMemo(() => {
    const totalScreened = records.length;
    const validCount = records.filter((r) => r.status === "VALID" || r.status === "PASS").length;
    const reviewRequiredCount = records.filter((r) => r.status === "REVIEW_REQUIRED").length;
    const expiredCount = records.filter(
      (r) =>
        r.status === "EXPIRED" ||
        r.status === "TAMPERED" ||
        r.status === "WATCHLIST_HIT" ||
        r.status === "INVALID" ||
        r.status === "FRAUD_DETECTED"
    ).length;

    const totalLatency = records.reduce((acc, r) => acc + (r.processing_time_ms || 0), 0);
    const avgLatencyMs = totalScreened > 0 ? Math.round(totalLatency / totalScreened) : 0;

    return {
      totalScreened,
      validCount,
      reviewRequiredCount,
      expiredCount,
      avgLatencyMs,
    };
  }, [records]);

  // Execute Screening Pipeline
  const executeScreening = useCallback(
    async (
      documentFile: File,
      liveFaceFile: File | null,
      docType: DocumentType
    ): Promise<UnifiedScreeningDossier> => {
      setIsScreening(true);
      try {
        const dossier = await api.inspectDocument(
          documentFile,
          liveFaceFile,
          docType,
          settings.officerId,
          settings.checkpointId
        );

        setCurrentResult(dossier);
        setRecords((prev) => [dossier, ...prev.filter((r) => r.screening_id !== dossier.screening_id)]);

        // Append audit entry locally
        const newAuditEntry: AuditLogEntry = {
          sequence_number: auditLogs.length + 1,
          log_id: `LOG-${Date.now()}`,
          timestamp: dossier.timestamp,
          event_type: `SCREENING_${dossier.status}`,
          officer_id: dossier.officer_id,
          checkpoint_id: dossier.checkpoint_id,
          doc_number: dossier.document_number,
          resource_id: dossier.screening_id,
          current_hash: dossier.record_hash,
          prev_hash:
            auditLogs.length > 0 ? auditLogs[auditLogs.length - 1].current_hash : "00000000000000000000000000000000",
        };

        setAuditLogs((prev) => [newAuditEntry, ...prev]);
        return dossier;
      } finally {
        setIsScreening(false);
      }
    },
    [settings, auditLogs]
  );

  const addScreeningRecord = useCallback((record: UnifiedScreeningDossier) => {
    setRecords((prev) => [record, ...prev.filter((r) => r.screening_id !== record.screening_id)]);
  }, []);

  const deleteRecord = useCallback((screeningId: string) => {
    setRecords((prev) => prev.filter((r) => r.screening_id !== screeningId));
    if (currentResult?.screening_id === screeningId) {
      setCurrentResult(null);
    }
  }, [currentResult]);

  const clearCurrentResult = useCallback(() => {
    setCurrentResult(null);
  }, []);

  const clearAllData = useCallback(() => {
    setRecords([]);
    setAuditLogs([]);
    setCurrentResult(null);
    localStorage.removeItem(STORAGE_RECORDS_KEY);
    localStorage.removeItem(STORAGE_AUDIT_KEY);
  }, []);

  const updateSettings = useCallback((newSettings: ConsoleSettings) => {
    setSettings(newSettings);
  }, []);

  const fetchAuditLogs = useCallback(async () => {
    try {
      const res = await api.getAuditLogs();
      if (res && res.logs && res.logs.length > 0) {
        // Map backend audit logs
        const mappedLogs: AuditLogEntry[] = res.logs.map((l: any, i: number) => ({
          sequence_number: i + 1,
          log_id: l.log_id || `LOG-${i}`,
          timestamp: l.timestamp || new Date().toISOString(),
          event_type: l.recommended_action ? `ACTION_${l.recommended_action}` : "INSPECTION_RECORDED",
          officer_id: l.officer_id || "OFFICER",
          checkpoint_id: l.checkpoint_id || "GATE",
          doc_number: l.doc_number || "—",
          resource_id: l.log_id || "RECORD",
          current_hash: l.entry_hash || l.current_hash || "HASH",
          prev_hash: l.prev_hash || "00000000000000000000000000000000",
        }));
        setAuditLogs(mappedLogs);
      }
    } catch {
      // Keep existing local audit logs if remote not available
    }
  }, []);

  const triggerSync = useCallback(async (): Promise<SyncStatusReport> => {
    setIsSyncing(true);
    try {
      const report = await api.triggerSync(records);
      setLastSyncedAt(new Date().toISOString());
      return report;
    } finally {
      setIsSyncing(false);
    }
  }, [records]);

  const refreshData = useCallback(async () => {
    await checkHealth();
    await fetchAuditLogs();
  }, [checkHealth, fetchAuditLogs]);

  return (
    <AppContext.Provider
      value={{
        records,
        currentResult,
        stats,
        auditLogs,
        settings,
        isLiveConnected,
        isScreening,
        isSyncing,
        lastSyncedAt,
        executeScreening,
        addScreeningRecord,
        deleteRecord,
        clearCurrentResult,
        clearAllData,
        updateSettings,
        fetchAuditLogs,
        triggerSync,
        refreshData,
      }}
    >
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error("useApp must be used within an AppProvider");
  }
  return context;
}
