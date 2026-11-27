import { Link, NavLink, Outlet } from "react-router-dom";

import { ChatIcon, LeafIcon } from "../icons";

const NAV = [
  { to: "/chat", label: "Chat simulator", icon: ChatIcon },
];

export default function AppShell() {
  return (
    <div className="min-h-dvh">
      <header className="sticky top-0 z-10 border-b border-line bg-surface/90 backdrop-blur">
        <div className="mx-auto flex h-16 max-w-7xl items-center gap-4 px-4 sm:px-6">
          <Link to="/" className="flex items-center gap-2.5" title="Back to the KisanRahnuma website">
            <span className="grid h-8 w-8 place-items-center rounded-lg bg-brand-600 text-white">
              <LeafIcon width={18} height={18} />
            </span>
            <span className="hidden font-semibold tracking-tight sm:inline">KisanRahnuma</span>
          </Link>

          <nav className="flex gap-1" aria-label="Main">
            {NAV.map(({ to, label, icon: Icon }) => (
              <NavLink
                key={to}
                to={to}
                end
                className={({ isActive }) =>
                  `inline-flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                    isActive ? "bg-brand-50 text-brand-700" : "text-ink-2 hover:bg-canvas hover:text-ink"
                  }`
                }
              >
                <Icon width={16} height={16} />
                {label}
              </NavLink>
            ))}
          </nav>

          <span className="ml-auto hidden rounded-full border border-line px-2.5 py-1 text-xs text-ink-3 md:inline">
            MVP · dummy data
          </span>
          <Link to="/" className="ml-auto text-sm font-medium text-ink-2 hover:text-brand-700 md:ml-0">
            ← Website
          </Link>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-4 py-5 sm:px-6">
        <Outlet />
      </main>
    </div>
  );
}
