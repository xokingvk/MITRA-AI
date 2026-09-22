// Mock DBT transaction status and remediation data

export const DBT_STATUS_DATA = {
  farmerName: "Ramesh Kumar",
  registrationNo: "TN-PMK-2024-991204",
  totalAmountCredited: "₹32,000",
  installmentsCompleted: 16,
  lastCreditDate: "2026-08-15",
  lastCreditAmount: "₹2,000",
  bankName: "State Bank of India",
  accountNoMasked: "XXXX-XXXX-4091",
  ifscCode: "SBIN0001842",
  npciStatus: "Aadhaar Seeding Verification Pending at Bank Branch",
  pendingInstallment: {
    number: "17th Installment",
    amount: "₹2,000",
    dueDate: "2026-11-30",
    issue: "NPCI Mapping Inactive",
    remediationActionRequired: "Submit pre-filled NPCI Aadhaar seeding form to SBI Vaduvur Counter 3 or verify OTP online."
  },
  history: [
    { installment: "16th Installment", amount: "₹2,000", date: "15 Aug 2026", status: "Success", refNo: "DBT2026081599812" },
    { installment: "15th Installment", amount: "₹2,000", date: "14 Apr 2026", status: "Success", refNo: "DBT2026041487612" },
    { installment: "14th Installment", amount: "₹2,000", date: "27 Nov 2025", status: "Success", refNo: "DBT2025112765419" },
    { installment: "13th Installment", amount: "₹2,000", date: "27 Jul 2025", status: "Success", refNo: "DBT2025072743210" }
  ]
};

export const getDbtStatus = () => DBT_STATUS_DATA;
