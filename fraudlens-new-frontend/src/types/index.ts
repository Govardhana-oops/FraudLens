export type ScreeningStatus =
  | "VALID"
  | "PASS"
  | "REVIEW_REQUIRED"
  | "INVALID"
  | "EXPIRED"
  | "TAMPERED"
  | "WATCHLIST_HIT"
  | "FRAUD_DETECTED"
  | "UNKNOWN"
  | "PROCESSING_ERROR";

export type CheckResult = "PASS" | "REVIEW_REQUIRED" | "INVALID" | "FAIL" | "UNKNOWN";

export type DocumentType =
  | "PASSPORT"
  | "VISA"
  | "NATIONAL_ID"
  | "RESIDENCE_PERMIT"
  | "DRIVER_LICENSE"
  | "AUTO_DETECT";

export interface ExtractedField {
  field_name: string;
  extracted_value: string;
  confidence: number;
  engine?: string;
}

export interface ValidationCheck {
  rule_id: string;
  description: string;
  result: CheckResult;
  severity?: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";
}

export interface TamperingAnalysis {
  tampering_score: number;
  tampering_detected: boolean;
  ela_disparity_score?: number;
  copy_move_detected?: boolean;
  font_anomaly_score?: number;
  anomalies_found?: string[];
}

export interface FaceComparisonResult {
  matched: boolean;
  similarity_score: number;
  liveness_score: number;
  liveness_detected: boolean;
  threshold: number;
  method?: string;
}

export interface WatchlistResult {
  hit: boolean;
  database_checked: string;
  matched_entries: string[];
}

export interface UnifiedScreeningDossier {
  screening_id: string;
  timestamp: string;
  status: ScreeningStatus;
  confidence_score: number;
  document_type: string;
  document_number: string;
  record_hash: string;
  officer_id: string;
  checkpoint_id: string;
  processing_time_ms: number;
  extracted_fields: ExtractedField[];
  validation_checks: ValidationCheck[];
  tampering_analysis: TamperingAnalysis;
  face_comparison: FaceComparisonResult | null;
  watchlist_result: WatchlistResult | null;
  metadata?: Record<string, unknown>;
}

export interface AuditLogEntry {
  sequence_number: number;
  log_id: string;
  timestamp: string;
  event_type: string;
  officer_id: string;
  checkpoint_id: string;
  doc_number: string;
  resource_id: string;
  current_hash: string;
  prev_hash: string;
  previous_hash?: string;
}

export interface AuditVerificationResponse {
  total_logs: number;
  chain_intact: boolean;
  logs: AuditLogEntry[];
}

export interface SystemHealthResponse {
  status: string;
  version: string;
  service: string;
  uptime_seconds: number;
  modules_ready: string[];
  measured_ping_ms?: number;
}

export interface SyncStatusReport {
  status: string;
  synced_records: number;
  last_sync_timestamp: string;
  watchlist_version?: string;
}

export interface ConsoleSettings {
  officerId: string;
  officerName: string;
  checkpointId: string;
  checkpointName: string;
  ocrConfidenceThreshold: number;
  tamperingSensitivity: number;
  faceMatchThreshold: number;
  apiBaseUrl: string;
}
