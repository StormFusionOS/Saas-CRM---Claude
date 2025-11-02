/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * This file is part of the RiverCityClean SaaS CRM system.
 */

import React, { useState, useEffect } from 'react';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';

const SettingsPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState('general');
  const [requireDeposit, setRequireDeposit] = useState(() => {
    return localStorage.getItem('requireDeposit') === 'true';
  });
  const [enableAutomation, setEnableAutomation] = useState(() => {
    return localStorage.getItem('enableAutomation') === 'true';
  });
  const [showHealthInHeader, setShowHealthInHeader] = useState(() => {
    return localStorage.getItem('showHealthInHeader') === 'true';
  });

  useEffect(() => {
    localStorage.setItem('requireDeposit', requireDeposit.toString());
  }, [requireDeposit]);

  useEffect(() => {
    localStorage.setItem('enableAutomation', enableAutomation.toString());
  }, [enableAutomation]);

  useEffect(() => {
    localStorage.setItem('showHealthInHeader', showHealthInHeader.toString());
    // Dispatch event to notify Shell component
    window.dispatchEvent(new Event('settingsChanged'));
  }, [showHealthInHeader]);

  const tabs = [
    { id: 'general', label: 'General', icon: '⚙️' },
    { id: 'business', label: 'Business Rules', icon: '📋' },
    { id: 'account', label: 'Account', icon: '👤' },
    { id: 'notifications', label: 'Notifications', icon: '🔔' },
    { id: 'security', label: 'Security', icon: '🔒' },
    { id: 'integrations', label: 'Integrations', icon: '🔗' },
  ];

  const Toggle: React.FC<{ enabled: boolean; onToggle: () => void }> = ({ enabled, onToggle }) => (
    <button
      onClick={onToggle}
      className={`w-12 h-6 rounded-full relative transition-colors ${
        enabled ? 'bg-success' : 'bg-white/20'
      }`}
    >
      <div
        className={`w-5 h-5 bg-white rounded-full absolute top-0.5 transition-transform ${
          enabled ? 'translate-x-6' : 'translate-x-0.5'
        }`}
      ></div>
    </button>
  );

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-display font-bold text-gradient">Settings</h1>
        <p className="text-text-secondary mt-1">Manage your account and application preferences</p>
      </div>

      <div className="flex gap-2 border-b border-white/10 overflow-x-auto">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors whitespace-nowrap ${
              activeTab === tab.id
                ? 'border-primary text-primary'
                : 'border-transparent text-text-secondary hover:text-text-primary'
            }`}
          >
            <span>{tab.icon}</span>
            {tab.label}
          </button>
        ))}
      </div>

      {activeTab === 'general' && (
        <div className="space-y-6">
          <Card variant="glass" padding="lg">
            <h2 className="text-xl font-semibold text-text-primary mb-4">General Settings</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-text-primary mb-2">Company Name</label>
                <input
                  type="text"
                  defaultValue="StormFusion OS"
                  className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-text-primary focus:outline-none focus:ring-2 focus:ring-primary/50"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-text-primary mb-2">Time Zone</label>
                <select className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-text-primary focus:outline-none focus:ring-2 focus:ring-primary/50">
                  <option>UTC-05:00 Eastern Time</option>
                  <option>UTC-06:00 Central Time</option>
                  <option>UTC-07:00 Mountain Time</option>
                  <option>UTC-08:00 Pacific Time</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-text-primary mb-2">Language</label>
                <select className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-text-primary focus:outline-none focus:ring-2 focus:ring-primary/50">
                  <option>English (US)</option>
                  <option>English (UK)</option>
                  <option>Spanish</option>
                  <option>French</option>
                </select>
              </div>
            </div>
            <div className="mt-6 flex justify-end gap-3">
              <Button variant="secondary">Cancel</Button>
              <Button variant="primary">Save Changes</Button>
            </div>
          </Card>
        </div>
      )}

      {activeTab === 'business' && (
        <Card variant="glass" padding="lg">
          <h2 className="text-xl font-semibold text-text-primary mb-4">Business Rules & Automation</h2>
          <p className="text-sm text-text-secondary mb-6">
            Configure business rules and automation settings for your CRM workflow
          </p>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 rounded-lg bg-white/5 border border-white/10">
              <div>
                <p className="font-medium text-text-primary">Require Deposit on Acceptance</p>
                <p className="text-sm text-text-muted mt-1">
                  Customers must pay a deposit before accepting a quote
                </p>
              </div>
              <Toggle enabled={requireDeposit} onToggle={() => setRequireDeposit(!requireDeposit)} />
            </div>

            <div className="flex items-center justify-between p-4 rounded-lg bg-white/5 border border-white/10">
              <div>
                <p className="font-medium text-text-primary">Enable Follow-up Automation</p>
                <p className="text-sm text-text-muted mt-1">
                  Automatically send follow-up emails to leads based on their stage
                </p>
              </div>
              <Toggle enabled={enableAutomation} onToggle={() => setEnableAutomation(!enableAutomation)} />
            </div>

            <div className="flex items-center justify-between p-4 rounded-lg bg-white/5 border border-white/10">
              <div>
                <p className="font-medium text-text-primary">Show Health in Header</p>
                <p className="text-sm text-text-muted mt-1">
                  Display a system health indicator in the navigation header
                </p>
              </div>
              <Toggle enabled={showHealthInHeader} onToggle={() => setShowHealthInHeader(!showHealthInHeader)} />
            </div>
          </div>

          <div className="mt-6 p-4 bg-primary/10 border border-primary/30 rounded-lg">
            <p className="text-sm text-text-secondary">
              💡 <strong className="text-primary">Tip:</strong> These settings are saved automatically and apply immediately.
            </p>
          </div>
        </Card>
      )}

      {activeTab === 'account' && (
        <Card variant="glass" padding="lg">
          <h2 className="text-xl font-semibold text-text-primary mb-4">Account Information</h2>
          <div className="space-y-4">
            <div className="flex items-center gap-4">
              <div className="w-20 h-20 rounded-full bg-primary/20 flex items-center justify-center text-3xl">
                👤
              </div>
              <div>
                <Button variant="secondary" size="sm">Change Avatar</Button>
                <p className="text-xs text-text-muted mt-1">JPG, PNG or GIF. Max size 2MB.</p>
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-text-primary mb-2">Full Name</label>
              <input
                type="text"
                defaultValue="User"
                className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-text-primary focus:outline-none focus:ring-2 focus:ring-primary/50"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-text-primary mb-2">Email</label>
              <input
                type="email"
                defaultValue="user@example.com"
                className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-text-primary focus:outline-none focus:ring-2 focus:ring-primary/50"
              />
            </div>
          </div>
          <div className="mt-6 flex justify-end gap-3">
            <Button variant="secondary">Cancel</Button>
            <Button variant="primary">Save Changes</Button>
          </div>
        </Card>
      )}

      {activeTab === 'notifications' && (
        <Card variant="glass" padding="lg">
          <h2 className="text-xl font-semibold text-text-primary mb-4">Notification Preferences</h2>
          <div className="space-y-4">
            {[
              { label: 'Email Notifications', desc: 'Receive email alerts for important events' },
              { label: 'Push Notifications', desc: 'Get push notifications on your device' },
              { label: 'Lead Assignments', desc: 'Notify when leads are assigned to you' },
              { label: 'Quote Updates', desc: 'Updates on quote status changes' },
            ].map((item, i) => (
              <div key={i} className="flex items-center justify-between p-4 rounded-lg bg-white/5 border border-white/10">
                <div>
                  <p className="font-medium text-text-primary">{item.label}</p>
                  <p className="text-sm text-text-muted mt-1">{item.desc}</p>
                </div>
                <button className="w-12 h-6 bg-primary rounded-full relative">
                  <div className="w-5 h-5 bg-white rounded-full absolute right-0.5 top-0.5"></div>
                </button>
              </div>
            ))}
          </div>
        </Card>
      )}

      {activeTab === 'security' && (
        <Card variant="glass" padding="lg">
          <h2 className="text-xl font-semibold text-text-primary mb-4">Security Settings</h2>
          <div className="space-y-6">
            <div>
              <h3 className="font-medium text-text-primary mb-2">Change Password</h3>
              <div className="space-y-3">
                <input
                  type="password"
                  placeholder="Current password"
                  className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-text-primary focus:outline-none focus:ring-2 focus:ring-primary/50"
                />
                <input
                  type="password"
                  placeholder="New password"
                  className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-text-primary focus:outline-none focus:ring-2 focus:ring-primary/50"
                />
                <input
                  type="password"
                  placeholder="Confirm new password"
                  className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-text-primary focus:outline-none focus:ring-2 focus:ring-primary/50"
                />
              </div>
              <Button variant="primary" size="sm" className="mt-3">Update Password</Button>
            </div>
            <div className="border-t border-white/10 pt-6">
              <h3 className="font-medium text-text-primary mb-2">Two-Factor Authentication</h3>
              <p className="text-sm text-text-secondary mb-4">Add an extra layer of security to your account</p>
              <Button variant="secondary">Enable 2FA</Button>
            </div>
          </div>
        </Card>
      )}

      {activeTab === 'integrations' && (
        <Card variant="glass" padding="lg">
          <h2 className="text-xl font-semibold text-text-primary mb-4">Connected Integrations</h2>
          <div className="space-y-4">
            {[
              { name: 'Google Calendar', status: 'connected', icon: '📅' },
              { name: 'Slack', status: 'disconnected', icon: '💬' },
              { name: 'Stripe', status: 'connected', icon: '💳' },
              { name: 'Mailchimp', status: 'disconnected', icon: '📧' },
            ].map((integration, i) => (
              <div key={i} className="flex items-center justify-between p-4 rounded-lg bg-white/5 border border-white/10">
                <div className="flex items-center gap-3">
                  <span className="text-2xl">{integration.icon}</span>
                  <div>
                    <p className="font-medium text-text-primary">{integration.name}</p>
                    <p className={`text-sm ${integration.status === 'connected' ? 'text-success' : 'text-text-muted'}`}>
                      {integration.status}
                    </p>
                  </div>
                </div>
                <Button variant={integration.status === 'connected' ? 'secondary' : 'primary'} size="sm">
                  {integration.status === 'connected' ? 'Disconnect' : 'Connect'}
                </Button>
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
};

export default SettingsPage;
