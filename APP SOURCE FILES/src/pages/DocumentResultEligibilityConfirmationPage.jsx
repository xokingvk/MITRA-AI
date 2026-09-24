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

  // Form fields with NO fabricated defaults (null/empty when unknown)
  const [formData, setFormData] = useState({
    name: initialExtracted.name || '',
    age: initialExtracted.age !== null && initialExtracted.age !== undefined ? String(initialExtracted.age) : '',
    gender: initialExtracted.gender || '',
    state: initialExtracted.state || '',
    district: initialExtracted.district || '',
    address: initialExtracted.address || '',
    pincode: initialExtracted.pincode || '',
    annual_income: initialExtracted.annual_income !== null && initialExtracted.annual_income !== undefined ? String(initialExtracted.annual_income) : '',
    occupation: initialExtracted.occupation || '',
    category: initialExtracted.category || '',
    disability_status: initialExtracted.disability_status === true ? 'Yes' : initialExtracted.disability_status === false ? 'No' : '',
    pregnancy_status: initialExtracted.pregnancy_status === true ? 'Yes' : initialExtracted.pregnancy_status === false ? 'No' : ''
  });

  const [matchingResults, setMatchingResults] = useState(null);
  const [loadingMatch, setLoadingMatch] = useState(false);
  const [matchError, setMatchError] = useState(null);
  const [expandedSchemeIdx, setExpandedSchemeIdx] = useState(null);

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const toggleSchemeExpand = (idx) => {
    setExpandedSchemeIdx(prev => prev === idx ? null : idx);
  };

  const handleConfirmAndMatch = async (e) => {
    if (e) e.preventDefault();
    setLoadingMatch(true);
    setMatchError(null);

    // Strictly preserve null for unspecified fields (NO false defaults)
    const confirmedProfile = {
      name: formData.name.trim() || null,
      age: formData.age.trim() ? parseInt(formData.age, 10) : null,
      gender: formData.gender.trim() || null,
      state: formData.state.trim() || null,
      district: formData.district.trim() || null,
      address: formData.address.trim() || null,
      pincode: formData.pincode.trim() || null,
      annual_income: formData.annual_income.trim() ? parseFloat(formData.annual_income) : null,
      occupation: formData.occupation.trim() || null,
      category: formData.category.trim() || null,
      disability_status: formData.disability_status === 'Yes' ? true : formData.disability_status === 'No' ? false : null,
      pregnancy_status: formData.pregnancy_status === 'Yes' ? true : formData.pregnancy_status === 'No' ? false : null
    };

    // Store confirmed profile in AppContext
    setUserProfile(confirmedProfile);

    try {
      const matchResponse = await matchConfirmedProfile(confirmedProfile, language);
      setMatchingResults(matchResponse);
      if (matchResponse && matchResponse.guidance_notes) {
        // Speak short guidance summary only
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

  // Count fields found in document
  const foundFields = [];
  if (initialExtracted.name) foundFields.push("Name");
  if (initialExtracted.age || initialExtracted.date_of_birth) foundFields.push("Age / DOB");
  if (initialExtracted.gender) foundFields.push("Gender");
  if (initialExtracted.state) foundFields.push("State");
  if (initialExtracted.district) foundFields.push("District");
  if (initialExtracted.address) foundFields.push("Address");
  if (initialExtracted.pincode) foundFields.push("PIN Code");

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
              {analysisResult.filename} • Visible facts extracted below
            </p>
          </div>
        </section>

        {/* Found vs Needed Information Summary */}
        <section className="bg-surface-warm-white rounded-3xl p-5 shadow-sm border border-border-warm-gray/40 flex flex-col gap-3">
          <div className="flex flex-col gap-1.5">
            <span className="font-label-sm text-xs font-bold text-emerald-800 flex items-center gap-1.5">
              <span className="material-symbols-outlined text-[16px] text-emerald-600">check_circle</span>
              Information Found from Document ({foundFields.length}):
            </span>
            <div className="flex flex-wrap gap-1.5">
              {foundFields.length > 0 ? (
                foundFields.map((field, i) => (
                  <span key={i} className="px-2.5 py-0.5 rounded-lg bg-emerald-50 text-emerald-800 border border-emerald-200 text-[11px] font-semibold">
                    ✓ {field}
                  </span>
                ))
              ) : (
                <span className="text-xs text-text-slate italic">Basic details detected. Please confirm below.</span>
              )}
            </div>
          </div>

          <div className="pt-2 border-t border-border-warm-gray/30 flex flex-col gap-1.5">
            <span className="font-label-sm text-xs font-bold text-secondary flex items-center gap-1.5">
              <span className="material-symbols-outlined text-[16px]">help</span>
              Information Needed for Scheme Matching:
            </span>
            <p className="font-body-sm text-[11px] text-text-slate leading-relaxed">
              Health schemes determine eligibility based on income, pregnancy, disability, and category. Fill any relevant fields below:
            </p>
          </div>
        </section>

        {/* Editable Profile Confirmation Form */}
        <form onSubmit={handleConfirmAndMatch} className="bg-surface-warm-white rounded-3xl p-5 shadow-sm border border-border-warm-gray/40 flex flex-col gap-4">
          <div className="flex items-center justify-between border-b border-border-warm-gray/30 pb-2">
            <h3 className="font-headline-sm text-sm font-bold text-text-charcoal uppercase tracking-wider">
              Step 1: Review & Complete Profile
            </h3>
            <span className="text-[11px] font-semibold text-secondary">
              Editable
            </span>
          </div>

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
                placeholder="e.g. 28"
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
                <option value="Female">Female</option>
                <option value="Male">Male</option>
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
                placeholder="e.g. Madurai"
                className="p-2.5 rounded-xl border border-border-warm-gray/60 bg-surface-sand/40 focus:outline-none focus:border-primary-container"
              />
            </div>

            <div className="flex flex-col gap-1 col-span-2">
              <label className="font-semibold text-text-slate">Annual Household Income (₹)</label>
              <input
                type="number"
                value={formData.annual_income}
                onChange={(e) => handleInputChange('annual_income', e.target.value)}
                placeholder="e.g. 120000 (leave empty if unknown)"
                className="p-2.5 rounded-xl border border-border-warm-gray/60 bg-surface-sand/40 focus:outline-none focus:border-primary-container"
              />
            </div>

            <div className="flex flex-col gap-1">
              <label className="font-semibold text-text-slate">Occupation</label>
              <input
                type="text"
                value={formData.occupation}
                onChange={(e) => handleInputChange('occupation', e.target.value)}
                placeholder="e.g. Daily Wage Worker"
                className="p-2.5 rounded-xl border border-border-warm-gray/60 bg-surface-sand/40 focus:outline-none focus:border-primary-container"
              />
            </div>

            <div className="flex flex-col gap-1">
              <label className="font-semibold text-text-slate">Social Category</label>
              <select
                value={formData.category}
                onChange={(e) => handleInputChange('category', e.target.value)}
                className="p-2.5 rounded-xl border border-border-warm-gray/60 bg-surface-sand/40 focus:outline-none focus:border-primary-container"
              >
                <option value="">Not Specified</option>
                <option value="General">General</option>
                <option value="OBC">OBC</option>
                <option value="SC">SC</option>
                <option value="ST">ST</option>
                <option value="EWS">EWS</option>
              </select>
            </div>

            <div className="flex flex-col gap-1">
              <label className="font-semibold text-text-slate">Pregnancy Status</label>
              <select
                value={formData.pregnancy_status}
                onChange={(e) => handleInputChange('pregnancy_status', e.target.value)}
                className="p-2.5 rounded-xl border border-border-warm-gray/60 bg-surface-sand/40 focus:outline-none focus:border-primary-container"
              >
                <option value="">Not Specified</option>
                <option value="Yes">Yes (Pregnant / Lactating)</option>
                <option value="No">No</option>
              </select>
            </div>

            <div className="flex flex-col gap-1">
              <label className="font-semibold text-text-slate">Disability Status (PwD)</label>
              <select
                value={formData.disability_status}
                onChange={(e) => handleInputChange('disability_status', e.target.value)}
                className="p-2.5 rounded-xl border border-border-warm-gray/60 bg-surface-sand/40 focus:outline-none focus:border-primary-container"
              >
                <option value="">Not Specified</option>
                <option value="Yes">Yes (PwD)</option>
                <option value="No">No</option>
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
                <span>Evaluating Health Schemes...</span>
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

        {/* Scheme Match Results Section */}
        {matchingResults && (
          <section className="flex flex-col gap-4">
            
            {/* Header: Potentially Relevant Schemes Count */}
            {matchingResults.matching_schemes && matchingResults.matching_schemes.length > 0 ? (
              <div className="flex items-center justify-between px-1">
                <h3 className="font-headline-sm text-base font-bold text-text-charcoal flex items-center gap-2">
                  <span className="material-symbols-outlined text-emerald-600 text-[22px]">verified</span>
                  Potentially Relevant Health Schemes ({matchingResults.matching_schemes.length})
                </h3>
              </div>
            ) : (
              <div className="bg-amber-50 border border-amber-200 rounded-3xl p-5 shadow-sm flex flex-col gap-2">
                <div className="flex items-center gap-2 text-amber-900 font-bold text-sm">
                  <span className="material-symbols-outlined text-[20px]">info</span>
                  <span>More Information Needed</span>
                </div>
                <p className="font-body-sm text-xs text-amber-900 leading-relaxed">
                  More information is needed to identify schemes that may be relevant to you.
                </p>
                {matchingResults.missing_information && matchingResults.missing_information.length > 0 && (
                  <div className="flex flex-wrap gap-1.5 pt-1">
                    {matchingResults.missing_information.map((item, idx) => (
                      <span key={idx} className="px-2.5 py-1 rounded-full bg-white border border-amber-300 text-amber-900 text-[11px] font-semibold">
                        + Please provide {item}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            )}

            {matchingResults.guidance_notes && (
              <div className="bg-surface-warm-white rounded-3xl p-4 shadow-sm border border-border-warm-gray/40">
                <p className="font-body-sm text-xs text-text-charcoal leading-relaxed">
                  {matchingResults.guidance_notes}
                </p>
              </div>
            )}

            {/* Scheme Cards */}
            {matchingResults.matching_schemes && matchingResults.matching_schemes.length > 0 && (
              <div className="flex flex-col gap-3">
                {matchingResults.matching_schemes.map((scheme, idx) => {
                  const isExpanded = expandedSchemeIdx === idx;
                  return (
                    <div
                      key={idx}
                      className="bg-surface-warm-white rounded-3xl p-5 shadow-sm border border-border-warm-gray/40 flex flex-col gap-3 transition-all"
                    >
                      {/* Card Header: Scheme Name & Status Badge */}
                      <div className="flex flex-col gap-1">
                        <div className="flex items-start justify-between gap-2">
                          <h4 className="font-headline-sm text-sm font-bold text-text-charcoal">
                            {scheme.scheme_name}
                          </h4>
                          <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-50 text-emerald-800 border border-emerald-200 whitespace-nowrap flex-shrink-0">
                            {scheme.eligibility_status || "Potentially relevant"}
                          </span>
                        </div>

                        <p className="font-body-sm text-xs text-text-charcoal leading-relaxed">
                          {scheme.short_description || scheme.key_benefits}
                        </p>

                        {scheme.why_it_matches && (
                          <div className="flex items-center gap-1 text-[11px] text-secondary font-medium mt-0.5">
                            <span className="material-symbols-outlined text-[14px]">lightbulb</span>
                            <span>{scheme.why_it_matches}</span>
                          </div>
                        )}
                      </div>

                      {/* View Details Toggle Button */}
                      <button
                        onClick={() => toggleSchemeExpand(idx)}
                        className="w-full py-2.5 px-4 rounded-xl bg-surface-sand/80 hover:bg-surface-sand active:bg-surface-dim text-text-charcoal text-xs font-semibold flex items-center justify-between transition-colors border border-border-warm-gray/30"
                        type="button"
                      >
                        <span className="flex items-center gap-1.5">
                          <span className="material-symbols-outlined text-[16px] text-primary-container">info</span>
                          <span>{isExpanded ? 'Hide Details' : 'View Details'}</span>
                        </span>
                        <span className="material-symbols-outlined text-[18px] text-text-slate transition-transform duration-200" style={{ transform: isExpanded ? 'rotate(180deg)' : 'rotate(0deg)' }}>
                          expand_more
                        </span>
                      </button>

                      {/* Detailed Scheme Breakdown (Expanded View) */}
                      {isExpanded && (
                        <div className="pt-2 border-t border-border-warm-gray/30 flex flex-col gap-3 text-xs animate-fadeIn">
                          {scheme.key_benefits && (
                            <div className="bg-emerald-50/60 border border-emerald-100 p-3 rounded-2xl">
                              <span className="font-bold text-emerald-950 block mb-0.5">Key Benefits:</span>
                              <span className="text-emerald-900 leading-relaxed">{scheme.key_benefits}</span>
                            </div>
                          )}

                          {scheme.required_documents && scheme.required_documents.length > 0 && (
                            <div className="flex flex-col gap-1.5">
                              <span className="font-bold text-text-charcoal">Required Documents:</span>
                              <div className="flex flex-wrap gap-1.5">
                                {scheme.required_documents.map((doc, dIdx) => (
                                  <span key={dIdx} className="px-2.5 py-1 rounded-lg bg-surface-sand text-text-slate text-[11px] font-medium border border-border-warm-gray/30">
                                    📄 {doc}
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}

                          <div className="p-2.5 bg-amber-50/70 border border-amber-200/60 rounded-xl text-[11px] text-amber-900 leading-relaxed">
                            ℹ️ This scheme may be relevant based on your profile. Official enrollment is confirmed upon verification at your local healthcare center or official portal.
                          </div>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </section>
        )}

      </main>

      <BottomNav />
    </div>
  );
};

export default DocumentResultEligibilityConfirmationPage;
