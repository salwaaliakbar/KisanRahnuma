import { Link, Navigate, NavLink, Outlet, useNavigate } from "react-router-dom";

import { clearAdminToken, getAdminToken } from "../../lib/adminAuth";
import { ChartIcon, CoinsIcon, LeafIcon, UserPlusIcon } from "../icons";

const NAV = [
  { to: "/admin", label: "Overview", icon: ChartIcon },
  { to: "/admin/farmers", label: "Farmers", icon: UserPlusIcon },
  { to: "/admin/crop-prices", label: "Crop Prices", icon: CoinsIcon },
  { to: "/admin/content", label: "Content", icon: LeafIcon },
];

/** Gates every /admin/* page except /admin/login behind a logged-in admin token. */
export default function AdminShell() {
  const navigate = useNavigate();
  if (!getAdminToken()) return <Navigate to="/admin/login" replace />;

  function logout() {
    clearAdminToken();
    navigate("/admin/login", { replace: true });
  }

  return (
    <div className="min-h-dvh">
      <header className="sticky top-0 z-10 border-b border-line bg-surface/90 backdrop-blur">
        <div className="mx-auto flex h-16 max-w-7xl items-center gap-4 px-4 sm:px-6">
          <Link to="/admin" className="flex items-center gap-2.5">
            <span className="grid h-8 w-8 place-items-center rounded-lg bg-brand-600 text-white">
              <LeafIcon width={18} height={18} />
            </span>
            <span className="hidden font-semibold tracking-tight sm:inline">KisanRahnuma Admin</span>
          </Link>

          <nav className="flex gap-1" aria-label="Admin">
            {NAV.map(({ to, label, icon: Icon }) => (
              <NavLink
                key={to}
                to={to}
                end={to === "/admin"}
                className={({ isActive }) =>
                  `inline-flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                    isActive ? "bg-brand-50 text-brand-700" : "text-ink-2 hover:bg-canvas hover:text-ink"
                  }`
                }
              >
                <Icon width={16} height={16} />
                <span className="hidden sm:inline">{label}</span>
              </NavLink>
            ))}
          </nav>

          <button type="button" onClick={logout} className="ml-auto text-sm font-medium text-ink-2 hover:text-brand-700">
            Log out
          </button>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-4 py-5 sm:px-6">
        <Outlet />
      </main>
    </div>
  );
}
