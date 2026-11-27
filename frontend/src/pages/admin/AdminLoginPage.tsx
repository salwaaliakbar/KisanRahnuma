import { useState, type FormEvent } from "react";
import { Navigate, useNavigate } from "react-router-dom";

import { adminLogin } from "../../api/adminClient";
import { errorMessage } from "../../api/client";
import { LeafIcon } from "../../components/icons";
import { getAdminToken, setAdminToken } from "../../lib/adminAuth";

export default function AdminLoginPage() {
  const navigate = useNavigate();
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  if (getAdminToken()) return <Navigate to="/admin" replace />;

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const { token } = await adminLogin(password);
      setAdminToken(token);
      navigate("/admin", { replace: true });
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="grid min-h-dvh place-items-center px-4">
      <form onSubmit={handleSubmit} className="w-full max-w-sm rounded-2xl border border-line bg-surface p-6 shadow-sm">
        <div className="mb-4 flex items-center gap-2.5">
          <span className="grid h-8 w-8 place-items-center rounded-lg bg-brand-600 text-white">
            <LeafIcon width={18} height={18} />
          </span>
          <span className="font-semibold tracking-tight">KisanRahnuma Admin</span>
        </div>
        <label className="block text-sm font-medium text-ink-2">
          Admin password
          <input
            type="password"
            autoFocus
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="mt-1.5 w-full rounded-xl border border-line bg-canvas px-3 py-2 text-sm outline-none focus:border-brand-300"
          />
        </label>
        {error && <p className="mt-3 text-sm text-negative">{error}</p>}
        <button
          type="submit"
          disabled={loading || !password}
          className="mt-4 w-full rounded-xl bg-brand-600 px-3 py-2 text-sm font-medium text-white transition-colors hover:bg-brand-700 disabled:opacity-50"
        >
          {loading ? "Logging in…" : "Log in"}
        </button>
      </form>
    </div>
  );
}
