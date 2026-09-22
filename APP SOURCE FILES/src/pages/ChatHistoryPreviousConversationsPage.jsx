import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Header from '../components/layout/Header';
import BottomNav from '../components/layout/BottomNav';
import { useApp } from '../context/AppContext';

export default function ChatHistoryPreviousConversationsPage() {
  const navigate = useNavigate();
  const { t, speakText, isPlayingAudio, stopAudio } = useApp();
  const [searchTerm, setSearchTerm] = useState('');

  const chats = [
    {
      id: 1,
      title: t("chat.farmerTopic"),
      date: `Today • 6 ${t("nav.chats")}`,
      desc: t("chat.farmerDesc"),
      status: `${t("common.verified")} ✓`,
      audioText: t("chat.farmerDesc")
    },
    {
      id: 2,
      title: t("chat.ekycTopic"),
      date: `Yesterday • 4 ${t("nav.chats")}`,
      desc: t("chat.ekycDesc"),
      status: `${t("common.eligible")} ✓`,
      audioText: t("chat.ekycDesc")
    },
    {
      id: 3,
      title: t("chat.kmutTopic"),
      date: `12 Apr 2025 • 3 ${t("nav.chats")}`,
      desc: t("chat.kmutDesc"),
      status: t("common.credited"),
      audioText: t("chat.kmutDesc")
    }
  ];

  const filteredChats = chats.filter(c => 
    !searchTerm || c.title.toLowerCase().includes(searchTerm.toLowerCase()) || c.desc.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="bg-surface-sand text-text-charcoal font-body-md min-h-screen flex flex-col">
      <Header title={t("chat.historyTitle")} />

      <main className="flex-1 w-full max-w-md mx-auto px-4 pt-20 pb-28 flex flex-col gap-4">
        
        {/* Header Title & New Chat Action */}
        <div className="flex items-center justify-between pt-1">
          <h1 className="font-headline-sm text-xl font-bold text-text-charcoal">
            {t("chat.historyTitle")}
          </h1>
          <button
            onClick={() => navigate('/')}
            className="px-3.5 py-2 rounded-full bg-primary-container text-on-primary font-label-sm text-xs font-semibold hover:bg-primary active:scale-95 transition-all flex items-center gap-1.5 shadow-sm min-h-[40px]"
            type="button"
          >
            <span className="material-symbols-outlined text-[18px]">add</span>
            <span>{t("chat.newChat")}</span>
          </button>
        </div>

        {/* Search Bar */}
        <div className="w-full bg-surface-warm-white rounded-2xl p-2 border border-border-warm-gray/50 shadow-sm flex items-center gap-2">
          <span className="material-symbols-outlined text-text-slate ml-2 text-[20px]">search</span>
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder={t("schemes.searchPlaceholder")}
            className="flex-1 min-w-0 bg-transparent text-text-charcoal font-body-md text-sm placeholder:text-text-slate focus:outline-none py-1"
          />
        </div>

        {/* Conversation Cards List */}
        <div className="flex flex-col gap-3">
          {filteredChats.map((chat) => (
            <div
              key={chat.id}
              className="w-full bg-surface-warm-white rounded-3xl p-5 shadow-sm border border-border-warm-gray/40 flex flex-col gap-3 hover:shadow-md transition-all cursor-pointer"
              onClick={() => navigate('/scheme/pm-kisan/check')}
            >
              <div className="flex items-start justify-between gap-3">
                <div className="min-w-0 flex-1">
                  <span className="font-label-sm text-[11px] text-text-slate block mb-0.5">
                    {chat.date}
                  </span>
                  <h3 className="font-headline-sm text-base font-bold text-text-charcoal leading-snug">
                    {chat.title}
                  </h3>
                </div>
                <span className="px-2.5 py-1 rounded-full bg-emerald-100 text-emerald-800 text-[11px] font-bold whitespace-nowrap flex-shrink-0">
                  {chat.status}
                </span>
              </div>

              <p className="font-body-sm text-xs text-text-slate leading-relaxed">
                {chat.desc}
              </p>

              <div className="flex items-center justify-between pt-2 border-t border-border-warm-gray/30">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    if (isPlayingAudio) {
                      stopAudio();
                    } else {
                      speakText(chat.audioText);
                    }
                  }}
                  className="px-3 py-1.5 rounded-full bg-surface-sand text-secondary font-label-sm text-xs font-semibold hover:bg-surface-dim transition-colors flex items-center gap-1.5 min-h-[36px]"
                  type="button"
                >
                  <span className="material-symbols-outlined text-[18px]">
                    {isPlayingAudio ? 'stop' : 'volume_up'}
                  </span>
                  <span>{t("common.listen")}</span>
                </button>

                <div className="flex items-center gap-1 text-primary-container font-label-sm text-xs font-semibold">
                  <span>{t("common.continue")}</span>
                  <span className="material-symbols-outlined text-[18px]">chevron_right</span>
                </div>
              </div>
            </div>
          ))}

          {filteredChats.length === 0 && (
            <div className="text-center py-10 text-text-slate font-body-md text-sm">
              {t("chat.noHistory")}
            </div>
          )}
        </div>

      </main>

      <BottomNav />
    </div>
  );
}
