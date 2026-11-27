import { Navigate, Route, Routes } from "react-router-dom";

import AdminShell from "./components/layout/AdminShell";
import AppShell from "./components/layout/AppShell";
import SiteLayout from "./components/site/SiteLayout";
import AdminContentPage from "./pages/admin/AdminContentPage";
import AdminCropPricesPage from "./pages/admin/AdminCropPricesPage";
import AdminFarmersPage from "./pages/admin/AdminFarmersPage";
import AdminLoginPage from "./pages/admin/AdminLoginPage";
import AdminOverviewPage from "./pages/admin/AdminOverviewPage";
import ChatPage from "./pages/ChatPage";
import { AboutPage, ContactPage, HomePage, ServicesPage, TeamPage, TimelinePage } from "./pages/site/SitePages";

export default function App() {
  return (
    <Routes>
      {/* Public website */}
      <Route element={<SiteLayout />}>
        <Route index element={<HomePage />} />
        <Route path="about" element={<AboutPage />} />
        <Route path="services" element={<ServicesPage />} />
        <Route path="timeline" element={<TimelinePage />} />
        <Route path="team" element={<TeamPage />} />
        <Route path="contact" element={<ContactPage />} />
      </Route>

      {/* Chat simulator */}
      <Route element={<AppShell />}>
        <Route path="chat" element={<ChatPage />} />
      </Route>

      {/* Admin dashboard */}
      <Route path="admin/login" element={<AdminLoginPage />} />
      <Route path="admin" element={<AdminShell />}>
        <Route index element={<AdminOverviewPage />} />
        <Route path="farmers" element={<AdminFarmersPage />} />
        <Route path="crop-prices" element={<AdminCropPricesPage />} />
        <Route path="content" element={<AdminContentPage />} />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
