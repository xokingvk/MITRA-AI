import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../context/AppContext';
import { Header } from '../components/layout/Header';
import { BottomNav } from '../components/layout/BottomNav';
import { matchConfirmedProfile } from '../services/api';

export const DocumentResultEligibilityConfirmationPage = () => {
  const navigate = useNavigate();
  const { analysisResult, language, setUserProfile, speakText, isPlayingAudio, stopAudio, t } = useApp();

  const initialExtracted = analysisResult?.extracted_profile || {};

  const [formData, setFormData] = useState({
    name: initialExtracted.name || '',
    age: initialExtracted.age !== null && initialExtracted.age !== undefined ? String(initialExtracted.age) : '',
    gender: initialExtracted.gender || '',
    state: initialExtracted.state || '',
    district: initialExtracted.district || '',
    annual_income: initialExtracted.annual_income !== null && initialExtracted.annual_income !== undefined ? String(initialExtracted.annual_income) : '',
    occupation: initialExtracted.occupation || '',
    disability_status: initialExtracted.disability_status ? 'Yes' : 'No'
  });

  const [matchingResults, setMatchingResults] = useState(null);
  const [loadingMatch, setLoadingMatch] = useState(false);
  const [matchError, setMatchError] = useState(null);

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleConfirmAndMatch = async (e) => {
    if (e) e.preventDefault();
    setLoadingMatch(true);
    setMatchError(null);

    const confirmedProfile = {
      name: formData.name.trim() || null,
      age: formData.age.trim() ? parseInt(formData.age, 10) : null,
      gender: formData.gender.trim() || null,
      state: formData.state.trim() || null,
      district: formData.district.trim() || null,
      annual_income: formData.annual_income.trim() ? parseFloat(formData.annual_income) : null,
      occupation: formData.occupation.trim() || null,
      disability_status: formData.disability_status === 'Yes'
    };

    // Store confirmed profile in AppContext
    setUserProfile(confirmedProfile);

    try {
      const matchResponse = await matchConfirmedProfile(confirmedProfile, language);
      setMatchingResults(matchResponse);
      if (matchResponse && matchResponse.guidance_notes) {
        speakText(matchResponse.guidance_notes);
      }
    } catch (err) {
      console.error("Scheme matching failed:", err);
      setMatchError(err.message || "Failed to match profile against official health scheme corpus.");
    } finally {
      setLoadingMatch(false);
    }
  };

  if (!analysisResult) {
    return (
      <div className="bg-surface-sand text-text-charcoal font-body-md min-h-screen flex flex-col">
        <Header title={t("doc.title")} showBack />
        <main className="flex-1 w-full max-w-md mx-auto px-4 pt-20 pb-28 flex flex-col gap-5 items-center justify-center text-center">
          <div className="bg-surface-warm-white rounded-3xl p-6 shadow-sm border border-border-warm-gray/40 flex flex-col items-center gap-4 w-full">
            <span className="material-symbols-outlined text-[48px] text-text-slate">upload_file</span>
            <h2 className="font-headline-sm text-lg font-bold text-text-charcoal">No Document Uploaded</h2>
            <p className="font-body-sm text-xs text-text-slate">Please upload a document to extract information and check scheme eligibility.</p>
            <button
              onClick={() => navigate('/document-upload')}
              className="py-3 px-6 rounded-full bg-primary-container text-on-primary font-label-md text-sm font-semibold hover:bg-primary transition-all shadow-md"
              type="button"
            >
              Upload Document
            </button>
          </div>
        </main>
        <BottomNav />
      </div>
    );
  }

  return (
    <div className="bg-surface-sand text-text-charcoal font-body-md min-h-screen flex flex-col">
      <Header title="Document Extraction & Matching" showBack />

      <main className="flex-1 w-full max-w-md mx-auto px-4 pt-20 pb-28 flex flex-col gap-5">
        
        {/* Verification Success Header */}
        <section className="bg-emerald-50 border border-emerald-200 rounded-3xl p-5 shadow-sm flex items-center gap-4">
          <div className="w-12 h-12 rounded-2xl bg-emerald-500 text-white flex items-center justify-center flex-shrink-0 shadow-md">
            <span className="material-symbols-outlined text-[28px]">description</span>
          </div>
          <div className="min-w-0">
            <h2 className="font-headline-sm text-base font-bold text-emerald-950">
              Document Processed
            </h2>
            <p className="font-body-sm text-xs text-emerald-800 mt-0.5 truncate">
              {analysisResult.filename} • Review and edit extracted fields below
            </p>
          </div>
        </section>

        {/* STEP 5: Editable Profile Confirmation Form */}
        <form onSubmit={handleConfirmAndMatch} className="bg-surface-warm-white rounded-3xl p-5 shadow-sm border border-border-warm-gray/40 flex flex-col gap-4">
          <div className="flex items-center justify-between border-b border-border-warm-gray/30 pb-2">
            <h3 className="font-headline-sm text-sm font-bold text-text-charcoal uppercase tracking-wider">
              Step 1: Confirm Profile Details
            </h3>
            <span className="text-[11px] font-semibold text-secondary">
              Editable Form
            </span>
          </div>

          <p className="font-body-sm text-xs text-text-slate">
            Gemini extracted the information below from your uploaded document. Correct any field or add missing values before matching schemes.
          </p>

          <div className="grid grid-cols-2 gap-3 text-xs">
            <div className="flex flex-col gap-1 col-span-2">
              <label className="font-semibold text-text-slate">Full Name</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => handleInputChange('name', e.target.value)}
                placeholder="Enter full name"
                className="p-2.5 rounded-xl border border-border-warm-gray/60 bg-surface-sand/40 focus:outline-none focus:border-primary-container"
              />
            </div>

            <div className="flex flex-col gap-1">
              <label className="font-semibold text-text-slate">Age (Years)</label>
              <input
                type="number"
                value={formData.age}
                onChange={(e) => handleInputChange('age', e.target.value)}
                placeholder="e.g. 45"
                className="p-2.5 rounded-xl border border-border-warm-gray/60 bg-surface-sand/40 focus:outline-none focus:border-primary-container"
              />
            </div>

            <div className="flex flex-col gap-1">
              <label className="font-semibold text-text-slate">Gender</label>
              <select
                value={formData.gender}
                onChange={(e) => handleInputChange('gender', e.target.value)}
                className="p-2.5 rounded-xl border border-border-warm-gray/60 bg-surface-sand/40 focus:outline-none focus:border-primary-container"
              >
                <option value="">Not Specified</option>
                <option value="Male">Male</option>
                <option value="Female">Female</option>
                <option value="Other">Other</option>
              </select>
            </div>

            <div className="flex flex-col gap-1">
              <label className="font-semibold text-text-slate">State</label>
              <input
                type="text"
                value={formData.state}
                onChange={(e) => handleInputChange('state', e.target.value)}
                placeholder="e.g. Tamil Nadu"
                className="p-2.5 rounded-xl border border-border-warm-gray/60 bg-surface-sand/40 focus:outline-none focus:border-primary-container"
              />
            </div>

            <div className="flex flex-col gap-1">
              <label className="font-semibold text-text-slate">District</label>
              <input
                type="text"
                value={formData.district}
                onChange={(e) => handleInputChange('district', e.target.value)}
                placeholder="e.g. Thanjavur"
                className="p-2.5 rounded-xl border border-border-warm-gray/60 bg-surface-sand/40 focus:outline-none focus:border-primary-container"
              />
            </div>

            <div className="flex flex-col gap-1 col-span-2">
              <label className="font-semibold text-text-slate">Annual Household Income (₹)</label>
              <input
                type="number"
                value={formData.annual_income}
                onChange={(e) => handleInputChange('annual_income', e.target.value)}
                placeholder="e.g. 120000"
                className="p-2.5 rounded-xl border border-border-warm-gray/60 bg-surface-sand/40 focus:outline-none focus:border-primary-container"
              />
            </div>

            <div className="flex flex-col gap-1">
              <label className="font-semibold text-text-slate">Occupation</label>
              <input
                type="text"
                value={formData.occupation}
                onChange={(e) => handleInputChange('occupation', e.target.value)}
                placeholder="e.g. Farmer / Worker"
                className="p-2.5 rounded-xl border border-border-warm-gray/60 bg-surface-sand/40 focus:outline-none focus:border-primary-container"
              />
            </div>

            <div className="flex flex-col gap-1">
              <label className="font-semibold text-text-slate">Disability Status</label>
              <select
                value={formData.disability_status}
                onChange={(e) => handleInputChange('disability_status', e.target.value)}
                className="p-2.5 rounded-xl border border-border-warm-gray/60 bg-surface-sand/40 focus:outline-none focus:border-primary-container"
              >
                <option value="No">No</option>
                <option value="Yes">Yes (PwD)</option>
              </select>
            </div>
          </div>

          <button
            type="submit"
            disabled={loadingMatch}
            className="w-full mt-2 py-4 rounded-full bg-primary-container text-on-primary font-label-md text-sm font-semibold hover:bg-primary active:scale-[0.98] transition-all shadow-md flex items-center justify-center gap-2 min-h-[52px]"
          >
            {loadingMatch ? (
              <>
                <span className="material-symbols-outlined text-[20px] animate-spin">sync</span>
                <span>Matching Against Scheme Corpus...</span>
              </>
            ) : (
              <>
                <span>Step 2: Confirm Information & Match Schemes</span>
                <span className="material-symbols-outlined text-[20px]">arrow_forward</span>
              </>
            )}
          </button>
        </form>

        {matchError && (
          <div className="p-4 bg-red-50 border border-red-200 text-red-900 rounded-2xl text-xs font-semibold">
            {matchError}
          </div>
        )}

        {/* STEP 6: Scheme Match Results Display */}
        {matchingResults && (
          <section className="flex flex-col gap-4">
            <div className="flex items-center justify-between">
              <h3 className="font-headline-sm text-base font-bold text-text-charcoal flex items-center gap-2">
                <span className="material-symbols-outlined text-emerald-600 text-[22px]">verified</span>
                Matched Health Schemes ({matchingResults.matching_schemes?.length || 0})
              </h3>
            </div>

            {matchingResults.guidance_notes && (
              <div className="bg-surface-warm-white rounded-3xl p-5 shadow-sm border border-border-warm-gray/40">
                <p className="font-body-sm text-xs text-text-charcoal leading-relaxed">
                  {matchingResults.guidance_notes}
                </p>
              </div>
            )}

            <div className="flex flex-col gap-3">
              {matchingResults.matching_schemes?.map((scheme, idx) => {
                const statusColor = 
                  scheme.eligibility_status === 'Eligible' ? 'bg-emerald-100 text-emerald-800 border-emerald-300' :
                  scheme.eligibility_status === 'Potentially eligible' ? 'bg-amber-100 text-amber-800 border-amber-300' :
                  scheme.eligibility_status === 'Not eligible' ? 'bg-red-100 text-red-800 border-red-300' :
                  'bg-slate-100 text-slate-800 border-slate-300';

                return (
                  <div key={idx} className="bg-surface-warm-white rounded-3xl p-5 shadow-sm border border-border-warm-gray/40 flex flex-col gap-3">
                    <div className="flex items-start justify-between gap-2">
                      <h4 className="font-headline-sm text-sm font-bold text-text-charcoal">
                        {scheme.scheme_name}
                      </h4>
                      <span className={`px-2.5 py-1 rounded-full text-[11px] font-bold border whitespace-nowrap ${statusColor}`}>
                        {scheme.eligibility_status}
                      </span>
                    </div>

                    <p className="font-body-sm text-xs text-text-slate leading-relaxed">
                      {scheme.why_it_matches}
                    </p>

                    {scheme.key_benefits && (
                      <div className="bg-surface-sand/60 p-3 rounded-2xl text-xs text-text-charcoal">
                        <span className="font-bold block mb-0.5 text-primary-container">Key Benefits:</span>
                        <span>{scheme.key_benefits}</span>
                      </div>
                    )}

                    {scheme.required_documents && scheme.required_documents.length > 0 && (
                      <div className="flex flex-wrap gap-1.5 pt-1">
                        {scheme.required_documents.map((doc, dIdx) => (
                          <span key={dIdx} className="px-2 py-0.5 rounded-lg bg-surface-sand text-text-slate text-[10px] font-semibold">
                            📄 {doc}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </section>
        )}

      </main>

      <BottomNav />
    </div>
  );
};

export default DocumentResultEligibilityConfirmationPage;
