import React, { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../context/AppContext';
import { Header } from '../components/layout/Header';
import { BottomNav } from '../components/layout/BottomNav';
import { SCHEMES_DATA } from '../services/schemeService';

export const SchemesDiscoveryFiltersPage = () => {
  const navigate = useNavigate();
  const { searchQuery, setSearchQuery, t } = useApp();
  
  const [activeTabCategory, setActiveTabCategory] = useState("All");
  const [visibleCount, setVisibleCount] = useState(20);

  const categories = [
    { label: t("schemes.filterAll"), name: "All", icon: "apps" },
    { label: t("schemes.filterHealthAccess"), name: "Health Access & Financial Protection", icon: "💳" },
    { label: t("schemes.filterMaternal"), name: "Maternal & Reproductive Health", icon: "🤱" },
    { label: t("schemes.filterChild"), name: "Newborn, Child & Adolescent Health", icon: "👶" },
    { label: t("schemes.filterNutrition"), name: "Immunization, Nutrition & Preventive Health", icon: "💉" },
    { label: t("schemes.filterCommunicable"), name: "Communicable Disease Control", icon: "🦠" },
    { label: t("schemes.filterNonCommunicable"), name: "Non-Communicable, Mental Health & Geriatric Care", icon: "🧠" },
    { label: t("schemes.filterDisability"), name: "Disability, Rehabilitation & Assistive Care", icon: "♿" },
    { label: t("schemes.filterAyush"), name: "AYUSH & Traditional Healthcare", icon: "🌿" },
    { label: t("schemes.filterEmergency"), name: "Health Systems, Emergency & Digital Health", icon: "🚑" }
  ];

  const filteredSchemes = useMemo(() => {
    const query = (searchQuery || "").toLowerCase().trim();
    return SCHEMES_DATA.filter(s => {
      const matchesCat = activeTabCategory === "All" || s.category.toLowerCase() === activeTabCategory.toLowerCase();
      const matchesQuery = !query || 
        s.title.toLowerCase().includes(query) || 
        s.shortDescription.toLowerCase().includes(query) ||
        s.category.toLowerCase().includes(query) ||
        s.genderEligible.toLowerCase().includes(query);
      return matchesCat && matchesQuery;
    });
  }, [activeTabCategory, searchQuery]);

  const displayedSchemes = filteredSchemes.slice(0, visibleCount);

  return (
    <div className="bg-surface-sand text-text-charcoal font-body-md min-h-screen flex flex-col">
      <Header title={t("schemes.title")} />

      <main className="flex-1 w-full max-w-md mx-auto px-4 pt-20 pb-28 flex flex-col gap-4">
        
        {/* Search Bar */}
        <section className="sticky top-[64px] z-30 pt-1 pb-2 bg-surface-sand">
          <div className="w-full bg-surface-warm-white rounded-2xl p-2 border border-border-warm-gray/50 shadow-sm flex items-center gap-2">
            <span className="material-symbols-outlined text-text-slate ml-2 text-[20px]">search</span>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                setVisibleCount(20);
              }}
              placeholder={t("schemes.searchPlaceholder")}
              className="flex-1 min-w-0 bg-transparent text-text-charcoal font-body-md text-sm placeholder:text-text-slate focus:outline-none py-1"
            />
            {searchQuery && (
              <button
                onClick={() => {
                  setSearchQuery('');
                  setVisibleCount(20);
                }}
                className="w-8 h-8 rounded-full flex items-center justify-center text-text-slate hover:bg-surface-sand"
                type="button"
              >
                <span className="material-symbols-outlined text-[18px]">close</span>
              </button>
            )}
          </div>
        </section>

        {/* Clean Category Chips */}
        <section className="flex items-center gap-2 overflow-x-auto pb-1 scrollbar-none">
          {categories.map((cat) => {
            const isSelected = activeTabCategory === cat.name;
            return (
              <button
                key={cat.name}
                onClick={() => {
                  setActiveTabCategory(cat.name);
                  setVisibleCount(20);
                }}
                className={`px-3.5 py-2 rounded-full font-label-md text-xs font-semibold whitespace-nowrap flex items-center gap-1.5 transition-all min-h-[40px] ${
                  isSelected
                    ? 'bg-primary-container text-on-primary shadow-sm'
                    : 'bg-surface-warm-white text-text-charcoal border border-border-warm-gray/40 hover:bg-surface-sand'
                }`}
                type="button"
              >
                <span>{cat.icon}</span>
                <span>{cat.label}</span>
              </button>
            );
          })}
        </section>

        {/* Total Count Badge */}
        <div className="flex items-center justify-between text-xs text-text-slate font-semibold px-1">
          <span>{filteredSchemes.length} {t("schemes.title")}</span>
          <span>{t("common.showing")} {displayedSchemes.length} {t("common.of")} {filteredSchemes.length}</span>
        </div>

        {/* Scheme Cards List */}
        <section className="flex flex-col gap-3.5">
          {displayedSchemes.map((scheme) => (
            <div
              key={scheme.id}
              className="w-full bg-surface-warm-white rounded-3xl p-5 shadow-sm border border-border-warm-gray/40 flex flex-col gap-3 hover:shadow-md transition-all"
            >
              <div className="flex items-start justify-between gap-3">
                <div className="min-w-0 flex-1">
                  <span className="inline-block px-2.5 py-0.5 rounded-full bg-surface-sand text-secondary text-[11px] font-semibold mb-1 truncate max-w-full">
                    {scheme.category}
                  </span>
                  <h3 className="font-headline-sm text-base font-bold text-text-charcoal leading-snug">
                    {scheme.title}
                  </h3>
                </div>
                <span className="px-2.5 py-1 rounded-xl bg-emerald-100 text-emerald-800 text-xs font-bold whitespace-nowrap flex-shrink-0">
                  {scheme.benefitAmount || t("common.eligible")}
                </span>
              </div>

              <p className="font-body-sm text-xs text-text-slate leading-relaxed">
                {scheme.shortDescription}
              </p>

              <div className="flex items-center justify-between gap-2 text-[11px] text-text-slate pt-1">
                <span className="flex items-center gap-1">
                  <span className="material-symbols-outlined text-[14px] text-primary-container">groups</span>
                  <span>{scheme.genderEligible}</span>
                </span>
                <span className="flex items-center gap-1 truncate max-w-[180px]">
                  <span className="material-symbols-outlined text-[14px] text-secondary">verified</span>
                  <span className="truncate">{scheme.officialSource}</span>
                </span>
              </div>

              <div className="flex items-center gap-2 pt-2 border-t border-border-warm-gray/30">
                <button
                  onClick={() => navigate(`/scheme/${scheme.id}`)}
                  className="flex-1 py-2.5 rounded-2xl bg-surface-sand text-text-charcoal font-label-sm text-xs font-semibold hover:bg-surface-dim active:scale-[0.98] transition-all flex items-center justify-center gap-1 min-h-[44px]"
                  type="button"
                >
                  <span>{t("schemes.viewDetails")}</span>
                </button>

                <button
                  onClick={() => navigate(`/scheme/${scheme.id}`)}
                  className="flex-1 py-2.5 rounded-2xl bg-primary-container text-on-primary font-label-sm text-xs font-semibold hover:bg-primary active:scale-[0.98] transition-all flex items-center justify-center gap-1 shadow-sm min-h-[44px]"
                  type="button"
                >
                  <span>{t("schemes.checkEligibilityBtn")}</span>
                </button>
              </div>
            </div>
          ))}

          {/* Load More Button */}
          {visibleCount < filteredSchemes.length && (
            <button
              onClick={() => setVisibleCount(prev => prev + 20)}
              className="w-full py-3.5 rounded-full bg-surface-warm-white text-primary-container font-label-md text-sm font-semibold border border-primary-container/30 hover:bg-surface-sand transition-colors shadow-sm min-h-[48px] my-2"
              type="button"
            >
              {t("common.explore")} ({filteredSchemes.length - visibleCount} {t("common.more")})
            </button>
          )}

          {filteredSchemes.length === 0 && (
            <div className="text-center py-12 px-4 bg-surface-warm-white rounded-3xl border border-border-warm-gray/40">
              <span className="material-symbols-outlined text-[48px] text-text-slate mb-2">search_off</span>
              <p className="font-headline-sm text-base font-bold text-text-charcoal">
                {t("search.noResults")}
              </p>
            </div>
          )}
        </section>

      </main>

      <BottomNav />
    </div>
  );
};

export default SchemesDiscoveryFiltersPage;

