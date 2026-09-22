import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AppProvider } from './context/AppContext';

import HomeVoiceAssistantPage from './pages/HomeVoiceAssistantPage';
import ActiveVoiceListeningPage from './pages/ActiveVoiceListeningPage';
import AiResponseSchemeResultsPage from './pages/AiResponseSchemeResultsPage';
import SchemesDiscoveryFiltersPage from './pages/SchemesDiscoveryFiltersPage';
import PmKisanSchemeDetailsPage from './pages/PmKisanSchemeDetailsPage';
import PmKisanConversationalEligibilityPage from './pages/PmKisanConversationalEligibilityPage';
import DocumentUploadVerificationPage from './pages/DocumentUploadVerificationPage';
import DocumentAnalyzingPage from './pages/DocumentAnalyzingPage';
import DocumentResultEligibilityConfirmationPage from './pages/DocumentResultEligibilityConfirmationPage';
import PmKisanFinalEligibilityResultPage from './pages/PmKisanFinalEligibilityResultPage';
import AadhaarOtpEkycVerificationPage from './pages/AadhaarOtpEkycVerificationPage';
import EkycSuccessDbtConfirmationPage from './pages/EkycSuccessDbtConfirmationPage';
import PreFilledNpciMandatePdfPreviewPage from './pages/PreFilledNpciMandatePdfPreviewPage';
import BankCounterSubmissionAcknowledgementPage from './pages/BankCounterSubmissionAcknowledgementPage';
import MyEnrolledSchemesBenefitsTrackerPage from './pages/MyEnrolledSchemesBenefitsTrackerPage';
import MyEnrolledSchemes2000CreditedPage from './pages/MyEnrolledSchemes2000CreditedPage';
import PmKisanDbtTrackingInstallmentStatusPage from './pages/PmKisanDbtTrackingInstallmentStatusPage';
import PmKisanDbtTransactionErrorRemediationPage from './pages/PmKisanDbtTransactionErrorRemediationPage';
import OfficialDbtCreditReceiptSlipPage from './pages/OfficialDbtCreditReceiptSlipPage';
import ChatHistoryPreviousConversationsPage from './pages/ChatHistoryPreviousConversationsPage';
import SettingsAccessibilityPage from './pages/SettingsAccessibilityPage';
import WhatsappShareFamilyInstructionsPage from './pages/WhatsappShareFamilyInstructionsPage';
import ForwardedWhatsappThreadPage from './pages/ForwardedWhatsappThreadPage';
import WhatsappVoiceNoteDialogPage from './pages/WhatsappVoiceNoteDialogPage';

export default function App() {
  return (
    <AppProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<HomeVoiceAssistantPage />} />
          <Route path="/active-voice" element={<ActiveVoiceListeningPage />} />
          <Route path="/search-results" element={<AiResponseSchemeResultsPage />} />
          <Route path="/schemes" element={<SchemesDiscoveryFiltersPage />} />
          <Route path="/scheme/pm-kisan" element={<PmKisanSchemeDetailsPage />} />
          <Route path="/scheme/:schemeId" element={<PmKisanSchemeDetailsPage />} />
          <Route path="/scheme/pm-kisan/check" element={<PmKisanConversationalEligibilityPage />} />
          <Route path="/document-upload" element={<DocumentUploadVerificationPage />} />
          <Route path="/document-analyzing" element={<DocumentAnalyzingPage />} />
          <Route path="/document-result" element={<DocumentResultEligibilityConfirmationPage />} />
          <Route path="/scheme/pm-kisan/result" element={<PmKisanFinalEligibilityResultPage />} />
          <Route path="/kyc/aadhaar-otp" element={<AadhaarOtpEkycVerificationPage />} />
          <Route path="/kyc/success" element={<EkycSuccessDbtConfirmationPage />} />
          <Route path="/kyc/npci-mandate" element={<PreFilledNpciMandatePdfPreviewPage />} />
          <Route path="/kyc/bank-acknowledgement" element={<BankCounterSubmissionAcknowledgementPage />} />
          <Route path="/my-schemes" element={<MyEnrolledSchemesBenefitsTrackerPage />} />
          <Route path="/my-schemes/credited" element={<MyEnrolledSchemes2000CreditedPage />} />
          <Route path="/dbt-tracker" element={<PmKisanDbtTrackingInstallmentStatusPage />} />
          <Route path="/dbt-error-remediation" element={<PmKisanDbtTransactionErrorRemediationPage />} />
          <Route path="/dbt-receipt" element={<OfficialDbtCreditReceiptSlipPage />} />
          <Route path="/chat-history" element={<ChatHistoryPreviousConversationsPage />} />
          <Route path="/settings" element={<SettingsAccessibilityPage />} />
          <Route path="/whatsapp-share" element={<WhatsappShareFamilyInstructionsPage />} />
          <Route path="/whatsapp-thread" element={<ForwardedWhatsappThreadPage />} />
          <Route path="/whatsapp-voice-dialog" element={<WhatsappVoiceNoteDialogPage />} />
        </Routes>
      </BrowserRouter>
    </AppProvider>
  );
}
