import { useEffect, useState } from "react";
import { Link, NavLink, Outlet, useLocation } from "react-router-dom";

import { SITE } from "../../content/site";
import { CloseIcon, LeafIcon, MailIcon, MenuIcon, PinIcon } from "../icons";
import WhatsAppButton, { FloatingWhatsApp } from "./WhatsAppButton";

export const SITE_NAV = [
  { to: "/", label: "Home" },
  { to: "/about", label: "About" },
  { to: "/services", label: "Services" },
  { to: "/timeline", label: "Timeline" },
  { to: "/team", label: "Team" },
  { to: "/contact", label: "Contact" },
];

export function Logo({ light = false }: { light?: boolean }) {
  return (
    <Link to="/" className="flex items-center gap-2.5" aria-label="KisanRahnuma home">
      <span className="grid h-9 w-9 place-items-center rounded-xl bg-brand-600 text-white">
        <LeafIcon width={20} height={20} />
      </span>
      <span className={`font-display text-xl font-semibold ${light ? "text-white" : "text-brand-900"}`}>
        Kisan<span className={light ? "text-wheat-300" : "text-wheat-700"}>Rahnuma</span>
      </span>
    </Link>
  );
}

export default function SiteLayout() {
  const [open, setOpen] = useState(false);
  const { pathname } = useLocation();

  // New page: close the mobile menu and start at the top.
  useEffect(() => {
    setOpen(false);
    window.scrollTo(0, 0);
  }, [pathname]);

  const linkCls = ({ isActive }: { isActive: boolean }) =>
    `rounded-full px-3.5 py-2 text-sm font-medium transition-colors ${
      isActive ? "bg-brand-50 text-brand-700" : "text-ink-2 hover:text-brand-700"
    }`;

  return (
    <div className="min-h-dvh bg-soil">
      <header className="sticky top-0 z-20 border-b border-line/70 bg-soil/90 backdrop-blur">
        <div className="mx-auto flex h-16 max-w-6xl items-center gap-4 px-4 sm:px-6">
          <Logo />
          <nav className="ml-auto hidden items-center gap-1 lg:flex" aria-label="Main">
            {SITE_NAV.map((n) => (
              <NavLink key={n.to} to={n.to} end className={linkCls}>
                {n.label}
              </NavLink>
            ))}
          </nav>
          <WhatsAppButton label="WhatsApp" className="ml-auto hidden sm:inline-flex lg:ml-2" />
          <button
            type="button"
            className="ml-auto grid h-10 w-10 place-items-center rounded-lg text-ink-2 hover:bg-brand-50 sm:ml-0 lg:hidden"
            aria-label={open ? "Close menu" : "Open menu"}
            aria-expanded={open}
            onClick={() => setOpen((o) => !o)}
          >
            {open ? <CloseIcon /> : <MenuIcon />}
          </button>
        </div>
        {open && (
          <nav className="border-t border-line/70 px-4 pb-4 pt-2 lg:hidden" aria-label="Mobile">
            <div className="flex flex-col">
              {SITE_NAV.map((n) => (
                <NavLink key={n.to} to={n.to} end className={linkCls}>
                  {n.label}
                </NavLink>
              ))}
            </div>
            <WhatsAppButton className="mt-3 w-full sm:hidden" />
          </nav>
        )}
      </header>

      <main>
        <Outlet />
      </main>

      <Footer />
      <FloatingWhatsApp />
    </div>
  );
}

function Footer() {
  return (
    <footer className="bg-brand-950 text-brand-100">
      <div className="mx-auto grid max-w-6xl gap-10 px-4 py-14 sm:px-6 md:grid-cols-[1.4fr_1fr_1fr]">
        <div>
          <Logo light />
          <p className="mt-4 max-w-sm text-sm leading-relaxed text-brand-200">
            A free WhatsApp assistant helping farmers in Sindh grow more, earn fairly and adapt to a changing
            climate.
          </p>
          <p className="mt-4 text-sm text-brand-300" dir="auto">
            {SITE.languages.join(" · ")}
          </p>
        </div>
        <div>
          <h2 className="text-sm font-semibold uppercase tracking-wider text-wheat-300">Explore</h2>
          <ul className="mt-4 space-y-2 text-sm">
            {SITE_NAV.slice(1).map((n) => (
              <li key={n.to}>
                <Link to={n.to} className="text-brand-100 hover:text-white">
                  {n.label}
                </Link>
              </li>
            ))}
            <li>
              <Link to="/chat" className="text-brand-100 hover:text-white">
                Web chat demo
              </Link>
            </li>
          </ul>
        </div>
        <div>
          <h2 className="text-sm font-semibold uppercase tracking-wider text-wheat-300">Contact</h2>
          <ul className="mt-4 space-y-3 text-sm">
            <li className="flex items-start gap-2">
              <MailIcon width={18} height={18} className="mt-0.5 shrink-0 text-brand-300" />
              <a href={`mailto:${SITE.email}`} className="hover:text-white">
                {SITE.email}
              </a>
            </li>
            <li className="flex items-start gap-2">
              <PinIcon width={18} height={18} className="mt-0.5 shrink-0 text-brand-300" />
              {SITE.location}
            </li>
          </ul>
          <WhatsAppButton className="mt-5" />
        </div>
      </div>
      <div className="border-t border-white/10">
        <div className="mx-auto flex max-w-6xl flex-wrap justify-between gap-2 px-4 py-5 text-xs text-brand-300 sm:px-6">
          <span>© {new Date().getFullYear()} KisanRahnuma. Project period: October 2026 to February 2027.</span>
        </div>
      </div>
    </footer>
  );
}
