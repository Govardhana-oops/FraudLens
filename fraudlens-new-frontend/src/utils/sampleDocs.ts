/**
 * Utility to generate client-side synthetic document samples for Demo Scenarios
 */

export type DemoScenario = "valid_passport" | "expired_document" | "ocr_uncertainty" | "tampering_review" | "face_review";

export function generateSyntheticDocumentFile(scenario: DemoScenario): Promise<File> {
  return new Promise((resolve) => {
    const canvas = document.createElement("canvas");
    canvas.width = 900;
    canvas.height = 600;
    const ctx = canvas.getContext("2d");
    if (!ctx) {
      const blob = new Blob(["sample"], { type: "image/png" });
      return resolve(new File([blob], "sample_document.png", { type: "image/png" }));
    }

    // 1. Background
    ctx.fillStyle = "#f1f5f9";
    ctx.fillRect(0, 0, 900, 600);

    // Security pattern lines
    ctx.strokeStyle = "rgba(148, 163, 184, 0.25)";
    ctx.lineWidth = 1;
    for (let i = 0; i < 900; i += 20) {
      ctx.beginPath();
      ctx.moveTo(i, 0);
      ctx.lineTo(i + 100, 600);
      ctx.stroke();
    }

    // 2. Header banner
    ctx.fillStyle = "#1e293b";
    ctx.fillRect(0, 0, 900, 70);

    ctx.fillStyle = "#ffffff";
    ctx.font = "bold 26px sans-serif";
    ctx.fillText("PASSPORT — UTOPIA FEDERATION", 40, 46);

    // 3. Photo area
    ctx.fillStyle = "#cbd5e1";
    ctx.fillRect(50, 110, 200, 260);
    ctx.fillStyle = "#475569";
    ctx.font = "bold 16px sans-serif";
    ctx.fillText("TRAVELER PHOTO", 75, 245);

    // Simulated Tampering if scenario is tampering_review
    if (scenario === "tampering_review") {
      ctx.fillStyle = "rgba(239, 68, 68, 0.4)";
      ctx.fillRect(180, 280, 70, 70);
      ctx.fillStyle = "#dc2626";
      ctx.font = "12px sans-serif";
      ctx.fillText("SPLICE", 190, 320);
    }

    // 4. Visual Inspection Zone fields
    ctx.fillStyle = "#0f172a";
    ctx.font = "bold 15px sans-serif";

    let surname = "DOE";
    let givenNames = "JOHN ALEXANDER";
    let docNum = "P12345678";
    let dob = "15 JAN 1988";
    let expiry = "15 JAN 2030";
    let nat = "UTO";
    let sex = "M";

    let mrzLine1 = "P<UTODOE<<JOHN<ALEXANDER<<<<<<<<<<<<<<<<<<<<";
    let mrzLine2 = "P123456784UTO8801152M3001158<<<<<<<<<<<<<<02";

    if (scenario === "expired_document") {
      expiry = "15 JAN 2022";
      mrzLine2 = "P123456784UTO8801152M2201158<<<<<<<<<<<<<<02";
    } else if (scenario === "ocr_uncertainty") {
      docNum = "P18X?99#";
      surname = "D~E";
      givenNames = "J*HN";
    } else if (scenario === "tampering_review") {
      surname = "GARCIA";
      docNum = "P99887766";
      mrzLine1 = "P<UTOGARCIA<<MARIA<<<<<<<<<<<<<<<<<<<<<<<<<<";
      mrzLine2 = "P998877668UTO8508124F3208128<<<<<<<<<<<<<<<2";
    }

    ctx.fillText("Type / Type: P", 300, 130);
    ctx.fillText("Country Code / Pays: " + nat, 540, 130);
    ctx.fillText("Passport No. / No du Passeport: " + docNum, 300, 175);
    ctx.fillText("Surname / Nom: " + surname, 300, 220);
    ctx.fillText("Given Names / Prenoms: " + givenNames, 300, 265);
    ctx.fillText("Nationality / Nationalite: " + nat, 300, 310);
    ctx.fillText("Date of Birth / Date de Naissance: " + dob, 300, 355);
    ctx.fillText("Sex / Sexe: " + sex + "     Date of Expiry / Date d'expiration: " + expiry, 300, 400);

    // 5. MRZ Machine Readable Zone
    ctx.fillStyle = "#ffffff";
    ctx.fillRect(30, 460, 840, 115);
    ctx.strokeStyle = "#94a3b8";
    ctx.strokeRect(30, 460, 840, 115);

    ctx.fillStyle = "#000000";
    ctx.font = "bold 20px 'Courier New', monospace";
    ctx.fillText(mrzLine1, 45, 505);
    ctx.fillText(mrzLine2, 45, 548);

    canvas.toBlob((blob) => {
      if (blob) {
        resolve(new File([blob], `passport_${scenario}.png`, { type: "image/png" }));
      } else {
        const fallback = new Blob(["sample"], { type: "image/png" });
        resolve(new File([fallback], `passport_${scenario}.png`, { type: "image/png" }));
      }
    }, "image/png");
  });
}
