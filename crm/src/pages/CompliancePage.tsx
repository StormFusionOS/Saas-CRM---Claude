/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * This file is part of the RiverCityClean SaaS CRM system.
 */

import React, { useState, useEffect } from 'react';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import { useAuth } from '../lib/auth-context';

interface GDPRRequest {
  id: number;
  contact_id: number;
  request_type: string;
  status: string;
  requested_at: string;
  completed_at?: string;
  completed_by?: number;
  notes?: string;
  created_at: string;
  updated_at: string;
}

const CompliancePage: React.FC = () => {
  const { token } = useAuth();
  const [requests, setRequests] = useState<GDPRRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>('all');
  const [error, setError] = useState<string>('');

  // Load GDPR requests
  useEffect(() => {
    fetchRequests();
  }, [filter]);

  const fetchRequests = async () => {
    setLoading(true);
    setError('');

    try {
      const url =
        filter === 'all'
          ? 'http://localhost:8000/api/v1/gdpr-request'
          : `http://localhost:8000/api/v1/gdpr-request?status=${filter}`;

      const response = await fetch(url, {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (response.ok) {
        const data = await response.json();
        setRequests(data);
      } else {
        setError('Failed to load GDPR requests');
      }
    } catch (err) {
      console.error('Error fetching GDPR requests:', err);
      setError('Error loading requests');
    } finally {
      setLoading(false);
    }
  };

  const updateRequestStatus = async (requestId: number, newStatus: string) => {
    try {
      const response = await fetch(
        `http://localhost:8000/api/v1/gdpr-request/${requestId}`,
        {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({ status: newStatus }),
        }
      );

      if (response.ok) {
        fetchRequests();
      } else {
        setError('Failed to update request status');
      }
    } catch (err) {
      console.error('Error updating request:', err);
      setError('Error updating request');
    }
  };

  const getRequestTypeBadge = (type: string) => {
    const badges: Record<string, string> = {
      access: 'bg-info/10 text-info border-info/30',
      deletion: 'bg-error/10 text-error border-error/30',
      portability: 'bg-accent/10 text-accent border-accent/30',
      rectification: 'bg-warning/10 text-warning border-warning/30',
      restriction: 'bg-text-muted/10 text-text-muted border-text-muted/30',
    };

    return badges[type] || badges.access;
  };

  const getStatusBadge = (status: string) => {
    const badges: Record<string, string> = {
      pending: 'bg-warning/10 text-warning border-warning/30',
      in_progress: 'bg-info/10 text-info border-info/30',
      completed: 'bg-success/10 text-success border-success/30',
      rejected: 'bg-error/10 text-error border-error/30',
    };

    return badges[status] || badges.pending;
  };

  const filteredRequests = requests;

  return (
    <div className="min-h-screen bg-bg-base">
      {/* Page Header */}
      <div className="p-8 pb-6 border-b border-white/5">
        <div>
          <h1 className="text-3xl font-display font-bold text-gradient">
            GDPR Compliance & Data Management
          </h1>
          <p className="text-sm text-text-muted mt-1">
            Manage data subject requests and ensure compliance with privacy regulations
          </p>
        </div>
      </div>

      {/* Main Content */}
      <main className="p-8">
        {error && (
          <div className="mb-6 p-4 bg-error/10 border border-error rounded-base text-error">
            {error}
          </div>
        )}

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card animate="scale-in" className="delay-0">
            <div>
              <p className="text-sm text-text-muted">Pending Requests</p>
              <p className="text-3xl font-bold text-warning mt-1">
                {requests.filter((r) => r.status === 'pending').length}
              </p>
            </div>
          </Card>

          <Card animate="scale-in" className="delay-100">
            <div>
              <p className="text-sm text-text-muted">In Progress</p>
              <p className="text-3xl font-bold text-info mt-1">
                {requests.filter((r) => r.status === 'in_progress').length}
              </p>
            </div>
          </Card>

          <Card animate="scale-in" className="delay-200">
            <div>
              <p className="text-sm text-text-muted">Completed</p>
              <p className="text-3xl font-bold text-success mt-1">
                {requests.filter((r) => r.status === 'completed').length}
              </p>
            </div>
          </Card>

          <Card animate="scale-in" className="delay-300">
            <div>
              <p className="text-sm text-text-muted">Total Requests</p>
              <p className="text-3xl font-bold text-text-primary mt-1">{requests.length}</p>
            </div>
          </Card>
        </div>

        {/* Filters */}
        <Card animate="slide-in-up" className="mb-6">
          <div className="flex items-center gap-4">
            <span className="text-sm font-medium text-text-primary">Filter by status:</span>
            <div className="flex gap-2">
              {['all', 'pending', 'in_progress', 'completed', 'rejected'].map((status) => (
                <button
                  key={status}
                  onClick={() => setFilter(status)}
                  className={`px-4 py-2 rounded-base text-sm font-medium transition-all ${
                    filter === status
                      ? 'bg-primary text-text-inverse'
                      : 'bg-bg-hover text-text-secondary hover:bg-bg-active'
                  }`}
                >
                  {status.charAt(0).toUpperCase() + status.slice(1).replace('_', ' ')}
                </button>
              ))}
            </div>
          </div>
        </Card>

        {/* Requests List */}
        <Card animate="fade-in">
          <h2 className="text-xl font-display font-semibold mb-4">GDPR Requests</h2>

          {loading ? (
            <div className="text-center py-12">
              <div className="inline-block w-8 h-8 border-4 border-border-default border-t-primary rounded-full animate-spin-slow" />
              <p className="text-sm text-text-muted mt-4">Loading requests...</p>
            </div>
          ) : filteredRequests.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-text-muted">No requests found</p>
            </div>
          ) : (
            <div className="space-y-4">
              {filteredRequests.map((request) => (
                <div
                  key={request.id}
                  className="p-4 bg-bg-hover border border-border-default rounded-base hover:border-border-strong transition-colors"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3">
                        <span
                          className={`px-3 py-1 text-xs font-medium border rounded-full ${getRequestTypeBadge(
                            request.request_type
                          )}`}
                        >
                          {request.request_type.toUpperCase()}
                        </span>
                        <span
                          className={`px-3 py-1 text-xs font-medium border rounded-full ${getStatusBadge(
                            request.status
                          )}`}
                        >
                          {request.status.replace('_', ' ').toUpperCase()}
                        </span>
                      </div>

                      <div className="mt-3 space-y-1">
                        <p className="text-sm text-text-primary">
                          <span className="font-medium">Contact ID:</span> {request.contact_id}
                        </p>
                        <p className="text-sm text-text-secondary">
                          <span className="font-medium">Requested:</span>{' '}
                          {new Date(request.requested_at).toLocaleString()}
                        </p>
                        {request.notes && (
                          <p className="text-sm text-text-secondary">
                            <span className="font-medium">Notes:</span> {request.notes}
                          </p>
                        )}
                      </div>
                    </div>

                    <div className="flex gap-2">
                      {request.status === 'pending' && (
                        <Button
                          size="sm"
                          variant="primary"
                          onClick={() => updateRequestStatus(request.id, 'in_progress')}
                        >
                          Start Processing
                        </Button>
                      )}
                      {request.status === 'in_progress' && (
                        <>
                          <Button
                            size="sm"
                            variant="primary"
                            onClick={() => updateRequestStatus(request.id, 'completed')}
                          >
                            Mark Complete
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => updateRequestStatus(request.id, 'rejected')}
                          >
                            Reject
                          </Button>
                        </>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </Card>

        {/* Information Card */}
        <Card animate="slide-in-up" className="mt-6">
          <h3 className="text-lg font-display font-semibold mb-4">
            GDPR Compliance Information
          </h3>

          <div className="space-y-4 text-sm text-text-secondary">
            <div>
              <h4 className="font-medium text-text-primary mb-2">Request Types</h4>
              <ul className="space-y-1 ml-4">
                <li>
                  <strong>Access:</strong> Provide a copy of all personal data
                </li>
                <li>
                  <strong>Deletion:</strong> Delete all personal data (right to be forgotten)
                </li>
                <li>
                  <strong>Portability:</strong> Export data in a machine-readable format
                </li>
                <li>
                  <strong>Rectification:</strong> Correct inaccurate personal data
                </li>
                <li>
                  <strong>Restriction:</strong> Limit processing of personal data
                </li>
              </ul>
            </div>

            <div>
              <h4 className="font-medium text-text-primary mb-2">Compliance Timeline</h4>
              <p>
                All GDPR requests must be fulfilled within <strong>30 days</strong> of receipt,
                as required by GDPR Article 12(3).
              </p>
            </div>

            <div className="p-3 bg-warning/10 border border-warning/30 rounded-base text-warning">
              <p className="font-medium">Important</p>
              <p className="text-sm mt-1">
                Deletion requests are irreversible. Always verify identity and backup data before
                executing deletions.
              </p>
            </div>
          </div>
        </Card>
      </main>
    </div>
  );
};

export default CompliancePage;
