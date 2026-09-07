/**
 * Scenario types for Border AI-DIDSS / FraudLens
 * Pure type definitions — zero synthetic or fake document generation.
 */

export type DemoScenario =
  | "valid_passport"
  | "expired_document"
  | "ocr_uncertainty"
  | "tampering_review"
  | "face_review";
