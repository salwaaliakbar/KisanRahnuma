import { useEffect, useState } from "react";

import { getContent, saveContent } from "../../api/adminClient";
import { errorMessage } from "../../api/client";
import { AlertIcon, CheckIcon } from "../../components/icons";

const FILES = [
  { filename: "credit_info.json", label: "Credit programs" },
  { filename: "certifications.json", label: "Certifications" },
  { filename: "knowledge_base.json", label: "Knowledge base (Ask Anything)" },
];

/** A raw, pretty-printed JSON editor for the content files that change rarely enough
 * not to need their own bespoke form (unlike crop prices, see AdminCropPricesPage). */
export default function AdminContentPage() {
  const [filename, setFilename] = useState(FILES[0].filename);
  const [text, setText] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [savedAt, setSavedAt] = useState<Date | null>(null);

  useEffect(() => {
    setError(null);
    setSavedAt(null);
    getContent(filename)
      .then((data) => setText(JSON.stringify(data, null, 2)))
      .catch((err) => setError(errorMessage(err)));
  }, [filename]);

  async function handleSave() {
    let parsed: unknown;
    try {
      parsed = JSON.parse(text);
    } catch {
      setError("That isn't valid JSON - check for a missing comma or bracket.");
      return;
    }
    setSaving(true);
    setError(null);
    try {
      const saved = await saveContent(filename, parsed);
      setText(JSON.stringify(saved, null, 2));
      setSavedAt(new Date());
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-lg font-semibold">Content</h1>
          <p className="text-sm text-ink-3">Edit the raw content file, then save. Changes apply immediately.</p>
        </div>
        <div className="flex items-center gap-3">
          {savedAt && (
            <span className="flex items-center gap-1.5 text-sm text-brand-700">
              <CheckIcon width={16} height={16} /> Saved {savedAt.toLocaleTimeString()}
            </span>
          )}
          <button
            type="button"
            onClick={handleSave}
            disabled={saving}
            className="rounded-xl bg-brand-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-brand-700 disabled:opacity-50"
          >
            {saving ? "Saving…" : "Save changes"}
          </button>
        </div>
      </div>

      <div className="flex gap-1">
        {FILES.map((f) => (
          <button
            key={f.filename}
            type="button"
            onClick={() => setFilename(f.filename)}
            className={`rounded-lg px-3 py-1.5 text-sm font-medium transition-colors ${
              filename === f.filename ? "bg-brand-50 text-brand-700" : "text-ink-2 hover:bg-canvas"
            }`}
          >
            {f.label}
          </button>
        ))}
      </div>

      {error && (
        <div className="flex items-center gap-2 rounded-xl border border-line bg-surface p-3 text-sm text-negative">
          <AlertIcon width={16} height={16} /> {error}
        </div>
      )}

      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        spellCheck={false}
        dir="ltr"
        className="h-[60vh] w-full rounded-2xl border border-line bg-surface p-4 font-mono text-xs leading-relaxed outline-none focus:border-brand-300"
      />
    </div>
  );
}
