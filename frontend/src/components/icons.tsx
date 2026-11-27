import type { SVGProps } from "react";

const base = {
  width: 20,
  height: 20,
  viewBox: "0 0 24 24",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 1.8,
  strokeLinecap: "round" as const,
  strokeLinejoin: "round" as const,
  "aria-hidden": true,
};

type P = SVGProps<SVGSVGElement>;

export const LeafIcon = (p: P) => (
  <svg {...base} {...p}><path d="M5 19c0-8 5-14 15-14 0 10-6 15-14 15" /><path d="M5 19c3-4 6-6 10-8" /></svg>
);
export const ChatIcon = (p: P) => (
  <svg {...base} {...p}><path d="M4 5h16v11H8l-4 4z" /></svg>
);
export const ChartIcon = (p: P) => (
  <svg {...base} {...p}><path d="M4 20V10M10 20V4M16 20v-7M22 20H2" /></svg>
);
export const SendIcon = (p: P) => (
  <svg {...base} {...p}><path d="M4 12l16-8-6 16-2.5-6.5z" /></svg>
);
export const MicIcon = (p: P) => (
  <svg {...base} {...p}><rect x="9" y="3" width="6" height="11" rx="3" /><path d="M5 11a7 7 0 0014 0M12 18v3" /></svg>
);
export const HomeIcon = (p: P) => (
  <svg {...base} {...p}><path d="M4 11l8-7 8 7v9h-5v-6H9v6H4z" /></svg>
);
export const ThumbUpIcon = (p: P) => (
  <svg {...base} {...p}><path d="M7 11v9H4v-9zM7 11l4-7c1.5 0 2.5 1 2 3l-1 3h6a2 2 0 012 2.3l-1.2 6A2 2 0 0115.8 20H7" /></svg>
);
export const ThumbDownIcon = (p: P) => (
  <svg {...base} {...p}><path d="M17 13V4h3v9zM17 13l-4 7c-1.5 0-2.5-1-2-3l1-3H6a2 2 0 01-2-2.3l1.2-6A2 2 0 017.2 4H17" /></svg>
);
export const RefreshIcon = (p: P) => (
  <svg {...base} {...p}><path d="M20 11a8 8 0 10-2.3 5.7M20 4v7h-7" /></svg>
);
export const UserPlusIcon = (p: P) => (
  <svg {...base} {...p}><circle cx="10" cy="8" r="4" /><path d="M3 20c1-4 4-6 7-6s6 2 7 6M19 8v6M16 11h6" /></svg>
);
export const AlertIcon = (p: P) => (
  <svg {...base} {...p}><circle cx="12" cy="12" r="9" /><path d="M12 7v6M12 16.5v.5" /></svg>
);

/* Website icons */
export const SunCloudIcon = (p: P) => (
  <svg {...base} {...p}><circle cx="9" cy="8" r="3" /><path d="M9 2v1.5M3 8h1.5M4.8 3.8l1 1M13.2 3.8l-1 1" /><path d="M8 20h9a4 4 0 000-8 5 5 0 00-9.6 1.5A3.3 3.3 0 008 20z" /></svg>
);
export const PriceIcon = (p: P) => (
  <svg {...base} {...p}><path d="M3 17l5-5 4 4 8-8" /><path d="M15 8h5v5" /></svg>
);
export const CoinsIcon = (p: P) => (
  <svg {...base} {...p}><ellipse cx="9" cy="7" rx="6" ry="3" /><path d="M3 7v4c0 1.7 2.7 3 6 3s6-1.3 6-3V7" /><path d="M9 14v3c0 1.7 2.7 3 6 3s6-1.3 6-3v-4c0-1.6-2.4-2.9-5.5-3" /></svg>
);
export const BadgeIcon = (p: P) => (
  <svg {...base} {...p}><circle cx="12" cy="9" r="6" /><path d="M9.5 9l1.8 1.8L14.8 7.3M8.5 14.2L7 22l5-3 5 3-1.5-7.8" /></svg>
);
export const QuestionIcon = (p: P) => (
  <svg {...base} {...p}><circle cx="12" cy="12" r="9" /><path d="M9.5 9.3a2.6 2.6 0 015 .9c0 1.8-2.5 2.2-2.5 3.8M12 17v.3" /></svg>
);
export const MenuIcon = (p: P) => (
  <svg {...base} {...p}><path d="M4 7h16M4 12h16M4 17h16" /></svg>
);
export const CloseIcon = (p: P) => (
  <svg {...base} {...p}><path d="M6 6l12 12M18 6L6 18" /></svg>
);
export const ArrowRightIcon = (p: P) => (
  <svg {...base} {...p}><path d="M5 12h14M13 6l6 6-6 6" /></svg>
);
export const ShieldIcon = (p: P) => (
  <svg {...base} {...p}><path d="M12 3l8 3v6c0 4.5-3.4 8-8 9-4.6-1-8-4.5-8-9V6z" /><path d="M9 12l2 2 4-4" /></svg>
);
export const GlobeIcon = (p: P) => (
  <svg {...base} {...p}><circle cx="12" cy="12" r="9" /><path d="M3 12h18M12 3c2.5 2.7 3.8 5.7 3.8 9s-1.3 6.3-3.8 9c-2.5-2.7-3.8-5.7-3.8-9S9.5 5.7 12 3z" /></svg>
);
export const DropletIcon = (p: P) => (
  <svg {...base} {...p}><path d="M12 3s7 7.3 7 12a7 7 0 01-14 0c0-4.7 7-12 7-12z" /></svg>
);
export const MailIcon = (p: P) => (
  <svg {...base} {...p}><rect x="3" y="5" width="18" height="14" rx="2" /><path d="M3 7l9 6 9-6" /></svg>
);
export const PinIcon = (p: P) => (
  <svg {...base} {...p}><path d="M12 21s7-6.2 7-12a7 7 0 00-14 0c0 5.8 7 12 7 12z" /><circle cx="12" cy="9" r="2.5" /></svg>
);
export const CheckIcon = (p: P) => (
  <svg {...base} {...p}><path d="M5 12.5l4.5 4.5L19 7.5" /></svg>
);
export const WhatsAppIcon = (p: P) => (
  <svg width={20} height={20} viewBox="0 0 24 24" fill="currentColor" aria-hidden {...p}>
    <path d="M12.04 2C6.58 2 2.13 6.45 2.13 11.91c0 1.75.46 3.45 1.32 4.95L2.05 22l5.25-1.38a9.9 9.9 0 004.74 1.21h.01c5.46 0 9.91-4.45 9.91-9.91 0-2.65-1.03-5.14-2.9-7.01A9.82 9.82 0 0012.04 2zm0 18.15h-.01a8.23 8.23 0 01-4.19-1.15l-.3-.18-3.12.82.83-3.04-.2-.31a8.2 8.2 0 01-1.26-4.38c0-4.54 3.7-8.24 8.25-8.24 2.2 0 4.27.86 5.83 2.42a8.18 8.18 0 012.41 5.83c0 4.54-3.7 8.23-8.24 8.23zm4.52-6.16c-.25-.12-1.47-.72-1.69-.81-.23-.08-.39-.12-.56.13-.16.25-.64.81-.79.97-.14.17-.29.19-.54.06-.25-.12-1.05-.39-1.99-1.23-.74-.66-1.23-1.47-1.38-1.72-.14-.25-.02-.38.11-.51.11-.11.25-.29.37-.43.13-.15.17-.25.25-.42.08-.17.04-.31-.02-.43-.06-.13-.56-1.34-.76-1.84-.2-.48-.41-.42-.56-.43h-.48c-.17 0-.43.06-.66.31-.22.25-.86.85-.86 2.07 0 1.22.89 2.4 1.01 2.56.12.17 1.75 2.67 4.23 3.74.59.26 1.05.41 1.41.52.59.19 1.13.16 1.56.1.48-.07 1.47-.6 1.67-1.18.21-.58.21-1.07.14-1.18-.06-.1-.22-.16-.47-.28z" />
  </svg>
);
