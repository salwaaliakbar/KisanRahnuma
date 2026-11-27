// Farmer-facing chat UI strings. Bot replies are translated by the backend; these cover only
// the simulator chrome around them (header, composer, feedback bar). Staff-facing screens
// (test panel) stay in English.

export type Language = "en" | "ur" | "sd";

export const LANGUAGES: { code: Language; name: string; dir: "ltr" | "rtl" }[] = [
  { code: "en", name: "English", dir: "ltr" },
  { code: "ur", name: "اردو", dir: "rtl" },
  { code: "sd", name: "سنڌي", dir: "rtl" },
];

export function isLanguage(value: unknown): value is Language {
  return LANGUAGES.some((l) => l.code === value);
}

export function languageInfo(code: Language) {
  return LANGUAGES.find((l) => l.code === code) ?? LANGUAGES[0];
}

const UI = {
  en: {
    online: "Online · replies in English",
    typing: "typing…",
    home: "Home",
    retry: "Retry",
    startTitle: "Start a conversation",
    startBody: "Simulate a farmer messaging the assistant. A new farmer chooses a language, then answers two consent questions.",
    greeting: "Hi",
    placeholder: "Type a message or a farming question…",
    voiceTitle: "Send a mock voice note (speech-to-text comes later)",
    voiceNote: "Voice note",
    helpfulQ: "Was this helpful?",
    helpfulYes: "Yes, helpful",
    helpfulNo: "Not helpful",
    thanksYes: "Thanks for your feedback. Glad it helped!",
    thanksNo: "Thanks for your feedback. We'll use it to improve.",
    feedbackError: "Couldn't save. Try again.",
    language: "Language",
  },
  ur: {
    online: "آن لائن · جوابات اردو میں",
    typing: "لکھ رہا ہے…",
    home: "مین مینو",
    retry: "دوبارہ کوشش کریں",
    startTitle: "بات چیت شروع کریں",
    startBody: "کسان کی طرح اسسٹنٹ کو پیغام بھیجیں۔ نیا کسان پہلے زبان منتخب کرتا ہے، پھر رضامندی کے دو سوالوں کے جواب دیتا ہے۔",
    greeting: "السلام علیکم",
    placeholder: "پیغام یا کھیتی باڑی کا سوال لکھیں…",
    voiceTitle: "فرضی وائس نوٹ بھیجیں",
    voiceNote: "وائس نوٹ",
    helpfulQ: "کیا یہ مفید تھا؟",
    helpfulYes: "ہاں، مفید",
    helpfulNo: "مفید نہیں",
    thanksYes: "آپ کی رائے کا شکریہ۔ خوشی ہوئی کہ مدد ملی!",
    thanksNo: "آپ کی رائے کا شکریہ۔ ہم اسے بہتری کے لیے استعمال کریں گے۔",
    feedbackError: "محفوظ نہیں ہو سکا۔ دوبارہ کوشش کریں۔",
    language: "زبان",
  },
  sd: {
    online: "آن لائن · جواب سنڌي ۾",
    typing: "لکي رهيو آهي…",
    home: "مک مينيو",
    retry: "ٻيهر ڪوشش ڪريو",
    startTitle: "ڳالهه ٻولهه شروع ڪريو",
    startBody: "هاري وانگر اسسٽنٽ کي پيغام موڪليو. نئون هاري پهرين ٻولي چونڊي ٿو، پوءِ رضامندي جي ٻن سوالن جا جواب ڏئي ٿو.",
    greeting: "السلام عليڪم",
    placeholder: "پيغام يا پوک بابت سوال لکو…",
    voiceTitle: "فرضي وائس نوٽ موڪليو",
    voiceNote: "وائس نوٽ",
    helpfulQ: "ڇا هي فائديمند هو؟",
    helpfulYes: "ها، فائديمند",
    helpfulNo: "فائديمند ناهي",
    thanksYes: "توهان جي راءِ جي مهرباني. خوشي ٿي ته مدد ملي!",
    thanksNo: "توهان جي راءِ جي مهرباني. اسان ان کي بهتري لاءِ استعمال ڪنداسين.",
    feedbackError: "محفوظ نه ٿي سگهيو. ٻيهر ڪوشش ڪريو.",
    language: "ٻولي",
  },
} satisfies Record<Language, Record<string, string>>;

export type UIStrings = (typeof UI)["en"];

export function uiStrings(lang: Language): UIStrings {
  return UI[lang];
}
