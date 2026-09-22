import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../context/AppContext';
import { Header } from '../components/layout/Header';
import { BottomNav } from '../components/layout/BottomNav';
import { verifyAadhaarOtp } from '../services/kycService';

export const AadhaarOtpEkycVerificationPage = () => {
  const navigate = useNavigate();
  const { setUserProfile, speakText, stopAudio, isPlayingAudio, t } = useApp();
  const [otpDigits, setOtpDigits] = useState(['5', '8', '3', '4', '9', '2']);
  const [errorMsg, setErrorMsg] = useState('');

  const toggleAudio = () => {
    if (isPlayingAudio) {
      stopAudio();
    } else {
      speakText(t("kyc.enterOtp"));
    }
  };

  const handleDigitChange = (index, val) => {
    if (val.length > 1) val = val[val.length - 1];
    const newDigits = [...otpDigits];
    newDigits[index] = val;
    setOtpDigits(newDigits);

    if (val && index < 5) {
      const nextInput = document.getElementById(`otp-input-${index + 1}`);
      if (nextInput) nextInput.focus();
    }
  };

  const handleVerify = () => {
    const otp = otpDigits.join('');
    if (otp.length === 6) {
      const res = verifyAadhaarOtp(otp);
      if (res.success) {
        setUserProfile(prev => ({
          ...prev,
          isEkycVerified: true,
          name: res.aadhaarHolderName
        }));
        navigate('/kyc/success');
      } else {
        setErrorMsg(res.message);
      }
    } else {
      setErrorMsg(t("kyc.enterOtp"));
    }
  };

  return (
    <div className="bg-surface-sand text-text-charcoal font-body-md min-h-screen flex flex-col">
      <Header title={t("kyc.title")} showBack />

      <main className="flex-1 w-full max-w-md mx-auto px-4 pt-20 pb-28 flex flex-col gap-5">
        
        {/* Step Badge & Encryption Indicator */}
        <div className="flex flex-col gap-2 pt-1">
          <span className="font-label-sm text-xs font-semibold text-secondary flex items-center gap-1.5 px-3 py-1 rounded-full bg-secondary-container/30 w-fit">
            <span className="w-2 h-2 rounded-full bg-secondary animate-pulse"></span>
            {t("kyc.sub")}
          </span>
          <div className="flex items-center gap-2 text-xs font-semibold text-emerald-800 bg-emerald-50 px-3 py-2 rounded-xl border border-emerald-200">
            <span className="material-symbols-outlined text-[18px]">verified_user</span>
            <span>{t("kyc.encryptedGateway")}</span>
          </div>
        </div>

        {/* OTP Input Card */}
        <section className="bg-surface-warm-white rounded-3xl p-5 shadow-sm border border-border-warm-gray/40 flex flex-col gap-4">
          <div className="flex flex-col gap-1 text-center">
            <h2 className="font-headline-sm text-base font-bold text-text-charcoal">
              {t("kyc.enterOtp")}
            </h2>
            <p className="font-body-sm text-xs text-text-slate">
              {t("kyc.mandatoryConfirm")}
            </p>
          </div>

          <div className="flex items-center justify-center gap-2 my-2">
            {otpDigits.map((digit, index) => (
              <input
                key={index}
                id={`otp-input-${index}`}
                type="text"
                inputMode="numeric"
                maxLength={1}
                value={digit}
                onChange={(e) => handleDigitChange(index, e.target.value)}
                className="w-11 h-13 rounded-xl border-2 border-border-warm-gray text-center font-mono font-bold text-xl text-primary-container focus:border-primary-container focus:outline-none bg-surface-sand/50"
              />
            ))}
          </div>

          <span className="font-label-sm text-xs text-center text-text-slate font-mono">
            {t("kyc.otpExpires")}
          </span>

          {errorMsg && (
            <p className="font-label-sm text-xs text-center text-rose-600 font-semibold">
              {errorMsg}
            </p>
          )}

          <button
            onClick={toggleAudio}
            className="w-full py-2.5 rounded-2xl bg-surface-sand text-secondary font-label-sm text-xs font-semibold hover:bg-surface-dim transition-colors flex items-center justify-center gap-1.5"
            type="button"
          >
            <span className="material-symbols-outlined text-[18px]">
              {isPlayingAudio ? 'stop' : 'volume_up'}
            </span>
            <span>{t("common.listen")}</span>
          </button>
        </section>

        {/* Action Button */}
        <button
          onClick={handleVerify}
          className="w-full py-4 rounded-full bg-primary-container text-on-primary font-label-md text-sm font-semibold hover:bg-primary active:scale-[0.98] transition-all shadow-md flex items-center justify-center gap-2 min-h-[52px]"
          type="button"
        >
          <span>{t("kyc.verifyBtn")}</span>
          <span className="material-symbols-outlined text-[20px]">arrow_forward</span>
        </button>

      </main>

      <BottomNav />
    </div>
  );
};

export default AadhaarOtpEkycVerificationPage;
