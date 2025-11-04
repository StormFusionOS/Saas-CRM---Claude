/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * AI Governance Page
 * Review and approve AI-generated changes before execution
 */

import React from 'react';
import ChangeLogTable from '../components/governance/ChangeLogTable';

const AIGovernancePage: React.FC = () => {
  return (
    <div className="min-h-screen bg-bg-base">
      {/* Page Header */}
      <div className="p-8 pb-6 border-b border-white/5">
        <h1 className="text-3xl font-display font-bold text-gradient">AI Governance</h1>
        <p className="text-sm text-text-muted mt-1">
          Review and approve AI-generated changes before execution
        </p>
      </div>

      {/* Main Content */}
      <main className="p-8">
        <ChangeLogTable />
      </main>
    </div>
  );
};

export default AIGovernancePage;
