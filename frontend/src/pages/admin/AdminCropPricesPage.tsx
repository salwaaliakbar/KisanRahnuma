import { useEffect, useState } from "react";

import { getContent, saveContent } from "../../api/adminClient";
import { errorMessage } from "../../api/client";
import { AlertIcon, CheckIcon } from "../../components/icons";

interface LocalizedText {
  en: string;
  ur: string;
  sd: string;
}

interface CropRate {
  rate: number;
  source: LocalizedText;
  date: string;
}

interface CropEntry {
  id: string;
  name: LocalizedText;
  unit: LocalizedText;
  rates: Record<string, CropRate>;
  [key: string]: unknown; // trend, expected: shown elsewhere, preserved as-is on save
}

interface District {
  id: string;
  name: LocalizedText;
}

interface CropRatesContent {
  districts: District[];
  crops: CropEntry[];
  [key: string]: unknown;
}

const FILENAME = "crop_rates.json";

/** The daily price-update screen: a rate/source/date grid over crop_rates.json. */
export default function AdminCropPricesPage() {
  const [content, setContent] = useState<CropRatesContent | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [savedAt, setSavedAt] = useState<Date | null>(null);

  useEffect(() => {
    getContent(FILENAME)
      .then((data) => setContent(data as CropRatesContent))
      .catch((err) => setError(errorMessage(err)));
  }, []);

  function updateRate(cropIndex: number, districtId: string, patch: Partial<CropRate>) {
    setContent((prev) => {
      if (!prev) return prev;
      const crops = prev.crops.map((crop, i) => {
        if (i !== cropIndex) return crop;
        return { ...crop, rates: { ...crop.rates, [districtId]: { ...crop.rates[districtId], ...patch } } };
      });
      return { ...prev, crops };
    });
    setSavedAt(null);
  }

  async function handleSave() {
    if (!content) return;
    setSaving(true);
    setError(null);
    try {
      const saved = await saveContent(FILENAME, content);
      setContent(saved as CropRatesContent);
      setSavedAt(new Date());
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setSaving(false);
    }
  }

  if (error && !content) {
    return (
      <div className="flex items-center gap-2 rounded-xl border border-line bg-surface p-4 text-sm text-negative">
        <AlertIcon width={16} height={16} /> {error}
      </div>
    );
  }
  if (!content) return <p className="text-sm text-ink-3">Loading…</p>;

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-lg font-semibold">Crop Prices</h1>
          <p className="text-sm text-ink-3">Update today's rate, source and date for each crop and district.</p>
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

      {error && (
        <div className="flex items-center gap-2 rounded-xl border border-line bg-surface p-3 text-sm text-negative">
          <AlertIcon width={16} height={16} /> {error}
        </div>
      )}

      <div className="space-y-4">
        {content.crops.map((crop, cropIndex) => (
          <div key={crop.id} className="rounded-2xl border border-line bg-surface p-4">
            <h2 className="text-sm font-semibold">
              {crop.name.en} <span className="font-normal text-ink-3">· {crop.unit.en}</span>
            </h2>
            <div className="mt-3 overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead className="text-xs uppercase tracking-wide text-ink-3">
                  <tr>
                    <th className="py-1.5 pr-3 font-medium">District</th>
                    <th className="py-1.5 pr-3 font-medium">Rate</th>
                    <th className="py-1.5 pr-3 font-medium">Source (English)</th>
                    <th className="py-1.5 pr-3 font-medium">Date</th>
                  </tr>
                </thead>
                <tbody>
                  {content.districts.map((district) => {
                    const rate = crop.rates[district.id];
                    if (!rate) return null;
                    return (
                      <tr key={district.id} className="border-t border-line">
                        <td className="py-2 pr-3 text-ink-2">{district.name.en}</td>
                        <td className="py-2 pr-3">
                          <input
                            type="number"
                            value={rate.rate}
                            onChange={(e) => {
                              const value = Number(e.target.value);
                              if (!Number.isNaN(value)) updateRate(cropIndex, district.id, { rate: value });
                            }}
                            className="w-28 rounded-lg border border-line bg-canvas px-2 py-1 outline-none focus:border-brand-300"
                          />
                        </td>
                        <td className="py-2 pr-3">
                          <input
                            type="text"
                            value={rate.source.en}
                            onChange={(e) =>
                              updateRate(cropIndex, district.id, { source: { ...rate.source, en: e.target.value } })
                            }
                            className="w-64 rounded-lg border border-line bg-canvas px-2 py-1 outline-none focus:border-brand-300"
                          />
                        </td>
                        <td className="py-2 pr-3">
                          <input
                            type="date"
                            value={rate.date}
                            onChange={(e) => updateRate(cropIndex, district.id, { date: e.target.value })}
                            className="rounded-lg border border-line bg-canvas px-2 py-1 outline-none focus:border-brand-300"
                          />
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
