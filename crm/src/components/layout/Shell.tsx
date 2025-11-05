/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * This file is part of the RiverCityClean SaaS CRM system.
 */

import React, { useState } from 'react';
import { Sidebar } from '../navigation/Sidebar';
import { Topbar } from '../navigation/Topbar';
import {
  CommandPalette,
  useCommandPalette,
} from '../navigation/CommandPalette';

interface ShellProps {
  children: React.ReactNode;
}

const Shell: React.FC<ShellProps> = ({ children }) => {
  const [isMobileSidebarOpen, setIsMobileSidebarOpen] = useState(false);
  const { open: commandOpen, setOpen: setCommandOpen } = useCommandPalette();

  // Detect screen size for responsive sidebar
  const [isMobile, setIsMobile] = useState(false);

  React.useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 1024); // lg breakpoint
    };

    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      {/* Desktop Sidebar */}
      {!isMobile && <Sidebar />}

      {/* Mobile Sidebar (Sheet) */}
      {isMobile && (
        <Sidebar
          open={isMobileSidebarOpen}
          onOpenChange={setIsMobileSidebarOpen}
          isMobile={true}
        />
      )}

      {/* Main Content Area */}
      <div className="flex flex-col flex-1 overflow-hidden">
        {/* Topbar */}
        <Topbar
          onMenuToggle={() => setIsMobileSidebarOpen(true)}
          onCommandOpen={() => setCommandOpen(true)}
        />

        {/* Page Content */}
        <main className="flex-1 overflow-auto bg-bg-base">
          {children}
        </main>
      </div>

      {/* Command Palette */}
      <CommandPalette open={commandOpen} onOpenChange={setCommandOpen} />
    </div>
  );
};

export default Shell;
