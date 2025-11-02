/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 */

import React, { useState } from 'react';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';

const CalendarPage: React.FC = () => {
  const [isLoading] = useState(false);

  const upcomingEvents = [
    { id: 1, title: 'Team Meeting', time: '10:00 AM', date: 'Today', type: 'meeting' },
    { id: 2, title: 'Client Call - Acme Corp', time: '2:00 PM', date: 'Today', type: 'call' },
    { id: 3, title: 'Quote Follow-up', time: '9:00 AM', date: 'Tomorrow', type: 'task' },
  ];

  if (isLoading) {
    return (
      <div className="p-6 flex items-center justify-center h-64">
        <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-display font-bold text-gradient">Calendar</h1>
          <p className="text-text-secondary mt-1">Manage your schedule and events</p>
        </div>
        <Button variant="primary" size="lg">+ New Event</Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: 'Today\'s Events', value: '3', icon: '📅' },
          { label: 'This Week', value: '12', icon: '📆' },
          { label: 'Pending', value: '5', icon: '⏰' },
          { label: 'Completed', value: '28', icon: '✅' },
        ].map((kpi, i) => (
          <Card key={i} variant="glass" padding="md" hover>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-text-muted text-sm">{kpi.label}</p>
                <p className="text-2xl font-bold text-text-primary mt-1">{kpi.value}</p>
              </div>
              <div className="text-3xl">{kpi.icon}</div>
            </div>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <Card variant="glass" padding="lg">
            <div className="text-center py-12">
              <div className="text-6xl mb-4">📅</div>
              <h2 className="text-xl font-semibold text-text-primary mb-2">Calendar View</h2>
              <p className="text-text-secondary mb-6">Full calendar integration coming soon</p>
            </div>
          </Card>
        </div>

        <div>
          <Card variant="glass" padding="lg">
            <h2 className="text-xl font-semibold text-text-primary mb-4">Upcoming Events</h2>
            <div className="space-y-3">
              {upcomingEvents.map((event) => (
                <div
                  key={event.id}
                  className="p-3 rounded-lg bg-white/5 hover:bg-white/10 transition-colors cursor-pointer border border-white/10"
                >
                  <p className="font-medium text-text-primary">{event.title}</p>
                  <p className="text-sm text-text-secondary mt-1">
                    {event.date} at {event.time}
                  </p>
                </div>
              ))}
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default CalendarPage;
