/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * This file is part of the RiverCityClean SaaS CRM system.
 */

import React from 'react';
import Card from '../components/ui/Card';

const InboxPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-bg-base">
      {/* Page header */}
      <div className="p-8 pb-6 border-b border-white/5">
        <h1 className="text-3xl font-display font-bold text-gradient">Inbox</h1>
        <p className="text-sm text-text-muted mt-1">Recent interactions and messages from all channels</p>
      </div>

      {/* Main content */}
      <main className="p-8">
        <div className="max-w-4xl">
          <Card padding="none">
            {/* Message list */}
            <div className="divide-y divide-white/5">
              <div className="p-4 hover:bg-white/5 cursor-pointer transition-colors">
                <div className="flex items-start gap-4">
                  <div className="w-10 h-10 rounded-full bg-primary/20 flex items-center justify-center flex-shrink-0">
                    <span className="text-primary font-bold">AC</span>
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-1">
                      <h4 className="font-medium text-text-primary">Acme Corp</h4>
                      <span className="text-xs text-text-muted">2 hours ago</span>
                    </div>
                    <p className="text-sm text-text-secondary">Interested in learning more about your services...</p>
                    <div className="flex items-center gap-2 mt-2">
                      <span className="text-xs px-2 py-1 bg-electric-cyan/10 text-electric-cyan rounded">Email</span>
                      <span className="text-xs px-2 py-1 bg-warning/10 text-warning rounded">Unread</span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="p-4 hover:bg-white/5 cursor-pointer transition-colors">
                <div className="flex items-start gap-4">
                  <div className="w-10 h-10 rounded-full bg-success/20 flex items-center justify-center flex-shrink-0">
                    <span className="text-success font-bold">TS</span>
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-1">
                      <h4 className="font-medium text-text-primary">Tech Solutions</h4>
                      <span className="text-xs text-text-muted">5 hours ago</span>
                    </div>
                    <p className="text-sm text-text-secondary">Thanks for the quick response! When can we schedule a demo?</p>
                    <div className="flex items-center gap-2 mt-2">
                      <span className="text-xs px-2 py-1 bg-primary/10 text-primary rounded">SMS</span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="p-4 hover:bg-white/5 cursor-pointer transition-colors opacity-60">
                <div className="flex items-start gap-4">
                  <div className="w-10 h-10 rounded-full bg-text-muted/20 flex items-center justify-center flex-shrink-0">
                    <span className="text-text-muted font-bold">GI</span>
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-1">
                      <h4 className="font-medium text-text-primary">Global Inc</h4>
                      <span className="text-xs text-text-muted">Yesterday</span>
                    </div>
                    <p className="text-sm text-text-secondary">Can you send over the pricing details?</p>
                    <div className="flex items-center gap-2 mt-2">
                      <span className="text-xs px-2 py-1 bg-white/10 text-text-muted rounded">Email</span>
                      <span className="text-xs text-text-muted">Read</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </Card>
        </div>
      </main>
    </div>
  );
};

export default InboxPage;
