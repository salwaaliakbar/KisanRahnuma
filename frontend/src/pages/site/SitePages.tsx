import { useEffect } from "react";

import { MailIcon, PinIcon, WhatsAppIcon } from "../../components/icons";
import {
  AboutSection,
  ClimateGoals,
  Container,
  CtaBand,
  FaqSection,
  Hero,
  HowItWorks,
  MissionVision,
  PageHeader,
  ServicesSection,
  Stats,
  TeamSection,
  TimelineSection,
} from "../../components/site/sections";
import WhatsAppButton from "../../components/site/WhatsAppButton";
import { SITE } from "../../content/site";
import { WHATSAPP_ENABLED } from "../../lib/whatsapp";

function useTitle(title?: string) {
  useEffect(() => {
    document.title = title ? `${title} · KisanRahnuma` : "KisanRahnuma: Farmer Assistant";
  }, [title]);
}

export function HomePage() {
  useTitle();
  return (
    <>
      <Hero />
      <Stats />
      <AboutSection />
      <ServicesSection />
      <HowItWorks />
      <ClimateGoals />
      <TimelineSection compact />
      <TeamSection limit={3} />
      <FaqSection />
      <CtaBand />
    </>
  );
}

export function AboutPage() {
  useTitle("About");
  return (
    <>
      <PageHeader
        eyebrow="About"
        title="Reliable farming advice for the farmers of Sindh"
        intro="KisanRahnuma (“farmer’s guide”) is a WhatsApp chatbot that brings weather, market, credit and farming knowledge to small farmers in their own language."
      />
      <AboutSection full />
      <MissionVision />
      <ClimateGoals />
      <CtaBand />
    </>
  );
}

export function ServicesPage() {
  useTitle("Services");
  return (
    <>
      <PageHeader
        eyebrow="Services"
        title="Five services in one WhatsApp chat"
        intro="Every service works in Sindhi, Urdu and English. Each answer ends with a quick “Was this helpful?” so we can keep improving."
      />
      <ServicesSection detailed />
      <HowItWorks />
      <CtaBand />
    </>
  );
}

export function TimelinePage() {
  useTitle("Timeline");
  return (
    <>
      <PageHeader
        eyebrow="Project timeline"
        title="October 2026 to February 2027"
        intro="From listening to farmers, to a working WhatsApp assistant, to a pilot in three districts of Sindh."
      />
      <TimelineSection />
      <CtaBand />
    </>
  );
}

export function TeamPage() {
  useTitle("Team");
  return (
    <>
      <PageHeader
        eyebrow="Our team"
        title="The people behind KisanRahnuma"
        intro="A team of agriculture, climate, technology and language specialists working alongside farming communities."
      />
      <TeamSection />
      <CtaBand />
    </>
  );
}

export function ContactPage() {
  useTitle("Contact");
  const cards = [
    {
      icon: WhatsAppIcon,
      title: "WhatsApp",
      text: WHATSAPP_ENABLED
        ? "Farmers: message us and the assistant replies instantly."
        : "Our WhatsApp number launches soon. Until then, try the web version of the chatbot.",
      action: <WhatsAppButton className="mt-5" label={WHATSAPP_ENABLED ? "Chat on WhatsApp" : "Open web chat"} />,
    },
    {
      icon: MailIcon,
      title: "Email",
      text: "Partnerships, research and media enquiries.",
      action: (
        <a href={`mailto:${SITE.email}`} className="mt-5 inline-block font-semibold text-brand-700 hover:text-brand-900">
          {SITE.email}
        </a>
      ),
    },
    {
      icon: PinIcon,
      title: "Location",
      text: `Working with farmers in ${SITE.districts.join(", ")}.`,
      action: <p className="mt-5 font-semibold text-brand-950">{SITE.location}</p>,
    },
  ];
  return (
    <>
      <PageHeader
        eyebrow="Contact"
        title="Get in touch"
        intro="Farmers can reach the assistant on WhatsApp any time. For partnerships and everything else, contact the team."
      />
      <section className="py-20">
        <Container className="grid gap-5 md:grid-cols-3">
          {cards.map(({ icon: Icon, title, text, action }) => (
            <article key={title} className="flex flex-col rounded-2xl border border-line bg-white p-6">
              <span className="grid h-12 w-12 place-items-center rounded-xl bg-brand-50 text-brand-700">
                <Icon width={24} height={24} />
              </span>
              <h2 className="mt-4 text-lg font-semibold text-brand-950">{title}</h2>
              <p className="mt-1.5 flex-1 text-ink-2">{text}</p>
              <div>{action}</div>
            </article>
          ))}
        </Container>
      </section>
      <FaqSection />
    </>
  );
}
