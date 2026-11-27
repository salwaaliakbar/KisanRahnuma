import type { ReactNode } from "react";
import { Link } from "react-router-dom";

import { FAQ, GOALS, SERVICES, SITE, STEPS, TEAM, TIMELINE, type Milestone, type Service } from "../../content/site";
import {
  ArrowRightIcon,
  BadgeIcon,
  CheckIcon,
  CoinsIcon,
  DropletIcon,
  GlobeIcon,
  LeafIcon,
  PriceIcon,
  QuestionIcon,
  ShieldIcon,
  SunCloudIcon,
} from "../icons";
import WhatsAppButton from "./WhatsAppButton";

/* ---------- building blocks ---------- */

export function Container({ children, className = "" }: { children: ReactNode; className?: string }) {
  return <div className={`mx-auto max-w-6xl px-4 sm:px-6 ${className}`}>{children}</div>;
}

export function SectionHeading({
  eyebrow,
  title,
  intro,
  center = false,
}: {
  eyebrow: string;
  title: string;
  intro?: string;
  center?: boolean;
}) {
  return (
    <div className={center ? "mx-auto max-w-2xl text-center" : "max-w-2xl"}>
      <p className="text-sm font-semibold uppercase tracking-wider text-wheat-700">{eyebrow}</p>
      <h2 className="font-display mt-2 text-3xl font-semibold text-brand-950 sm:text-4xl">{title}</h2>
      {intro && <p className="mt-4 text-lg leading-relaxed text-ink-2">{intro}</p>}
    </div>
  );
}

/** Top banner for the inner pages (About, Services, ...). */
export function PageHeader({ eyebrow, title, intro }: { eyebrow: string; title: string; intro: string }) {
  return (
    <section className="relative overflow-hidden bg-brand-900 text-white">
      <FieldLines />
      <Container className="relative py-16 sm:py-20">
        <p className="text-sm font-semibold uppercase tracking-wider text-wheat-300">{eyebrow}</p>
        <h1 className="font-display mt-3 max-w-3xl text-4xl font-semibold sm:text-5xl">{title}</h1>
        <p className="mt-5 max-w-2xl text-lg leading-relaxed text-brand-100">{intro}</p>
      </Container>
    </section>
  );
}

/** Decorative furrow lines, like a ploughed field, behind dark banners. */
function FieldLines() {
  return (
    <svg className="pointer-events-none absolute inset-0 h-full w-full opacity-[0.09]" aria-hidden preserveAspectRatio="none" viewBox="0 0 800 400">
      {Array.from({ length: 14 }, (_, i) => (
        <path key={i} d={`M-50 ${430 - i * 34} Q 400 ${330 - i * 34} 850 ${400 - i * 30}`} fill="none" stroke="#f0cf7a" strokeWidth="2" />
      ))}
    </svg>
  );
}

function SectionLink({ to, children }: { to: string; children: ReactNode }) {
  return (
    <Link to={to} className="group inline-flex items-center gap-1.5 font-semibold text-brand-700 hover:text-brand-900">
      {children}
      <ArrowRightIcon width={18} height={18} className="transition-transform group-hover:translate-x-0.5" />
    </Link>
  );
}

/* ---------- hero ---------- */

export function Hero() {
  return (
    <section className="relative overflow-hidden bg-gradient-to-b from-brand-950 via-brand-900 to-brand-800 text-white">
      <FieldLines />
      <div className="pointer-events-none absolute -right-24 -top-24 h-80 w-80 rounded-full bg-wheat-500/20 blur-3xl" aria-hidden />
      <Container className="relative grid items-center gap-12 py-16 sm:py-20 lg:grid-cols-[1.15fr_1fr] lg:py-24">
        <div>
          <p className="inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/5 px-3 py-1 text-sm text-brand-100">
            <LeafIcon width={16} height={16} className="text-wheat-300" />
            Climate-smart farming for Sindh
          </p>
          <h1 className="font-display mt-6 text-4xl font-semibold leading-[1.1] sm:text-5xl lg:text-6xl">
            Farming advice in your pocket, <span className="text-wheat-300">in your language.</span>
          </h1>
          <p className="mt-6 max-w-xl text-lg leading-relaxed text-brand-100">
            KisanRahnuma is a free WhatsApp assistant for farmers. Get weather alerts, crop rates, credit and
            certification guidance, and answers to farming questions in Sindhi, Urdu and English.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <WhatsAppButton size="lg" />
            <Link
              to="/services"
              className="inline-flex items-center gap-2 rounded-full border border-white/25 px-6 py-3.5 font-semibold text-white transition hover:bg-white/10"
            >
              Explore services
              <ArrowRightIcon width={18} height={18} />
            </Link>
          </div>
          <p className="mt-6 text-sm text-brand-200">
            Pilot districts: {SITE.districts.join(", ")} · No app, no sign-up
          </p>
        </div>
        <PhoneMockup />
      </Container>
    </section>
  );
}

function PhoneMockup() {
  return (
    <div className="mx-auto w-full max-w-[320px]" aria-label="Example WhatsApp conversation with KisanRahnuma" role="img">
      <div className="rounded-[2.5rem] border-[10px] border-brand-950 bg-brand-950 shadow-2xl shadow-black/40">
        <div className="overflow-hidden rounded-[1.8rem] bg-[#efe7dd]">
          <div className="flex items-center gap-2.5 bg-[#075e54] px-4 py-3 text-white">
            <span className="grid h-8 w-8 place-items-center rounded-full bg-brand-500">
              <LeafIcon width={16} height={16} />
            </span>
            <div className="leading-tight">
              <p className="text-sm font-semibold">KisanRahnuma</p>
              <p className="text-[11px] text-white/75">online</p>
            </div>
          </div>
          <div className="space-y-2 px-3 py-4 text-[13px] leading-snug text-ink">
            <Bubble me>Hi</Bubble>
            <Bubble>
              Welcome to <b>KisanRahnuma</b>! What would you like to know?
              <div className="mt-2 grid gap-1">
                {["Weather", "Crop Rates", "Ask Anything"].map((o) => (
                  <span key={o} className="rounded-md border border-line bg-white py-1 text-center text-[12px] font-medium text-[#027eb5]">
                    {o}
                  </span>
                ))}
              </div>
            </Bubble>
            <Bubble me>
              <span lang="sd" dir="rtl" className="block text-right">
                ڪڻڪ ڪڏهن پوکجي؟
              </span>
            </Bubble>
            <Bubble>
              In upper Sindh, sow wheat between <b>1 and 30 November</b>. Late sowing can reduce yield.
              <p className="mt-1.5 text-[11px] text-ink-3">Was this helpful? 👍 👎</p>
            </Bubble>
          </div>
        </div>
      </div>
    </div>
  );
}

function Bubble({ me = false, children }: { me?: boolean; children: ReactNode }) {
  return (
    <div className={`flex ${me ? "justify-end" : "justify-start"}`}>
      <div className={`max-w-[85%] rounded-lg px-2.5 py-1.5 shadow-sm ${me ? "bg-[#d9fdd3]" : "bg-white"}`}>{children}</div>
    </div>
  );
}

/* ---------- stats ---------- */

export function Stats() {
  const stats = [
    { value: "5", label: "farmer services" },
    { value: "3", label: "languages: Sindhi, Urdu, English" },
    { value: "3", label: "pilot districts in Sindh" },
    { value: "0", label: "phone numbers in usage records" },
  ];
  return (
    <section className="border-b border-line bg-white">
      <Container className="grid grid-cols-2 gap-6 py-10 md:grid-cols-4">
        {stats.map((s) => (
          <div key={s.label}>
            <p className="font-display text-4xl font-semibold text-brand-700">{s.value}</p>
            <p className="mt-1 text-sm text-ink-2">{s.label}</p>
          </div>
        ))}
      </Container>
    </section>
  );
}

/* ---------- about ---------- */

const PILLARS = [
  {
    icon: GlobeIcon,
    title: "In the farmer’s language",
    text: "Every answer is available in Sindhi, Urdu and English, written in plain words.",
  },
  {
    icon: SunCloudIcon,
    title: "Built for a changing climate",
    text: "Heat waves, floods and erratic rain are hitting Sindh harder. Timely, local advice helps farmers adapt.",
  },
  {
    icon: ShieldIcon,
    title: "Private by design",
    text: "Farmers choose whether usage is recorded. Records are anonymous and never hold a phone number.",
  },
];

export function AboutSection({ full = false }: { full?: boolean }) {
  return (
    <section className="py-20">
      <Container className="grid gap-12 lg:grid-cols-2 lg:items-start">
        <div>
          <SectionHeading
            eyebrow="About KisanRahnuma"
            title="A trusted guide (rahnuma) for every kisan"
          />
          <div className="mt-5 space-y-4 text-lg leading-relaxed text-ink-2">
            <p>
              Small farmers in Sindh make big decisions every season, often without timely information on weather,
              prices or support schemes. Extension services are stretched thin, and most digital tools are in
              English or need a smartphone app.
            </p>
            <p>
              KisanRahnuma meets farmers where they already are: on WhatsApp. One message brings reliable, local
              advice in their own language, any time of day.
            </p>
            {full && (
              <p>
                The project runs from October 2026 to February 2027. It starts with a pilot in {SITE.districts.join(", ")}
                , gathers feedback on every answer, and uses what farmers tell us to improve the service before it
                grows to more districts.
              </p>
            )}
          </div>
          {!full && (
            <div className="mt-6">
              <SectionLink to="/about">More about the project</SectionLink>
            </div>
          )}
        </div>
        <div className="grid gap-4">
          {PILLARS.map(({ icon: Icon, title, text }) => (
            <div key={title} className="flex gap-4 rounded-2xl border border-line bg-white p-5">
              <span className="grid h-11 w-11 shrink-0 place-items-center rounded-xl bg-brand-50 text-brand-700">
                <Icon width={22} height={22} />
              </span>
              <div>
                <h3 className="font-semibold text-brand-950">{title}</h3>
                <p className="mt-1 text-ink-2">{text}</p>
              </div>
            </div>
          ))}
        </div>
      </Container>
    </section>
  );
}

export function MissionVision() {
  const items = [
    {
      title: "Mission",
      text: "Give every small farmer in Sindh free, timely and trustworthy farming advice in their own language, through the phone they already use.",
    },
    {
      title: "Vision",
      text: "Resilient farming communities that grow more with less water and fewer chemicals, earn fair prices, and stay ahead of climate risks.",
    },
  ];
  return (
    <section className="bg-white py-20">
      <Container className="grid gap-6 md:grid-cols-2">
        {items.map((i) => (
          <div key={i.title} className="rounded-3xl bg-gradient-to-br from-wheat-100 to-soil p-8">
            <h2 className="font-display text-2xl font-semibold text-brand-950">{i.title}</h2>
            <p className="mt-3 text-lg leading-relaxed text-ink-2">{i.text}</p>
          </div>
        ))}
      </Container>
    </section>
  );
}

/* ---------- services ---------- */

const SERVICE_ICON: Record<Service["key"], typeof LeafIcon> = {
  weather: SunCloudIcon,
  rates: PriceIcon,
  credit: CoinsIcon,
  certifications: BadgeIcon,
  ask: QuestionIcon,
};

const SERVICE_TINT: Record<Service["key"], string> = {
  weather: "bg-sky-soft text-sky-deep",
  rates: "bg-wheat-100 text-wheat-700",
  credit: "bg-brand-50 text-brand-700",
  certifications: "bg-[#eef3e2] text-[#55702a]",
  ask: "bg-[#f3ebe4] text-[#8a5a3c]",
};

export function ServicesSection({ detailed = false }: { detailed?: boolean }) {
  return (
    <section className={detailed ? "py-20" : "bg-white py-20"}>
      <Container>
        {!detailed && (
          <SectionHeading
            eyebrow="Services"
            title="Everything a farmer needs, in one chat"
            intro="Five services, available in a single WhatsApp conversation. Tap a button or just type your question."
          />
        )}
        <div className={`grid gap-5 sm:grid-cols-2 lg:grid-cols-3 ${detailed ? "" : "mt-12"}`}>
          {SERVICES.map((s) => {
            const Icon = SERVICE_ICON[s.key];
            return (
              <article key={s.key} className="flex flex-col rounded-2xl border border-line bg-soil/60 p-6 transition hover:-translate-y-0.5 hover:shadow-md hover:shadow-brand-900/5">
                <span className={`grid h-12 w-12 place-items-center rounded-xl ${SERVICE_TINT[s.key]}`}>
                  <Icon width={24} height={24} />
                </span>
                <h3 className="mt-5 text-lg font-semibold text-brand-950">{s.title}</h3>
                <p className="mt-2 leading-relaxed text-ink-2">{s.summary}</p>
                {detailed && (
                  <ul className="mt-4 space-y-2 text-sm text-ink-2">
                    {s.points.map((p) => (
                      <li key={p} className="flex gap-2">
                        <CheckIcon width={18} height={18} className="shrink-0 text-brand-600" />
                        {p}
                      </li>
                    ))}
                  </ul>
                )}
              </article>
            );
          })}
          <article className="flex flex-col justify-between rounded-2xl bg-brand-800 p-6 text-white">
            <div>
              <h3 className="font-display text-2xl font-semibold">Try it now</h3>
              <p className="mt-2 text-brand-100">
                Say “Hi” and the assistant will guide you. It takes less than a minute to get started.
              </p>
            </div>
            <WhatsAppButton className="mt-6 self-start" />
          </article>
        </div>
        {!detailed && (
          <div className="mt-8">
            <SectionLink to="/services">See service details</SectionLink>
          </div>
        )}
      </Container>
    </section>
  );
}

export function HowItWorks() {
  return (
    <section className="py-20">
      <Container>
        <SectionHeading eyebrow="How it works" title="From “Hi” to helpful advice in four steps" center />
        <ol className="mt-12 grid gap-5 md:grid-cols-2 lg:grid-cols-4">
          {STEPS.map((s, i) => (
            <li key={s.title} className="relative rounded-2xl border border-line bg-white p-6">
              <span className="font-display grid h-10 w-10 place-items-center rounded-full bg-wheat-300 text-lg font-semibold text-brand-950">
                {i + 1}
              </span>
              <h3 className="mt-4 font-semibold text-brand-950">{s.title}</h3>
              <p className="mt-1.5 text-ink-2">{s.text}</p>
            </li>
          ))}
        </ol>
      </Container>
    </section>
  );
}

/* ---------- climate & sustainability ---------- */

export function ClimateGoals() {
  return (
    <section className="relative overflow-hidden bg-sky-soft py-20">
      <Container>
        <div className="grid gap-12 lg:grid-cols-[1fr_1.3fr] lg:items-center">
          <div>
            <SectionHeading
              eyebrow="Climate & sustainability"
              title="Helping farms adapt to a changing climate"
              intro="Pakistan is among the countries most affected by climate change, and Sindh’s farmers feel it first: the 2022 floods, record heat and shifting rains. KisanRahnuma turns climate and market data into simple, timely actions."
            />
            <ul className="mt-6 space-y-3 text-ink-2">
              {[
                { icon: DropletIcon, t: "Water-smart irrigation timed to the forecast" },
                { icon: SunCloudIcon, t: "Early alerts for heat, frost, wind and rain" },
                { icon: LeafIcon, t: "Guidance on organic and good-practice farming" },
              ].map(({ icon: Icon, t }) => (
                <li key={t} className="flex items-center gap-3">
                  <Icon width={20} height={20} className="shrink-0 text-sky-deep" />
                  {t}
                </li>
              ))}
            </ul>
          </div>
          <div>
            <p className="text-sm font-semibold text-ink-2">Contributing to the UN Sustainable Development Goals</p>
            <div className="mt-4 grid gap-3 sm:grid-cols-2">
              {GOALS.map((g) => (
                <div key={g.sdg} className="flex gap-3 rounded-2xl bg-white p-4 shadow-sm">
                  <span
                    className="font-display grid h-12 w-12 shrink-0 place-items-center rounded-lg text-lg font-bold text-white"
                    style={{ background: g.color }}
                    aria-label={`SDG ${g.sdg}`}
                  >
                    {g.sdg}
                  </span>
                  <div>
                    <h3 className="font-semibold text-brand-950">{g.title}</h3>
                    <p className="mt-0.5 text-sm text-ink-2">{g.text}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </Container>
    </section>
  );
}

/* ---------- timeline ---------- */

type Status = "done" | "now" | "next";

function statusOf(m: Milestone, today = new Date()): Status {
  const [sy, sm] = m.start.split("-").map(Number);
  const [ey, em] = m.end.split("-").map(Number);
  const start = new Date(sy, sm - 1, 1);
  const afterEnd = new Date(ey, em, 1); // first day of the month after `end`
  if (today >= afterEnd) return "done";
  if (today >= start) return "now";
  return "next";
}

function monthLabel(ym: string) {
  const [y, m] = ym.split("-").map(Number);
  return new Date(y, m - 1, 1).toLocaleString("en-GB", { month: "short", year: "numeric" });
}

const STATUS_UI: Record<Status, { label: string; dot: string; chip: string }> = {
  done: { label: "Completed", dot: "bg-brand-600 text-white", chip: "bg-brand-50 text-brand-700" },
  now: { label: "In progress", dot: "bg-wheat-500 text-brand-950 ring-4 ring-wheat-300/50", chip: "bg-wheat-100 text-wheat-700" },
  next: { label: "Upcoming", dot: "bg-white text-ink-3 border-2 border-line", chip: "bg-canvas text-ink-3" },
};

export function TimelineSection({ compact = false }: { compact?: boolean }) {
  return (
    <section className={compact ? "bg-white py-20" : "py-20"}>
      <Container>
        {compact && (
          <SectionHeading
            eyebrow="Project timeline"
            title="October 2026 to February 2027"
            intro="Five months from field research to a working pilot with farmers."
          />
        )}
        <ol className={`relative ${compact ? "mt-12" : ""} space-y-6 before:absolute before:bottom-4 before:left-[19px] before:top-4 before:w-0.5 before:bg-line`}>
          {TIMELINE.map((m, i) => {
            const st = statusOf(m);
            const ui = STATUS_UI[st];
            const when = m.start === m.end ? monthLabel(m.start) : `${monthLabel(m.start)} – ${monthLabel(m.end)}`;
            return (
              <li key={m.title} className="relative flex gap-5">
                <span className={`relative z-10 grid h-10 w-10 shrink-0 place-items-center rounded-full text-sm font-semibold ${ui.dot}`}>
                  {st === "done" ? <CheckIcon width={18} height={18} /> : i + 1}
                </span>
                <div className="flex-1 rounded-2xl border border-line bg-white p-5 sm:p-6">
                  <div className="flex flex-wrap items-center gap-x-3 gap-y-1">
                    <p className="text-sm font-semibold text-wheat-700">{when}</p>
                    <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${ui.chip}`}>{ui.label}</span>
                  </div>
                  <h3 className="mt-1.5 text-lg font-semibold text-brand-950">{m.title}</h3>
                  <p className="mt-1.5 text-ink-2">{m.text}</p>
                </div>
              </li>
            );
          })}
        </ol>
      </Container>
    </section>
  );
}

/* ---------- team ---------- */

function initials(name: string, role: string) {
  const src = name === "Team Member" ? role : name;
  return src
    .split(/\s+/)
    .filter((w) => /^[A-Za-z]/.test(w))
    .slice(0, 2)
    .map((w) => w[0].toUpperCase())
    .join("");
}

const AVATAR_TINTS = ["bg-brand-100 text-brand-800", "bg-wheat-100 text-wheat-700", "bg-sky-soft text-sky-deep"];

export function TeamSection({ limit }: { limit?: number }) {
  const members = limit ? TEAM.slice(0, limit) : TEAM;
  return (
    <section className="py-20">
      <Container>
        {limit && (
          <SectionHeading
            eyebrow="Our team"
            title="The people behind KisanRahnuma"
            intro="Agriculture, climate, technology and language experts working with farming communities."
          />
        )}
        <div className={`grid gap-5 sm:grid-cols-2 lg:grid-cols-3 ${limit ? "mt-12" : ""}`}>
          {members.map((m, i) => (
            <article key={`${m.role}-${i}`} className="rounded-2xl border border-line bg-white p-6">
              <span className={`font-display grid h-16 w-16 place-items-center rounded-2xl text-xl font-semibold ${AVATAR_TINTS[i % AVATAR_TINTS.length]}`}>
                {initials(m.name, m.role)}
              </span>
              <h3 className="mt-4 text-lg font-semibold text-brand-950">{m.name}</h3>
              <p className="text-sm font-medium text-wheat-700">{m.role}</p>
              <p className="mt-2 text-ink-2">{m.bio}</p>
            </article>
          ))}
        </div>
        {limit && TEAM.length > limit && (
          <div className="mt-8">
            <SectionLink to="/team">Meet the whole team</SectionLink>
          </div>
        )}
      </Container>
    </section>
  );
}

/* ---------- FAQ & call to action ---------- */

export function FaqSection() {
  return (
    <section className="bg-white py-20">
      <Container className="grid gap-10 lg:grid-cols-[1fr_1.5fr]">
        <SectionHeading eyebrow="FAQ" title="Common questions" intro="Can’t find your answer? Send us a message." />
        <div className="divide-y divide-line rounded-2xl border border-line">
          {FAQ.map((f) => (
            <details key={f.q} className="group px-5 py-4">
              <summary className="flex cursor-pointer items-center justify-between gap-4 font-semibold text-brand-950">
                {f.q}
                <span className="faq-chevron grid h-7 w-7 shrink-0 place-items-center rounded-full bg-brand-50 text-lg leading-none text-brand-700 transition-transform">
                  +
                </span>
              </summary>
              <p className="mt-3 leading-relaxed text-ink-2">{f.a}</p>
            </details>
          ))}
        </div>
      </Container>
    </section>
  );
}

export function CtaBand() {
  return (
    <section className="py-20">
      <Container>
        <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-brand-800 to-brand-950 px-6 py-14 text-center text-white sm:px-12">
          <FieldLines />
          <div className="relative">
            <h2 className="font-display text-3xl font-semibold sm:text-4xl">Start a conversation with KisanRahnuma</h2>
            <p className="mx-auto mt-4 max-w-xl text-lg text-brand-100">
              Send “Hi” on WhatsApp and get farming advice in Sindhi, Urdu or English. Free for every farmer.
            </p>
            <div className="mt-8 flex flex-wrap justify-center gap-3">
              <WhatsAppButton size="lg" />
              <Link
                to="/chat"
                className="inline-flex items-center gap-2 rounded-full border border-white/25 px-6 py-3.5 font-semibold transition hover:bg-white/10"
              >
                Try the web demo
              </Link>
            </div>
          </div>
        </div>
      </Container>
    </section>
  );
}
