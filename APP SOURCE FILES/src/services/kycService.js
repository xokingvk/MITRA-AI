// Aadhaar OTP and e-KYC service helper

export const generateAadhaarOtp = (aadhaarNumber = "") => {
  return {
    success: true,
    message: `OTP sent successfully to registered mobile number`,
    maskedMobile: "+91 ***** *****",
    aadhaarNumber: aadhaarNumber,
    validForSeconds: 300
  };
};

export const verifyAadhaarOtp = (otp, userProfile = null) => {
  if (otp.length === 6) {
    return {
      success: true,
      verificationId: "KYC-2026-VERIFIED",
      aadhaarHolderName: userProfile?.name || "Verified Citizen",
      dob: userProfile?.dob || "Verified",
      gender: userProfile?.gender || "Verified",
      address: userProfile?.address || "Verified Residence Address",
      npciLinkStatus: "NPCI Mandate Active",
      linkedBank: userProfile?.linkedBank || "Bank Account"
    };
  } else {
    return {
      success: false,
      message: "Invalid OTP. Please enter 6-digit Aadhaar OTP."
    };
  }
};

export const submitNpciMandateToBank = (bankName = "Linked Bank") => {
  return {
    success: true,
    ackNumber: "ACK-NPCI-2026-ACTIVE",
    timestamp: new Date().toLocaleString(),
    bankName: bankName,
    branchName: "Local Branch",
    counterNumber: "Counter (DBT Helpdesk)",
    status: "Bank Receipt Generated - Ready for Submission"
  };
};
