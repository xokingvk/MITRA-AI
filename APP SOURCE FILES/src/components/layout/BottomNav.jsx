import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useApp } from '../../context/AppContext';

export const BottomNav = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { t } = useApp();
  const currentPath = location.pathname;

  const navItems = [
    { label: t("nav.home"), icon: "home", path: "/" },
    { label: t("nav.schemes"), icon: "grid_view", path: "/schemes" },
    { label: t("nav.settings"), icon: "settings", path: "/settings" }
  ];

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 bg-surface-warm-white/95 backdrop-blur-xl border-t border-border-warm-gray/40 pb-safe shadow-[0_-2px_12px_rgba(73,53,72,0.08)]">
      <div className="max-w-md mx-auto h-16 px-gutter flex items-center justify-around">
        {navItems.map((item) => {
          const isActive = currentPath === item.path || 
            (item.path !== '/' && currentPath.startsWith(item.path));
          
          return (
            <button
              key={item.path}
              onClick={() => navigate(item.path)}
              aria-label={item.label}
              className={`flex flex-col items-center justify-center gap-0.5 flex-1 min-h-[48px] rounded-xl transition-all ${
                isActive 
                  ? 'text-primary-container font-semibold' 
                  : 'text-text-slate hover:text-text-charcoal active:scale-95'
              }`}
              type="button"
            >
              <div className={`w-10 h-7 flex items-center justify-center rounded-full transition-all ${
                isActive ? 'bg-primary-container/10' : ''
              }`}>
                <span className={`material-symbols-outlined text-[22px] ${
                  isActive ? 'material-symbols-fill text-primary-container' : ''
                }`}>
                  {item.icon}
                </span>
              </div>
              <span className="font-label-sm text-[11px] leading-tight tracking-tight truncate max-w-[70px]">
                {item.label}
              </span>
            </button>
          );
        })}
      </div>
    </nav>
  );
};

export default BottomNav;
