/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * Schema (JSON-LD) Generator
 * Generate and validate structured data markup
 */

import React from 'react';
import Card from '../components/ui/Card';
import { Code, CheckCircle, FileJson, Layers } from 'lucide-react';

const SchemaGeneratorPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-bg-base">
      <div className="p-8 pb-6 border-b border-white/5">
        <h1 className="text-3xl font-display font-bold text-gradient">Schema (JSON-LD) Generator</h1>
        <p className="text-sm text-text-muted mt-1">
          Generate and validate structured data markup for enhanced search visibility
        </p>
      </div>

      <main className="p-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card className="relative overflow-hidden glow-hover">
            <div className="absolute top-0 right-0 w-24 h-24 bg-primary/10 rounded-full blur-2xl" />
            <div className="relative">
              <div className="flex items-center gap-2 mb-2">
                <Layers className="w-4 h-4 text-primary" />
                <h3 className="text-sm font-medium text-text-secondary">Schema Types</h3>
              </div>
              <p className="text-4xl font-display font-bold text-primary">12</p>
              <div className="mt-2 text-xs text-text-muted">Available templates</div>
            </div>
          </Card>

          <Card className="relative overflow-hidden glow-hover">
            <div className="absolute top-0 right-0 w-24 h-24 bg-success/10 rounded-full blur-2xl" />
            <div className="relative">
              <div className="flex items-center gap-2 mb-2">
                <FileJson className="w-4 h-4 text-success" />
                <h3 className="text-sm font-medium text-text-secondary">Generated</h3>
              </div>
              <p className="text-4xl font-display font-bold text-success">0</p>
              <div className="mt-2 text-xs text-text-muted">Schema markups</div>
            </div>
          </Card>

          <Card className="relative overflow-hidden glow-hover">
            <div className="absolute top-0 right-0 w-24 h-24 bg-electric-cyan/10 rounded-full blur-2xl" />
            <div className="relative">
              <div className="flex items-center gap-2 mb-2">
                <CheckCircle className="w-4 h-4 text-electric-cyan" />
                <h3 className="text-sm font-medium text-text-secondary">Validated</h3>
              </div>
              <p className="text-4xl font-display font-bold text-electric-cyan">0</p>
              <div className="mt-2 text-xs text-text-muted">Passed validation</div>
            </div>
          </Card>

          <Card className="relative overflow-hidden glow-hover">
            <div className="absolute top-0 right-0 w-24 h-24 bg-warning/10 rounded-full blur-2xl" />
            <div className="relative">
              <div className="flex items-center gap-2 mb-2">
                <Code className="w-4 h-4 text-warning" />
                <h3 className="text-sm font-medium text-text-secondary">Pages with Schema</h3>
              </div>
              <p className="text-4xl font-display font-bold text-warning">0</p>
              <div className="mt-2 text-xs text-text-muted">Implemented</div>
            </div>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card padding="lg">
            <h2 className="text-xl font-display font-semibold mb-4">Popular Schema Types</h2>
            <div className="space-y-3">
              <div className="p-3 bg-white/5 rounded-lg border border-primary/20">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-primary">Organization</span>
                  <span className="text-xs bg-primary/10 text-primary px-2 py-1 rounded">Essential</span>
                </div>
                <p className="text-xs text-text-muted">Company info, logo, contact details, social profiles</p>
              </div>
              <div className="p-3 bg-white/5 rounded-lg border border-white/10">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-text-primary">LocalBusiness</span>
                  <span className="text-xs bg-white/10 text-text-muted px-2 py-1 rounded">Maps</span>
                </div>
                <p className="text-xs text-text-muted">Business location, hours, service area, reviews</p>
              </div>
              <div className="p-3 bg-white/5 rounded-lg border border-white/10">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-text-primary">Product</span>
                  <span className="text-xs bg-white/10 text-text-muted px-2 py-1 rounded">E-commerce</span>
                </div>
                <p className="text-xs text-text-muted">Product details, pricing, availability, reviews</p>
              </div>
              <div className="p-3 bg-white/5 rounded-lg border border-white/10">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-text-primary">Article</span>
                  <span className="text-xs bg-white/10 text-text-muted px-2 py-1 rounded">Content</span>
                </div>
                <p className="text-xs text-text-muted">Blog posts with headline, author, publish date, image</p>
              </div>
              <div className="p-3 bg-white/5 rounded-lg border border-white/10">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-text-primary">FAQPage</span>
                  <span className="text-xs bg-white/10 text-text-muted px-2 py-1 rounded">Rich Results</span>
                </div>
                <p className="text-xs text-text-muted">FAQ sections that can appear in search results</p>
              </div>
              <div className="p-3 bg-white/5 rounded-lg border border-white/10">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-text-primary">BreadcrumbList</span>
                  <span className="text-xs bg-white/10 text-text-muted px-2 py-1 rounded">Navigation</span>
                </div>
                <p className="text-xs text-text-muted">Page hierarchy shown in search results</p>
              </div>
            </div>
          </Card>

          <Card padding="lg">
            <h2 className="text-xl font-display font-semibold mb-4">Implementation Guide</h2>
            <div className="space-y-3">
              <div className="flex gap-3">
                <div className="flex items-center justify-center w-6 h-6 rounded-full bg-primary/20 text-primary text-xs font-bold flex-shrink-0">
                  1
                </div>
                <div>
                  <p className="font-medium text-text-primary mb-1">Select Schema Type</p>
                  <p className="text-xs text-text-muted">Choose the appropriate schema.org type for your content</p>
                </div>
              </div>
              <div className="flex gap-3">
                <div className="flex items-center justify-center w-6 h-6 rounded-full bg-primary/20 text-primary text-xs font-bold flex-shrink-0">
                  2
                </div>
                <div>
                  <p className="font-medium text-text-primary mb-1">Fill Required Fields</p>
                  <p className="text-xs text-text-muted">Complete all required properties for the schema type</p>
                </div>
              </div>
              <div className="flex gap-3">
                <div className="flex items-center justify-center w-6 h-6 rounded-full bg-primary/20 text-primary text-xs font-bold flex-shrink-0">
                  3
                </div>
                <div>
                  <p className="font-medium text-text-primary mb-1">Add Recommended Fields</p>
                  <p className="text-xs text-text-muted">Include optional fields for richer search appearance</p>
                </div>
              </div>
              <div className="flex gap-3">
                <div className="flex items-center justify-center w-6 h-6 rounded-full bg-primary/20 text-primary text-xs font-bold flex-shrink-0">
                  4
                </div>
                <div>
                  <p className="font-medium text-text-primary mb-1">Generate JSON-LD</p>
                  <p className="text-xs text-text-muted">System creates properly formatted JSON-LD markup</p>
                </div>
              </div>
              <div className="flex gap-3">
                <div className="flex items-center justify-center w-6 h-6 rounded-full bg-primary/20 text-primary text-xs font-bold flex-shrink-0">
                  5
                </div>
                <div>
                  <p className="font-medium text-text-primary mb-1">Validate Schema</p>
                  <p className="text-xs text-text-muted">Test with Google Rich Results Test and Schema Validator</p>
                </div>
              </div>
              <div className="flex gap-3">
                <div className="flex items-center justify-center w-6 h-6 rounded-full bg-primary/20 text-primary text-xs font-bold flex-shrink-0">
                  6
                </div>
                <div>
                  <p className="font-medium text-text-primary mb-1">Add to Page</p>
                  <p className="text-xs text-text-muted">Insert JSON-LD script in page &lt;head&gt; or &lt;body&gt;</p>
                </div>
              </div>
              <div className="pt-3 border-t border-white/10">
                <p className="text-xs font-medium text-text-secondary mb-2">Pro Tip:</p>
                <p className="text-xs text-text-muted">
                  Use JSON-LD format (not Microdata or RDFa) as it's easier to implement and maintain
                </p>
              </div>
            </div>
          </Card>
        </div>
      </main>
    </div>
  );
};

export default SchemaGeneratorPage;
