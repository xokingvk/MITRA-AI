// Mock OCR document analysis service

export const analyzeUploadedDocument = (file) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        success: true,
        documentType: "Land Ownership Certificate (Patta Passbook)",
        extractedData: {
          ownerName: "Ramesh Kumar S/o V. Swaminathan",
          landSize: "1.85 Acres (0.75 Hectares)",
          surveyNumber: "241/3B",
          village: "Vaduvur",
          district: "Thanjavur",
          state: "Tamil Nadu",
          issuingAuthority: "Tahsildar, Needamangalam"
        },
        eligibilityCheck: {
          status: "Eligible for PM-Kisan",
          reason: "Landholding size (1.85 acres) is under 2.0 hectares limit for small and marginal farmers.",
          confidenceScore: "98.5%"
        }
      });
    }, 2000);
  });
};
