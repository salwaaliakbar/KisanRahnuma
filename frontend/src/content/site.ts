/**
 * All website copy in one place. Edit team members, timeline and services here;
 * the pages read from this file and need no changes.
 */

export const SITE = {
  name: "KisanRahnuma",
  tagline: "Farming advice in your pocket, in your language.",
  // Shown on the Contact page and in the footer. Replace with the project's real details.
  email: "hello@kisanrahnuma.org",
  location: "Sukkur, Sindh, Pakistan",
  districts: ["Sukkur", "Khairpur", "Ghotki"],
  languages: ["سنڌي", "اردو", "English"],
};

export type Service = {
  key: "weather" | "rates" | "credit" | "certifications" | "ask";
  title: string;
  summary: string;
  points: string[];
};

export const SERVICES: Service[] = [
  {
    key: "weather",
    title: "Weather & farm advice",
    summary: "A 3-day forecast for your district, with advice on when to irrigate, spray and harvest.",
    points: ["Rain, heat, frost and wind alerts", "Advice on when to irrigate and spray", "District-level forecasts"],
  },
  {
    key: "rates",
    title: "Crop rates",
    summary: "Current market rates for major crops in your local mandi, with the seasonal trend.",
    points: ["Cotton, wheat, rice, sugarcane and dates", "Summer and winter price trends", "Expected price range"],
  },
  {
    key: "credit",
    title: "Credit information",
    summary: "Plain-language guides to farm loans and support schemes, and how to apply.",
    points: ["Benazir Hari Card", "ZTBL and bank agri-loans", "Eligibility and documents needed"],
  },
  {
    key: "certifications",
    title: "Certifications",
    summary: "How to get organic, GAP and Better Cotton certification for better markets and prices.",
    points: ["Organic, GAP and Better Cotton", "Steps, costs and timelines", "Where to apply"],
  },
  {
    key: "ask",
    title: "Ask anything",
    summary: "Type any farming question in your own words and get an answer from vetted extension guides.",
    points: ["Sowing times and seed choice", "Pest and disease control", "Fertiliser and water use"],
  },
];

export const STEPS = [
  { title: "Say “Hi” on WhatsApp", text: "No app to install and no sign-up. Message the KisanRahnuma number." },
  { title: "Pick your language", text: "Sindhi, Urdu or English. You choose whether your usage is recorded anonymously." },
  { title: "Choose a service", text: "Tap a menu button, or simply type your question." },
  { title: "Get advice and tell us", text: "Every answer asks “Was this helpful?” so the service keeps getting better." },
];

export type Milestone = {
  /** First and last month of the phase, as YYYY-MM. Status (done / now / next) is worked out from today's date. */
  start: string;
  end: string;
  title: string;
  text: string;
};

/** Broad project phases. Keep this short: one line per phase. */
export const TIMELINE: Milestone[] = [
  {
    start: "2026-10",
    end: "2026-12",
    title: "Research & build",
    text: "Field research with farmers, then the chatbot and its launch on WhatsApp.",
  },
  {
    start: "2027-01",
    end: "2027-01",
    title: "Farmer pilot",
    text: "Farmers in Sukkur, Khairpur and Ghotki use the service and tell us what works.",
  },
  {
    start: "2027-02",
    end: "2027-02",
    title: "Evaluation & handover",
    text: "We measure the results and hand the service over.",
  },
];

export type Member = { name: string; role: string; bio: string };

export const TEAM: Member[] = [
  {
    name: "Dr Muhammad Ismail Mangrio",
    role: "Project Lead",
    bio: "Assistant Professor, Computer Science Department, Sukkur IBA University, Sindh, Pakistan.",
  },
  {
    name: "Prof. Dr Altaf Hussain Samo",
    role: "Co-lead",
    bio: "Dean, Faculty of Business and Media Science, Sukkur IBA University, Sindh, Pakistan.",
  },
  {
    name: "Mr Rasool Bakhsh Junejo",
    role: "Agriculture Consultant",
    bio: "Ex-Director, Agriculture Extension Department, Sukkur.",
  },
  {
    name: "Dr Mulazim Ali Khokhar",
    role: "Credit Expert",
    bio: "Assistant Professor, Business Administration Department, Sukkur IBA University.",
  },
  {
    name: "Dr Asad Ali Qazi",
    role: "Finance Expert",
    bio: "Assistant Professor, Business Administration Department, Sukkur IBA University.",
  },
  { name: "Salwa Ansari", role: "AI Team", bio: "Builds the chatbot, its AI features and the WhatsApp channel." },
  { name: "Abdul Haseeb", role: "AI Team", bio: "Builds the chatbot, its AI features and the WhatsApp channel." },
];

export const GOALS = [
  { sdg: 1, title: "No Poverty", color: "#E5243B", text: "Fair crop prices and access to credit protect farm incomes." },
  { sdg: 2, title: "Zero Hunger", color: "#DDA63A", text: "Timely sowing, fertiliser and pest advice raise yields." },
  { sdg: 6, title: "Clean Water", color: "#26BDE2", text: "Weather-aware irrigation saves scarce canal and ground water." },
  { sdg: 12, title: "Responsible Production", color: "#BF8B2E", text: "Organic and GAP guidance supports sustainable farming." },
  { sdg: 13, title: "Climate Action", color: "#3F7E44", text: "Heat, rain and frost alerts help farmers adapt to a changing climate." },
];

export const FAQ = [
  {
    q: "Does KisanRahnuma cost anything?",
    a: "No. The service is free for farmers. Normal WhatsApp data use applies.",
  },
  {
    q: "Do you store my phone number?",
    a: "Usage records are anonymous and never contain your phone number. If you subscribe to weekly updates, your number is kept in a separate, restricted list used only to send those updates.",
  },
  {
    q: "Which languages are supported?",
    a: "Sindhi, Urdu and English. You can switch language at any time from the menu.",
  },
  {
    q: "Which areas are covered?",
    a: "The pilot covers Sukkur, Khairpur and Ghotki districts in Sindh, with more districts planned.",
  },
  {
    q: "Can I send a voice note?",
    a: "Not yet. Voice notes are on the roadmap. For now, type your question or tap a menu button.",
  },
];
