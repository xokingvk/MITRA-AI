// Direct Benefit Transfer (DBT) helper service

export const getDbtStatus = (userProfile = null) => {
  return {
    farmerName: userProfile?.name || "Enrolled Beneficiary",
    registrationNo: "REG-2026-ACTIVE",
    totalAmountCredited: "₹0",
    installmentsCompleted: 0,
    bankName: userProfile?.linkedBank || "Bank Account",
    accountNoMasked: "XXXX-XXXX-XXXX",
    npciStatus: "Active",
    history: []
  };
};
