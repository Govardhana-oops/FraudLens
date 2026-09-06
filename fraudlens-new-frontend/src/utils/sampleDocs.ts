/**
 * High-fidelity synthetic document generator for Border AI-DIDSS / FraudLens
 * Generates realistic ICAO Doc 9303 Passports and Credentials on HTML5 Canvas
 */

export type DemoScenario =
  | "valid_passport"
  | "expired_document"
  | "ocr_uncertainty"
  | "tampering_review"
  | "face_review";

export function generateSyntheticDocumentFile(scenario: DemoScenario): Promise<File> {
  return new Promise((resolve) => {
    const canvas = document.createElement("canvas");
    canvas.width = 960;
    canvas.height = 640;
    const ctx = canvas.getContext("2d");

    if (!ctx) {
      const blob = new Blob(["sample"], { type: "image/png" });
      return resolve(new File([blob], "passport_rohit_sharma.png", { type: "image/png" }));
    }

    // 1. Security Substrate & Guilloche Pattern Background
    ctx.fillStyle = "#EAEFF5";
    ctx.fillRect(0, 0, 960, 640);

    ctx.strokeStyle = "rgba(180, 195, 215, 0.4)";
    ctx.lineWidth = 1;
    for (let i = 0; i < 960; i += 24) {
      ctx.beginPath();
      ctx.moveTo(i, 0);
      ctx.lineTo(i + 80, 640);
      ctx.stroke();
    }
    for (let i = 0; i < 640; i += 24) {
      ctx.beginPath();
      ctx.moveTo(0, i);
      ctx.lineTo(960, i + 60);
      ctx.stroke();
    }

    // Outer border
    ctx.strokeStyle = "#4A6B8A";
    ctx.lineWidth = 3;
    ctx.strokeRect(12, 12, 936, 616);

    // 2. Header: Bilingual Country Title
    ctx.fillStyle = "#1E3A5F";
    ctx.font = "bold 20px 'IBM Plex Sans', sans-serif";
    ctx.fillText("भारत गणराज्य  REPUBLIC OF INDIA", 220, 48);

    // Header Meta labels
    ctx.font = "bold 13px 'IBM Plex Sans', sans-serif";
    ctx.fillStyle = "#2D4A6E";
    ctx.fillText("पासपोर्ट", 220, 85);
    ctx.fillText("PASSPORT", 220, 102);

    ctx.fillText("प्रकार / Type", 360, 85);
    ctx.font = "bold 15px 'IBM Plex Sans', sans-serif";
    ctx.fillText("P", 360, 104);

    ctx.font = "bold 13px 'IBM Plex Sans', sans-serif";
    ctx.fillText("राष्ट्र कोड / Country Code", 480, 85);
    ctx.font = "bold 15px 'IBM Plex Sans', sans-serif";
    ctx.fillText("IND", 480, 104);

    ctx.font = "bold 13px 'IBM Plex Sans', sans-serif";
    ctx.fillText("पासपोर्ट नं. / Passport No.", 700, 85);
    ctx.font = "bold 18px 'IBM Plex Mono', monospace";
    ctx.fillStyle = "#0A1E38";

    let docNum = "S1234567";
    let surname = "SHARMA";
    let givenNames = "ROHIT";
    let dob = "15 JAN 1995";
    let expiry = "09 FEB 2030";
    let issueDate = "10 FEB 2020";
    let pob = "NEW DELHI";
    let nat = "INDIAN";
    let sex = "M";

    let mrzLine1 = "P<IND<SHARMA<<ROHIT<<<<<<<<<<<<<<<<<<<<<<<<<<";
    let mrzLine2 = "S1234567<8IND9501156M3002097<<<<<<<<<<<<<<<02";

    if (scenario === "expired_document") {
      expiry = "09 FEB 2020";
      mrzLine2 = "S1234567<8IND9501156M2002097<<<<<<<<<<<<<<<02";
    } else if (scenario === "ocr_uncertainty") {
      docNum = "S123X?97";
      surname = "SH~RMA";
      givenNames = "R*HIT";
    } else if (scenario === "tampering_review") {
      surname = "GARCIA";
      givenNames = "MARIA";
      docNum = "P99887766";
      mrzLine1 = "P<UTOGARCIA<<MARIA<<<<<<<<<<<<<<<<<<<<<<<<<<";
      mrzLine2 = "P998877668UTO8508124F3208128<<<<<<<<<<<<<<<2";
    }

    ctx.fillText(docNum, 700, 104);

    // 3. Photo Box with Portrait Illustration
    const photoX = 45;
    const photoY = 125;
    const photoW = 210;
    const photoH = 270;

    ctx.fillStyle = "#CCD7E4";
    ctx.fillRect(photoX, photoY, photoW, photoH);
    ctx.strokeStyle = "#6B8BAA";
    ctx.lineWidth = 2;
    ctx.strokeRect(photoX, photoY, photoW, photoH);

    // Draw stylized silhouette portrait
    ctx.fillStyle = "#8BA3BE";
    // Head
    ctx.beginPath();
    ctx.arc(photoX + photoW / 2, photoY + 95, 52, 0, Math.PI * 2);
    ctx.fill();
    // Shoulders
    ctx.beginPath();
    ctx.arc(photoX + photoW / 2, photoY + 260, 95, Math.PI, Math.PI * 2);
    ctx.fill();

    // Hair / Face overlay
    ctx.fillStyle = "#1E293B";
    ctx.beginPath();
    ctx.arc(photoX + photoW / 2, photoY + 75, 48, Math.PI * 0.8, Math.PI * 2.2);
    ctx.fill();

    // Signature below photo
    ctx.font = "italic bold 17px 'Caveat', cursive, sans-serif";
    ctx.fillStyle = "#0A2038";
    ctx.fillText("Rohit Sharma", photoX + 35, photoY + photoH + 30);

    // 4. National Emblem Watermark Placeholder in background
    ctx.strokeStyle = "rgba(100, 130, 165, 0.25)";
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.arc(760, 240, 55, 0, Math.PI * 2);
    ctx.stroke();
    ctx.font = "bold 12px sans-serif";
    ctx.fillStyle = "rgba(70, 100, 135, 0.4)";
    ctx.fillText("सत्यमेव जयते", 730, 310);

    // 5. Visual Inspection Data Grid
    ctx.fillStyle = "#0A1E38";

    const drawField = (hindiLabel: string, engLabel: string, value: string, x: number, y: number, isRed = false) => {
      ctx.font = "11px 'IBM Plex Sans', sans-serif";
      ctx.fillStyle = "#4A6888";
      ctx.fillText(`${hindiLabel} / ${engLabel}`, x, y);
      ctx.font = "bold 14px 'IBM Plex Sans', sans-serif";
      ctx.fillStyle = isRed ? "#C51616" : "#0A1E38";
      ctx.fillText(value, x, y + 18);
    };

    // Row 1
    drawField("उपनाम", "Surname", surname, 280, 140);
    // Row 2
    drawField("दिया गया नाम", "Given Name", givenNames, 280, 190);
    // Row 3
    drawField("राष्ट्रीयता", "Nationality", nat, 280, 240);
    drawField("लिंग", "Sex", sex, 480, 240);
    drawField("जन्म तिथि", "Date of Birth", dob, 620, 240);
    // Row 4
    drawField("जन्म स्थान", "Place of Birth", pob, 280, 295);
    // Row 5
    drawField("जारी करने की तिथि", "Date of Issue", issueDate, 280, 350);
    drawField("समाप्ति की तिथि", "Date of Expiry", expiry, 480, 350, scenario === "expired_document");

    // Tampering artifact overlay
    if (scenario === "tampering_review") {
      ctx.fillStyle = "rgba(239, 68, 68, 0.35)";
      ctx.fillRect(photoX + 130, photoY + 180, 75, 75);
      ctx.strokeStyle = "#DC2626";
      ctx.lineWidth = 2;
      ctx.strokeRect(photoX + 130, photoY + 180, 75, 75);
      ctx.fillStyle = "#DC2626";
      ctx.font = "bold 11px monospace";
      ctx.fillText("SPLICE", photoX + 140, photoY + 225);
    }

    // 6. ICAO Machine Readable Zone (MRZ)
    ctx.fillStyle = "#FFFFFF";
    ctx.fillRect(30, 480, 900, 125);
    ctx.strokeStyle = "#8FA8C6";
    ctx.lineWidth = 1.5;
    ctx.strokeRect(30, 480, 900, 125);

    ctx.fillStyle = "#000000";
    ctx.font = "bold 23px 'Courier New', 'Courier', monospace";
    ctx.fillText(mrzLine1, 46, 532);
    ctx.fillText(mrzLine2, 46, 580);

    canvas.toBlob((blob) => {
      if (blob) {
        resolve(new File([blob], `passport_${scenario}.jpg`, { type: "image/jpeg" }));
      } else {
        const fallback = new Blob(["sample"], { type: "image/jpeg" });
        resolve(new File([fallback], `passport_${scenario}.jpg`, { type: "image/jpeg" }));
      }
    }, "image/jpeg", 0.95);
  });
}
