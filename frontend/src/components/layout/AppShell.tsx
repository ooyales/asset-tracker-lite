import { useState, useEffect } from 'react';
import { Outlet } from 'react-router-dom';
import Navbar from './Navbar';
import Sidebar from './Sidebar';
import { useIsMobile } from '@/hooks/useIsMobile';

export default function AppShell() {
  const isMobile = useIsMobile();
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  // Close mobile menu when crossing to desktop
  useEffect(() => {
    if (!isMobile) setMobileMenuOpen(false);
  }, [isMobile]);

  return (
    <div className="min-h-screen bg-eaw-background">
      <Navbar
        isMobile={isMobile}
        onMenuToggle={() => setMobileMenuOpen(o => !o)}
      />

      {/* Backdrop — mobile drawer open */}
      {isMobile && mobileMenuOpen && (
        <div
          className="fixed inset-0 bg-black/40 z-30 transition-opacity"
          onClick={() => setMobileMenuOpen(false)}
        />
      )}

      <Sidebar
        collapsed={isMobile ? false : sidebarCollapsed}
        onToggle={() => setSidebarCollapsed(c => !c)}
        isMobile={isMobile}
        mobileOpen={mobileMenuOpen}
        onMobileClose={() => setMobileMenuOpen(false)}
      />

      <main
        className={`pt-14 transition-all duration-200 ${
          isMobile ? 'ml-0' : sidebarCollapsed ? 'ml-12' : 'ml-56'
        }`}
      >
        <div className="p-4 md:p-6">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
