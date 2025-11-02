/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * This file is part of the RiverCityClean SaaS CRM system.
 */

import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { leadsAPI, pricebookAPI, estimatesAPI } from '../lib/api';
import Card from '../components/ui/Card';

interface PricebookItem {
  id: number;
  name: string;
  description: string;
  unit: string;
  base_price: number;
  formula: string;
  category: string;
  is_active: boolean;
}

interface Tier {
  name: string;
  price: number;
  items: Array<{
    id: number;
    name: string;
    description: string;
    price: number;
  }>;
  features: string[];
}

interface Quote {
  id: number;
  lead_id: number;
  contact_id: number;
  good_tier: Tier;
  better_tier: Tier;
  best_tier: Tier;
  status: string;
}

interface Lead {
  id: number;
  contact_id: number;
  contact: {
    id: number;
    first_name: string;
    last_name: string;
    email?: string;
    phone?: string;
  };
  status: string;
}

function EstimatorPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const leadId = searchParams.get('lead');

  const [lead, setLead] = useState<Lead | null>(null);
  const [pricebookItems, setPricebookItems] = useState<PricebookItem[]>([]);
  const [selectedServices, setSelectedServices] = useState<number[]>([]);
  const [inputs, setInputs] = useState<Record<string, number>>({
    sq_ft: 2500,
    stories: 2,
    linear_ft: 150,
    window_count: 20,
    pitch_difficulty: 1,
  });
  const [quote, setQuote] = useState<Quote | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [acceptingTier, setAcceptingTier] = useState<string | null>(null);

  // Load lead and pricebook items
  useEffect(() => {
    const loadData = async () => {
      if (!leadId) {
        setError('No lead ID provided');
        return;
      }

      try {
        setLoading(true);
        const [leadData, pricebook] = await Promise.all([
          leadsAPI.getLead(parseInt(leadId)),
          pricebookAPI.getPricebookItems(),
        ]);
        setLead(leadData);
        setPricebookItems(pricebook);
      } catch (err: any) {
        console.error('Error loading data:', err);
        setError(err.response?.data?.detail || 'Failed to load data');
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [leadId]);

  // Auto-generate quote when services and inputs change
  useEffect(() => {
    if (selectedServices.length === 0) {
      setQuote(null);
      return;
    }

    const generateQuote = async () => {
      try {
        const quoteData = await estimatesAPI.createQuote({
          lead_id: parseInt(leadId!),
          service_ids: selectedServices,
          inputs,
        });
        setQuote(quoteData);
        setError(null);
      } catch (err: any) {
        console.error('Error generating quote:', err);
        setError(err.response?.data?.detail || 'Failed to generate quote');
      }
    };

    const debounce = setTimeout(generateQuote, 500);
    return () => clearTimeout(debounce);
  }, [selectedServices, inputs, leadId]);

  const handleServiceToggle = (serviceId: number) => {
    setSelectedServices((prev) =>
      prev.includes(serviceId)
        ? prev.filter((id) => id !== serviceId)
        : [...prev, serviceId]
    );
  };

  const handleInputChange = (key: string, value: string) => {
    const numValue = parseFloat(value) || 0;
    setInputs((prev) => ({ ...prev, [key]: numValue }));
  };

  const handleAcceptTier = async (tier: 'good' | 'better' | 'best') => {
    if (!quote) return;

    setAcceptingTier(tier);
    try {
      const job = await estimatesAPI.acceptEstimate(quote.id, tier);

      // Show success message and navigate back to leads
      alert(
        `🎉 Job Created!\n\n` +
        `Job ID: ${job.job_id}\n` +
        `Total: $${job.total_price.toFixed(2)}\n` +
        `Deposit: $${job.deposit_amount.toFixed(2)}\n` +
        `Due: ${new Date(job.deposit_due).toLocaleDateString()}\n\n` +
        `The lead has been marked as Won!`
      );

      navigate('/leads');
    } catch (err: any) {
      console.error('Error accepting estimate:', err);
      setError(err.response?.data?.detail || 'Failed to accept estimate');
    } finally {
      setAcceptingTier(null);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-text-secondary">Loading estimator...</p>
        </div>
      </div>
    );
  }

  if (error && !lead) {
    return (
      <div className="flex items-center justify-center h-screen">
        <Card className="max-w-md p-6 text-center">
          <p className="text-red-400 mb-4">{error}</p>
          <button
            onClick={() => navigate('/leads')}
            className="px-4 py-2 bg-bg-elevated border border-white/10 rounded-lg hover:bg-white/5"
          >
            Back to Leads
          </button>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-bg-primary">
      {/* Header */}
      <div className="bg-bg-elevated border-b border-white/10 px-6 py-4">
        <div className="flex items-center justify-between max-w-7xl mx-auto">
          <div>
            <button
              onClick={() => navigate('/leads')}
              className="text-text-secondary hover:text-text-primary mb-2 text-sm flex items-center gap-2"
            >
              ← Back to Leads
            </button>
            <h1 className="text-2xl font-bold text-text-primary">
              Estimate Generator
            </h1>
            {lead && (
              <p className="text-text-secondary text-sm mt-1">
                For: {lead.contact.first_name} {lead.contact.last_name}
                {lead.contact.email && ` • ${lead.contact.email}`}
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Two-column layout */}
      <div className="max-w-7xl mx-auto px-6 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left: Questionnaire */}
          <div className="space-y-6">
            {/* Service Selection */}
            <Card className="p-6">
              <h2 className="text-lg font-semibold text-text-primary mb-4">
                1. Select Services
              </h2>
              <div className="space-y-3">
                {pricebookItems.map((item) => (
                  <label
                    key={item.id}
                    className="flex items-start gap-3 p-3 rounded-lg border border-white/10 hover:bg-white/5 cursor-pointer"
                  >
                    <input
                      type="checkbox"
                      checked={selectedServices.includes(item.id)}
                      onChange={() => handleServiceToggle(item.id)}
                      className="mt-1"
                    />
                    <div className="flex-1">
                      <div className="flex items-baseline justify-between">
                        <span className="font-medium text-text-primary">
                          {item.name}
                        </span>
                        <span className="text-sm text-text-secondary">
                          ${item.base_price.toFixed(2)}/{item.unit}
                        </span>
                      </div>
                      <p className="text-sm text-text-secondary mt-1">
                        {item.description}
                      </p>
                    </div>
                  </label>
                ))}
              </div>
            </Card>

            {/* Input Form */}
            {selectedServices.length > 0 && (
              <Card className="p-6">
                <h2 className="text-lg font-semibold text-text-primary mb-4">
                  2. Property Details
                </h2>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-text-primary mb-2">
                      Square Footage
                    </label>
                    <input
                      type="number"
                      value={inputs.sq_ft}
                      onChange={(e) => handleInputChange('sq_ft', e.target.value)}
                      className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-text-primary focus:outline-none focus:border-primary"
                      min="0"
                      step="100"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-text-primary mb-2">
                      Number of Stories
                    </label>
                    <input
                      type="number"
                      value={inputs.stories}
                      onChange={(e) => handleInputChange('stories', e.target.value)}
                      className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-text-primary focus:outline-none focus:border-primary"
                      min="1"
                      max="5"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-text-primary mb-2">
                      Linear Feet (Gutters)
                    </label>
                    <input
                      type="number"
                      value={inputs.linear_ft}
                      onChange={(e) => handleInputChange('linear_ft', e.target.value)}
                      className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-text-primary focus:outline-none focus:border-primary"
                      min="0"
                      step="10"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-text-primary mb-2">
                      Window Count
                    </label>
                    <input
                      type="number"
                      value={inputs.window_count}
                      onChange={(e) => handleInputChange('window_count', e.target.value)}
                      className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-text-primary focus:outline-none focus:border-primary"
                      min="0"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-text-primary mb-2">
                      Roof Pitch Difficulty (1-5)
                    </label>
                    <input
                      type="number"
                      value={inputs.pitch_difficulty}
                      onChange={(e) => handleInputChange('pitch_difficulty', e.target.value)}
                      className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-text-primary focus:outline-none focus:border-primary"
                      min="1"
                      max="5"
                    />
                    <p className="text-xs text-text-secondary mt-1">
                      1 = Low pitch, 5 = Very steep
                    </p>
                  </div>
                </div>
              </Card>
            )}
          </div>

          {/* Right: Tier Cards */}
          <div>
            {!quote && selectedServices.length === 0 && (
              <Card className="p-12 text-center">
                <div className="text-6xl mb-4">📋</div>
                <h3 className="text-lg font-semibold text-text-primary mb-2">
                  Select Services to Begin
                </h3>
                <p className="text-text-secondary">
                  Choose one or more services from the left panel to generate pricing tiers
                </p>
              </Card>
            )}

            {selectedServices.length > 0 && !quote && (
              <Card className="p-12 text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
                <p className="text-text-secondary">Generating quote...</p>
              </Card>
            )}

            {error && quote === null && selectedServices.length > 0 && (
              <Card className="p-6 border-red-500/50 bg-red-500/10">
                <p className="text-red-400">{error}</p>
              </Card>
            )}

            {quote && (
              <div className="space-y-4">
                <h2 className="text-lg font-semibold text-text-primary">
                  3. Choose Your Package
                </h2>

                {/* Good Tier */}
                <TierCard
                  tier={quote.good_tier}
                  tierKey="good"
                  isAccepting={acceptingTier === 'good'}
                  onAccept={() => handleAcceptTier('good')}
                  highlight={false}
                />

                {/* Better Tier */}
                <TierCard
                  tier={quote.better_tier}
                  tierKey="better"
                  isAccepting={acceptingTier === 'better'}
                  onAccept={() => handleAcceptTier('better')}
                  highlight={true}
                />

                {/* Best Tier */}
                <TierCard
                  tier={quote.best_tier}
                  tierKey="best"
                  isAccepting={acceptingTier === 'best'}
                  onAccept={() => handleAcceptTier('best')}
                  highlight={false}
                />
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

interface TierCardProps {
  tier: Tier;
  tierKey: string;
  isAccepting: boolean;
  onAccept: () => void;
  highlight: boolean;
}

function TierCard({ tier, tierKey, isAccepting, onAccept, highlight }: TierCardProps) {
  const depositAmount = (tier.price * 0.25).toFixed(2);

  return (
    <Card
      className={`p-6 relative ${
        highlight
          ? 'border-primary border-2 shadow-lg shadow-primary/20'
          : 'border-white/10'
      }`}
    >
      {highlight && (
        <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
          <span className="px-3 py-1 bg-primary text-white text-xs font-bold rounded-full">
            RECOMMENDED
          </span>
        </div>
      )}

      <div className="mb-4">
        <h3 className="text-xl font-bold text-text-primary mb-1">{tier.name}</h3>
        <div className="flex items-baseline gap-2">
          <span className="text-3xl font-bold text-primary">
            ${tier.price.toFixed(2)}
          </span>
          <span className="text-text-secondary text-sm">total</span>
        </div>
        <p className="text-text-secondary text-sm mt-1">
          ${depositAmount} deposit (25%)
        </p>
      </div>

      {/* Services */}
      <div className="mb-4 pb-4 border-b border-white/10">
        <p className="text-sm font-semibold text-text-primary mb-2">
          Services Included:
        </p>
        <ul className="space-y-1">
          {tier.items.map((item) => (
            <li
              key={item.id}
              className="text-sm text-text-secondary flex justify-between"
            >
              <span>{item.name}</span>
              <span className="text-text-primary">${item.price.toFixed(2)}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Features */}
      <div className="mb-4">
        <p className="text-sm font-semibold text-text-primary mb-2">Features:</p>
        <ul className="space-y-2">
          {tier.features.map((feature, idx) => (
            <li key={idx} className="text-sm text-text-secondary flex items-start gap-2">
              <span className="text-primary mt-0.5">✓</span>
              <span>{feature}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Accept Button */}
      <button
        onClick={onAccept}
        disabled={isAccepting}
        className={`w-full py-3 rounded-lg font-semibold transition-colors ${
          highlight
            ? 'bg-primary text-white hover:bg-primary/90'
            : 'bg-bg-elevated border border-white/10 text-text-primary hover:bg-white/5'
        } disabled:opacity-50 disabled:cursor-not-allowed`}
      >
        {isAccepting ? (
          <span className="flex items-center justify-center gap-2">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
            Processing...
          </span>
        ) : (
          `Accept & Collect Deposit`
        )}
      </button>
    </Card>
  );
}

export default EstimatorPage;
