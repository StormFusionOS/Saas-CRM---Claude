/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * This file is part of the RiverCityClean SaaS CRM system.
 */

import React, { useState, useEffect } from 'react';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import Input from '../components/ui/Input';
import { useAuth } from '../lib/auth-context';

interface Service {
  id: number;
  name: string;
  description: string;
  category: string;
  base_price: number;
  unit: string;
  min_price?: number;
}

interface QuoteItem {
  service_id: number;
  service_name?: string;
  description?: string;
  quantity: number;
  unit_price: number;
  discount_percent?: number;
  tax_percent?: number;
  display_order?: number;
}

interface Quote {
  id: number;
  quote_number: string;
  lead_id: number;
  contact_id: number;
  title: string;
  status: string;
  subtotal: number;
  discount_amount: number;
  tax_amount: number;
  total: number;
  valid_until?: string;
  created_at: string;
}

interface Lead {
  id: number;
  source: string;
  status: string;
  contact: {
    id: number;
    first_name: string;
    last_name: string;
    email?: string;
    phone?: string;
  };
}

const QuotesInvoicesPage: React.FC = () => {
  const { token } = useAuth();
  const [quotes, setQuotes] = useState<Quote[]>([]);
  const [services, setServices] = useState<Service[]>([]);
  const [leads, setLeads] = useState<Lead[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const [showCreateForm, setShowCreateForm] = useState(false);

  // Form state
  const [selectedLead, setSelectedLead] = useState<number | null>(null);
  const [quoteTitle, setQuoteTitle] = useState('');
  const [quoteItems, setQuoteItems] = useState<QuoteItem[]>([]);
  const [submitting, setSubmitting] = useState(false);

  // Fetch data on mount
  useEffect(() => {
    fetchData();
  }, [token]);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError('');

      const [quotesRes, servicesRes, leadsRes] = await Promise.all([
        fetch('http://localhost:8000/api/v1/sales/quotes', {
          headers: { Authorization: `Bearer ${token}` },
        }),
        fetch('http://localhost:8000/api/v1/sales/services?is_active=true', {
          headers: { Authorization: `Bearer ${token}` },
        }),
        fetch('http://localhost:8000/api/v1/leads', {
          headers: { Authorization: `Bearer ${token}` },
        }),
      ]);

      if (!quotesRes.ok || !servicesRes.ok || !leadsRes.ok) {
        throw new Error('Failed to fetch data');
      }

      const quotesData = await quotesRes.json();
      const servicesData = await servicesRes.json();
      const leadsData = await leadsRes.json();

      setQuotes(quotesData);
      setServices(servicesData);

      // Extract leads from board structure
      const allLeads: Lead[] = [];
      if (leadsData.new) allLeads.push(...leadsData.new);
      if (leadsData.contacted) allLeads.push(...leadsData.contacted);
      if (leadsData.quoted) allLeads.push(...leadsData.quoted);
      setLeads(allLeads);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const addLineItem = () => {
    if (services.length === 0) return;
    const firstService = services[0];
    setQuoteItems([
      ...quoteItems,
      {
        service_id: firstService.id,
        service_name: firstService.name,
        description: firstService.description,
        quantity: 1,
        unit_price: firstService.base_price,
        discount_percent: 0,
        tax_percent: 0,
        display_order: quoteItems.length,
      },
    ]);
  };

  const removeLineItem = (index: number) => {
    setQuoteItems(quoteItems.filter((_, i) => i !== index));
  };

  const updateLineItem = (index: number, updates: Partial<QuoteItem>) => {
    const newItems = [...quoteItems];
    newItems[index] = { ...newItems[index], ...updates };

    // Update service details if service changed
    if (updates.service_id) {
      const service = services.find(s => s.id === updates.service_id);
      if (service) {
        newItems[index].service_name = service.name;
        newItems[index].description = service.description;
        newItems[index].unit_price = service.base_price;
      }
    }

    setQuoteItems(newItems);
  };

  const calculateTotal = () => {
    return quoteItems.reduce((sum, item) => {
      const subtotal = item.quantity * item.unit_price;
      const discount = subtotal * ((item.discount_percent || 0) / 100);
      const taxable = subtotal - discount;
      const tax = taxable * ((item.tax_percent || 0) / 100);
      return sum + (taxable + tax);
    }, 0);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!selectedLead || quoteItems.length === 0) {
      setError('Please select a lead and add at least one line item');
      return;
    }

    const lead = leads.find(l => l.id === selectedLead);
    if (!lead) {
      setError('Selected lead not found');
      return;
    }

    setSubmitting(true);
    setError('');

    try {
      const response = await fetch('http://localhost:8000/api/v1/sales/quotes', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          lead_id: lead.id,
          contact_id: lead.contact.id,
          title: quoteTitle || `Quote for ${lead.contact.first_name} ${lead.contact.last_name}`,
          items: quoteItems,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create quote');
      }

      // Success - reset form and refresh
      setShowCreateForm(false);
      setSelectedLead(null);
      setQuoteTitle('');
      setQuoteItems([]);
      await fetchData();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
            <p className="text-text-secondary">Loading quotes...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-bg-base">
      {/* Page Header */}
      <div className="p-8 pb-6 border-b border-white/5">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-3xl font-display font-bold text-gradient">Quotes & Invoices</h1>
            <p className="text-sm text-text-muted mt-1">
              Create and manage quotes for leads
            </p>
          </div>
          <Button
            onClick={() => setShowCreateForm(!showCreateForm)}
            variant={showCreateForm ? 'outline' : 'primary'}
          >
            {showCreateForm ? 'Cancel' : '+ New Quote'}
          </Button>
        </div>
      </div>

      {/* Main Content */}
      <main className="p-8">
        {error && (
          <div className="mb-6 p-4 bg-error/10 border border-error rounded-base text-error">
            {error}
          </div>
        )}

        {/* Create Quote Form */}
        {showCreateForm && (
          <Card className="mb-8">
            <h2 className="text-xl font-display font-semibold mb-6">Create New Quote</h2>
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Lead Selection */}
              <div>
                <label htmlFor="lead" className="block text-sm font-medium text-text-primary mb-2">
                  Select Lead <span className="text-error">*</span>
                </label>
                <select
                  id="lead"
                  value={selectedLead || ''}
                  onChange={(e) => setSelectedLead(Number(e.target.value))}
                  className="w-full px-4 py-2 bg-bg-elev text-text-primary border border-border-default rounded-base focus-ring"
                  required
                >
                  <option value="">Choose a lead...</option>
                  {leads.map((lead) => (
                    <option key={lead.id} value={lead.id}>
                      {lead.contact.first_name} {lead.contact.last_name}
                      {lead.contact.email && ` (${lead.contact.email})`}
                    </option>
                  ))}
                </select>
              </div>

              {/* Quote Title */}
              <Input
                id="title"
                label="Quote Title (Optional)"
                value={quoteTitle}
                onChange={(e) => setQuoteTitle(e.target.value)}
                placeholder="e.g., House Wash + Gutter Clean Package"
              />

              {/* Line Items */}
              <div>
                <div className="flex items-center justify-between mb-4">
                  <label className="text-sm font-medium text-text-primary">
                    Line Items <span className="text-error">*</span>
                  </label>
                  <Button type="button" size="sm" onClick={addLineItem}>
                    + Add Service
                  </Button>
                </div>

                {quoteItems.length === 0 ? (
                  <div className="p-8 text-center border border-border-default rounded-base bg-bg-hover">
                    <p className="text-text-muted">No line items yet. Click "Add Service" to get started.</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {quoteItems.map((item, index) => (
                      <div key={index} className="p-4 border border-border-default rounded-base bg-bg-hover">
                        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
                          <div className="md:col-span-2">
                            <label className="block text-xs text-text-muted mb-1">Service</label>
                            <select
                              value={item.service_id}
                              onChange={(e) => updateLineItem(index, { service_id: Number(e.target.value) })}
                              className="w-full px-3 py-2 text-sm bg-bg-elev text-text-primary border border-border-default rounded-base focus-ring"
                            >
                              {services.map((service) => (
                                <option key={service.id} value={service.id}>
                                  {service.name} (${service.base_price}/{service.unit})
                                </option>
                              ))}
                            </select>
                          </div>

                          <div>
                            <label className="block text-xs text-text-muted mb-1">Quantity</label>
                            <input
                              type="number"
                              min="0.01"
                              step="0.01"
                              value={item.quantity}
                              onChange={(e) => updateLineItem(index, { quantity: parseFloat(e.target.value) || 0 })}
                              className="w-full px-3 py-2 text-sm bg-bg-elev text-text-primary border border-border-default rounded-base focus-ring"
                            />
                          </div>

                          <div>
                            <label className="block text-xs text-text-muted mb-1">Unit Price</label>
                            <input
                              type="number"
                              min="0"
                              step="0.01"
                              value={item.unit_price}
                              onChange={(e) => updateLineItem(index, { unit_price: parseFloat(e.target.value) || 0 })}
                              className="w-full px-3 py-2 text-sm bg-bg-elev text-text-primary border border-border-default rounded-base focus-ring"
                            />
                          </div>

                          <div className="flex items-end">
                            <Button
                              type="button"
                              variant="ghost"
                              size="sm"
                              onClick={() => removeLineItem(index)}
                              className="text-error hover:bg-error/10 w-full"
                            >
                              Remove
                            </Button>
                          </div>
                        </div>

                        <div className="mt-2 flex items-center justify-between text-sm">
                          <span className="text-text-muted">
                            Subtotal: ${(item.quantity * item.unit_price).toFixed(2)}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Total Preview */}
              {quoteItems.length > 0 && (
                <div className="p-4 bg-primary/10 border border-primary rounded-base">
                  <div className="flex items-center justify-between">
                    <span className="text-lg font-semibold text-text-primary">Total</span>
                    <span className="text-2xl font-bold text-primary">
                      ${calculateTotal().toFixed(2)}
                    </span>
                  </div>
                </div>
              )}

              {/* Actions */}
              <div className="flex gap-3 pt-4">
                <Button type="submit" disabled={submitting || quoteItems.length === 0}>
                  {submitting ? 'Creating...' : 'Create Quote'}
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => {
                    setShowCreateForm(false);
                    setError('');
                  }}
                >
                  Cancel
                </Button>
              </div>
            </form>
          </Card>
        )}

        {/* Quotes List */}
        <Card>
          <div className="p-6 border-b border-white/10">
            <h2 className="text-xl font-semibold text-text-primary">All Quotes</h2>
          </div>

          {quotes.length === 0 ? (
            <div className="p-12 text-center">
              <div className="text-6xl mb-4">📄</div>
              <h3 className="text-xl font-display font-semibold mb-2">No Quotes Yet</h3>
              <p className="text-text-muted mb-6">
                Create your first quote to get started with the quoting engine.
              </p>
              <Button onClick={() => setShowCreateForm(true)}>+ Create First Quote</Button>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-white/5">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-text-muted uppercase">Quote #</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-text-muted uppercase">Title</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-text-muted uppercase">Status</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-text-muted uppercase">Total</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-text-muted uppercase">Created</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5">
                  {quotes.map((quote) => (
                    <tr key={quote.id} className="hover:bg-white/5 transition-colors">
                      <td className="px-6 py-4 text-sm font-medium text-primary">{quote.quote_number}</td>
                      <td className="px-6 py-4 text-sm text-text-primary">{quote.title}</td>
                      <td className="px-6 py-4 text-sm">
                        <span className={`px-2 py-1 text-xs rounded-full ${
                          quote.status === 'ACCEPTED' ? 'bg-success/10 text-success' :
                          quote.status === 'SENT' ? 'bg-warning/10 text-warning' :
                          'bg-text-muted/10 text-text-muted'
                        }`}>
                          {quote.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm font-semibold text-text-primary">
                        ${quote.total.toFixed(2)}
                      </td>
                      <td className="px-6 py-4 text-sm text-text-secondary">
                        {new Date(quote.created_at).toLocaleDateString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Card>
      </main>
    </div>
  );
};

export default QuotesInvoicesPage;
