// Mock Aadhaar OTP and NPCI e-KYC service

export const generateAadhaarOtp = (aadhaarNumber = "XXXX-XXXX-4892") => {
  return {
    success: true,
    message: `OTP sent successfully to registered mobile ending with ****8921`,
    maskedMobile: "+91 ***** *8921",
    aadhaarNumber: aadhaarNumber,
    validForSeconds: 300
  };
};

export const verifyAadhaarOtp = (otp) => {
  if (otp.length === 6) {
    return {
      success: true,
      verificationId: "KYC-2026-99214-A",
      aadhaarHolderName: "Ramesh Kumar",
      dob: "14-08-1978",
      gender: "Male",
      address: "Village Vaduvur, District Thanjavur, Tamil Nadu - 614019",
      npciLinkStatus: "NPCI Mandate Created - Pending Bank Confirmation",
      linkedBank: "State Bank of India (A/C ****4091)"
    };
  } else {
    return {
      success: false,
      message: "Invalid OTP. Please enter 6-digit Aadhaar OTP."
    };
  }
};

export const submitNpciMandateToBank = () => {
  return {
    success: true,
    ackNumber: "ACK-NPCI-2026-88192",
    timestamp: new Date().toLocaleString(),
    bankName: "State Bank of India",
    branchName: "Vaduvur Branch",
    counterNumber: "Counter 3 (DBT Helpdesk)",
    officerName: "S. Swaminathan (Senior Assistant)",
    status: "Bank Receipt Generated - Ready for Counter 3 Submission"
  };
};
