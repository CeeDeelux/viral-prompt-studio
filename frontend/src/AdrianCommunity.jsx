import React from 'react'

const COMMUNITY_URL = 'https://www.skool.com/adrian/about?ref=297517c89ef84acd9c347c22c501d262'

export default function AdrianCommunity({ tr }) {
  return (
    <section aria-labelledby="adrian-community-title" className="mt-8 overflow-hidden rounded-2xl border border-purple-400/20 bg-gradient-to-br from-purple-950/90 via-gray-900/95 to-fuchsia-950/70 shadow-lg transition duration-300 hover:border-purple-300/40 hover:shadow-purple-950/40 motion-reduce:transition-none">
      <div className="flex flex-col items-center gap-6 p-6 text-center sm:flex-row sm:items-start sm:p-8 sm:text-left">
        <img
          src="/assets/adrian-avatar.webp"
          alt="Adrian — Viral AI Marketing"
          width="128"
          height="128"
          loading="lazy"
          decoding="async"
          className="h-24 w-24 shrink-0 rounded-full object-cover ring-4 ring-purple-300/15 sm:h-28 sm:w-28"
        />
        <div className="min-w-0 flex-1">
          <p className="mb-2 text-xs font-semibold uppercase tracking-widest text-purple-300">Adrian Viral AI Marketing</p>
          <h2 id="adrian-community-title" className="text-xl font-semibold leading-snug text-white sm:text-2xl">
            {tr('Want to Turn Viral Scripts Into Amazing AI Videos?')}
          </h2>
          <p className="mt-3 max-w-2xl text-sm leading-relaxed text-purple-100/80 sm:text-base">
            {tr('Learn AI video creation, prompting, and marketing workflows with Adrian Viral AI Marketing.')}
          </p>
          <a
            href={COMMUNITY_URL}
            target="_blank"
            rel="sponsored noopener noreferrer"
            referrerPolicy="no-referrer"
            aria-describedby="adrian-affiliate-disclosure"
            className="mt-5 inline-flex min-h-12 w-full items-center justify-center gap-2 rounded-xl border border-purple-300/20 bg-gradient-to-r from-purple-600 to-fuchsia-600 px-5 py-3 text-sm font-semibold leading-snug text-white shadow-md transition hover:from-purple-500 hover:to-fuchsia-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-purple-200 focus-visible:ring-offset-4 focus-visible:ring-offset-gray-900 motion-reduce:transition-none sm:w-auto"
          >
            <span>{tr("Explore Adrian's AI Marketing Community")}</span>
            <svg aria-hidden="true" className="h-4 w-4 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
              <path strokeLinecap="round" strokeLinejoin="round" d="M7 17 17 7M7 7h10v10" />
            </svg>
          </a>
          <p id="adrian-affiliate-disclosure" className="mt-3 text-xs leading-relaxed text-purple-200/75">
            {tr('Affiliate link — we may earn a commission if you join.')}
          </p>
        </div>
      </div>
    </section>
  )
}
