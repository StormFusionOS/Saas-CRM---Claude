/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * This file is part of the RiverCityClean SaaS CRM system.
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  DndContext,
  DragEndEvent,
  DragOverlay,
  DragStartEvent,
  PointerSensor,
  useSensor,
  useSensors,
  closestCorners,
} from '@dnd-kit/core';
import { SortableContext, verticalListSortingStrategy } from '@dnd-kit/sortable';
import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import Card from '../components/ui/Card';
import { leadsAPI } from '../lib/api';
import { useAuth } from '../lib/auth-context';

interface Contact {
  id: number;
  first_name?: string;
  last_name?: string;
  company?: string;
  email?: string;
  phone?: string;
  title?: string;
}

interface Lead {
  id: number;
  status: string;
  value?: number;
  source?: string;
  probability?: number;
  created_at: string;
  updated_at?: string;
  notes?: string;
  assigned_to_id?: number | null;
  contact_id: number;
  contact: Contact;
}

interface LeadBoard {
  new: Lead[];
  contacted: Lead[];
  quoted: Lead[];
  scheduled: Lead[];
  won: Lead[];
  lost: Lead[];
}

type LeadStatus = 'NEW' | 'CONTACTED' | 'QUOTED' | 'SCHEDULED' | 'WON' | 'LOST';

const COLUMN_CONFIG: Record<LeadStatus, { title: string; color: string; slaDays: number }> = {
  NEW: { title: 'New', color: 'text-blue-400', slaDays: 1 },
  CONTACTED: { title: 'Contacted', color: 'text-purple-400', slaDays: 3 },
  QUOTED: { title: 'Quoted', color: 'text-yellow-400', slaDays: 7 },
  SCHEDULED: { title: 'Scheduled', color: 'text-cyan-400', slaDays: 14 },
  WON: { title: 'Won', color: 'text-green-400', slaDays: 0 },
  LOST: { title: 'Lost', color: 'text-red-400', slaDays: 0 },
};

interface LeadCardProps {
  lead: Lead;
  onClick: () => void;
  isDragging?: boolean;
}

function LeadCard({ lead, onClick, isDragging }: LeadCardProps) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging: isSortableDragging,
  } = useSortable({ id: lead.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isSortableDragging ? 0.5 : 1,
  };

  const getContactName = (contact: Contact) => {
    if (contact.first_name || contact.last_name) {
      return `${contact.first_name || ''} ${contact.last_name || ''}`.trim();
    }
    return contact.company || contact.email || 'Unknown';
  };

  const formatValue = (value?: number) => {
    if (!value) return null;
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
    }).format(value);
  };

  const calculateDaysOld = (createdAt: string) => {
    const created = new Date(createdAt);
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - created.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
  };

  const getSLAStatus = () => {
    const daysOld = calculateDaysOld(lead.created_at);
    const slaDays = COLUMN_CONFIG[lead.status as LeadStatus]?.slaDays || 0;

    if (slaDays === 0) return null;

    if (daysOld > slaDays) {
      return { label: `${daysOld - slaDays}d overdue`, class: 'bg-red-500/20 text-red-400 border-red-500' };
    } else if (daysOld === slaDays) {
      return { label: 'Due today', class: 'bg-yellow-500/20 text-yellow-400 border-yellow-500' };
    } else {
      return { label: `${slaDays - daysOld}d left`, class: 'bg-green-500/20 text-green-400 border-green-500' };
    }
  };

  const slaStatus = getSLAStatus();

  return (
    <div
      ref={setNodeRef}
      style={style}
      {...attributes}
      {...listeners}
      onClick={onClick}
      className={`p-3 rounded-lg border bg-white/5 border-white/10 hover:bg-white/10 cursor-pointer transition-all ${
        isDragging ? 'shadow-lg ring-2 ring-primary' : ''
      }`}
    >
      <div className="flex items-start justify-between gap-2 mb-2">
        <p className="font-medium text-text-primary text-sm">{getContactName(lead.contact)}</p>
        {slaStatus && (
          <span className={`px-2 py-0.5 rounded text-xs border ${slaStatus.class}`}>
            {slaStatus.label}
          </span>
        )}
      </div>

      {lead.contact.company && lead.contact.company !== getContactName(lead.contact) && (
        <p className="text-xs text-text-muted mb-1">{lead.contact.company}</p>
      )}

      {lead.value && (
        <p className="text-sm text-success font-medium">{formatValue(lead.value)}</p>
      )}

      {lead.source && (
        <div className="mt-2 pt-2 border-t border-white/5">
          <span className="text-xs text-text-muted">Source: {lead.source}</span>
        </div>
      )}
    </div>
  );
}

interface KanbanColumnProps {
  status: LeadStatus;
  leads: Lead[];
  onLeadClick: (lead: Lead) => void;
}

function KanbanColumn({ status, leads, onLeadClick }: KanbanColumnProps) {
  const config = COLUMN_CONFIG[status];
  const leadIds = leads.map(lead => lead.id);

  return (
    <div className="flex flex-col h-full">
      <div className="mb-4">
        <h3 className={`text-lg font-display font-semibold ${config.color} flex items-center gap-2`}>
          {config.title}
          <span className="text-text-muted text-sm font-normal">({leads.length})</span>
        </h3>
        {config.slaDays > 0 && (
          <p className="text-xs text-text-muted mt-1">SLA: {config.slaDays} days</p>
        )}
      </div>

      <SortableContext items={leadIds} strategy={verticalListSortingStrategy}>
        <div className="flex-1 space-y-3 min-h-[200px] p-4 rounded-lg bg-white/5 border border-white/10">
          {leads.length === 0 ? (
            <p className="text-sm text-text-muted italic text-center py-8">No leads</p>
          ) : (
            leads.map((lead) => (
              <LeadCard
                key={lead.id}
                lead={lead}
                onClick={() => onLeadClick(lead)}
              />
            ))
          )}
        </div>
      </SortableContext>
    </div>
  );
}

interface QuickComposerModalProps {
  lead: Lead | null;
  actionType: 'call' | 'text' | 'email' | null;
  onClose: () => void;
  onSend: (message: string) => void;
}

function QuickComposerModal({ lead, actionType, onClose, onSend }: QuickComposerModalProps) {
  const [message, setMessage] = useState('');

  if (!lead || !actionType) return null;

  const getContactName = (contact: Contact) => {
    if (contact.first_name || contact.last_name) {
      return `${contact.first_name || ''} ${contact.last_name || ''}`.trim();
    }
    return contact.company || contact.email || 'Unknown';
  };

  const handleSend = () => {
    if (message.trim()) {
      onSend(message);
      setMessage('');
    }
  };

  const actionConfig = {
    call: { title: 'Log Call', icon: '📞', placeholder: 'Call notes...' },
    text: { title: 'Send Text', icon: '💬', placeholder: 'Text message...' },
    email: { title: 'Send Email', icon: '📧', placeholder: 'Email body...' },
  };

  const config = actionConfig[actionType];

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-full max-w-lg bg-bg-elevated border border-white/10 rounded-lg shadow-lg z-50">
        {/* Header */}
        <div className="border-b border-white/10 p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-2xl">{config.icon}</span>
              <div>
                <h3 className="text-lg font-semibold">{config.title}</h3>
                <p className="text-sm text-text-muted">{getContactName(lead.contact)}</p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-2 hover:bg-white/10 rounded-lg transition-colors"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-4">
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder={config.placeholder}
            className="w-full h-32 px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-text-primary placeholder-text-muted resize-none focus:outline-none focus:ring-2 focus:ring-primary"
            autoFocus
          />
        </div>

        {/* Footer */}
        <div className="border-t border-white/10 p-4 flex justify-end gap-3">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg border border-white/10 hover:bg-white/10 transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleSend}
            disabled={!message.trim()}
            className="px-4 py-2 rounded-lg bg-primary text-white hover:bg-primary-dark disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Send (Stub)
          </button>
        </div>
      </div>
    </>
  );
}

interface LeadDetailDrawerProps {
  lead: Lead | null;
  onClose: () => void;
}

function LeadDetailDrawer({ lead, onClose }: LeadDetailDrawerProps) {
  if (!lead) return null;

  const getContactName = (contact: Contact) => {
    if (contact.first_name || contact.last_name) {
      return `${contact.first_name || ''} ${contact.last_name || ''}`.trim();
    }
    return contact.company || contact.email || 'Unknown';
  };

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40"
        onClick={onClose}
      />

      {/* Drawer */}
      <div className="fixed right-0 top-0 bottom-0 w-full max-w-2xl bg-bg-elevated border-l border-white/10 z-50 overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-bg-elevated border-b border-white/10 p-6">
          <div className="flex items-start justify-between">
            <div>
              <h2 className="text-2xl font-display font-bold text-gradient">
                {getContactName(lead.contact)}
              </h2>
              <p className="text-sm text-text-muted mt-1">Lead ID: #{lead.id}</p>
            </div>
            <button
              onClick={onClose}
              className="p-2 hover:bg-white/10 rounded-lg transition-colors"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Overview Section */}
          <Card>
            <h3 className="text-lg font-semibold mb-4">Overview</h3>
            <dl className="grid grid-cols-2 gap-4">
              <div>
                <dt className="text-sm text-text-muted">Status</dt>
                <dd className="text-base text-text-primary font-medium mt-1">
                  {COLUMN_CONFIG[lead.status as LeadStatus]?.title || lead.status}
                </dd>
              </div>
              <div>
                <dt className="text-sm text-text-muted">Value</dt>
                <dd className="text-base text-success font-medium mt-1">
                  {lead.value ? `$${lead.value.toLocaleString()}` : 'Not set'}
                </dd>
              </div>
              <div>
                <dt className="text-sm text-text-muted">Source</dt>
                <dd className="text-base text-text-primary mt-1">{lead.source || 'Unknown'}</dd>
              </div>
              <div>
                <dt className="text-sm text-text-muted">Probability</dt>
                <dd className="text-base text-text-primary mt-1">{lead.probability || 0}%</dd>
              </div>
            </dl>
          </Card>

          {/* Contact Information */}
          <Card>
            <h3 className="text-lg font-semibold mb-4">Contact Information</h3>
            <dl className="space-y-3">
              {lead.contact.email && (
                <div>
                  <dt className="text-sm text-text-muted">Email</dt>
                  <dd className="text-base text-text-primary mt-1">
                    <a href={`mailto:${lead.contact.email}`} className="hover:text-primary">
                      {lead.contact.email}
                    </a>
                  </dd>
                </div>
              )}
              {lead.contact.phone && (
                <div>
                  <dt className="text-sm text-text-muted">Phone</dt>
                  <dd className="text-base text-text-primary mt-1">
                    <a href={`tel:${lead.contact.phone}`} className="hover:text-primary">
                      {lead.contact.phone}
                    </a>
                  </dd>
                </div>
              )}
              {lead.contact.company && (
                <div>
                  <dt className="text-sm text-text-muted">Company</dt>
                  <dd className="text-base text-text-primary mt-1">{lead.contact.company}</dd>
                </div>
              )}
              {lead.contact.title && (
                <div>
                  <dt className="text-sm text-text-muted">Title</dt>
                  <dd className="text-base text-text-primary mt-1">{lead.contact.title}</dd>
                </div>
              )}
            </dl>
          </Card>

          {/* Notes */}
          {lead.notes && (
            <Card>
              <h3 className="text-lg font-semibold mb-4">Notes</h3>
              <p className="text-base text-text-secondary whitespace-pre-wrap">{lead.notes}</p>
            </Card>
          )}

          {/* Placeholder sections */}
          <Card>
            <h3 className="text-lg font-semibold mb-4">Timeline</h3>
            <p className="text-sm text-text-muted italic">Interaction timeline coming soon...</p>
          </Card>

          <Card>
            <h3 className="text-lg font-semibold mb-4">Quotes & Invoices</h3>
            <p className="text-sm text-text-muted italic">Quotes and invoices coming soon...</p>
          </Card>

          <Card>
            <h3 className="text-lg font-semibold mb-4">Appointments</h3>
            <p className="text-sm text-text-muted italic">Scheduled appointments coming soon...</p>
          </Card>
        </div>
      </div>
    </>
  );
}

const LeadsPage: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [board, setBoard] = useState<LeadBoard | null>(null);
  const [unassignedLeads, setUnassignedLeads] = useState<Lead[]>([]);
  const [followUpsDue, setFollowUpsDue] = useState<Lead[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeId, setActiveId] = useState<number | null>(null);
  const [selectedLead, setSelectedLead] = useState<Lead | null>(null);
  const [composerLead, setComposerLead] = useState<Lead | null>(null);
  const [composerAction, setComposerAction] = useState<'call' | 'text' | 'email' | null>(null);
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null);

  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8,
      },
    })
  );

  useEffect(() => {
    loadLeads();
    loadRightRail();
  }, []);

  useEffect(() => {
    if (toast) {
      const timer = setTimeout(() => setToast(null), 3000);
      return () => clearTimeout(timer);
    }
  }, [toast]);

  const loadLeads = async () => {
    try {
      setLoading(true);
      const data = await leadsAPI.getLeadsBoard();
      setBoard(data);
      setError('');
    } catch (err: any) {
      console.error('Error loading leads:', err);
      setError('Failed to load leads. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const loadRightRail = async () => {
    try {
      const [unassigned, followUps] = await Promise.all([
        leadsAPI.getUnassignedLeads(10),
        leadsAPI.getFollowUpsDue(),
      ]);
      setUnassignedLeads(unassigned);
      setFollowUpsDue(followUps);
    } catch (err: any) {
      console.error('Error loading right rail data:', err);
    }
  };

  const calculateDaysOld = (createdAt: string) => {
    const created = new Date(createdAt);
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - created.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
  };

  const handleAssignToMe = async (leadId: number) => {
    if (!user?.id) return;

    try {
      await leadsAPI.assignLead(leadId, user.id);
      setToast({ message: 'Lead assigned to you', type: 'success' });
      // Reload both lists
      await Promise.all([loadLeads(), loadRightRail()]);
    } catch (err: any) {
      console.error('Error assigning lead:', err);
      setToast({ message: 'Failed to assign lead', type: 'error' });
    }
  };

  const handleQuickAction = (lead: Lead, action: 'call' | 'text' | 'email') => {
    setComposerLead(lead);
    setComposerAction(action);
  };

  const handleSendMessage = async (message: string) => {
    if (!composerLead || !composerAction) return;

    try {
      const interactionTypeMap = {
        call: 'PHONE',
        text: 'SMS',
        email: 'EMAIL',
      };

      await leadsAPI.createInteraction(composerLead.id, {
        contact_id: composerLead.contact_id,
        interaction_type: interactionTypeMap[composerAction],
        direction: 'OUTBOUND',
        subject: `${composerAction.charAt(0).toUpperCase() + composerAction.slice(1)} interaction`,
        body: message,
      });

      setToast({ message: `${composerAction.charAt(0).toUpperCase() + composerAction.slice(1)} logged (stub)`, type: 'success' });
      setComposerLead(null);
      setComposerAction(null);
      await loadRightRail();
    } catch (err: any) {
      console.error('Error creating interaction:', err);
      setToast({ message: 'Failed to log interaction', type: 'error' });
    }
  };

  const findLeadAndStatus = (leadId: number): { lead: Lead; status: LeadStatus } | null => {
    if (!board) return null;

    for (const [status, leads] of Object.entries(board)) {
      const lead = leads.find((l: Lead) => l.id === leadId);
      if (lead) {
        return { lead, status: status.toUpperCase() as LeadStatus };
      }
    }
    return null;
  };

  const handleDragStart = (event: DragStartEvent) => {
    setActiveId(event.active.id as number);
  };

  const handleDragEnd = async (event: DragEndEvent) => {
    const { active, over } = event;
    setActiveId(null);

    if (!over || !board) return;

    const leadId = active.id as number;
    const newStatus = over.id as LeadStatus;

    const result = findLeadAndStatus(leadId);
    if (!result) return;

    const { lead, status: oldStatus } = result;

    if (oldStatus === newStatus) return;

    // Optimistic update
    const updatedBoard = { ...board };
    const oldStatusKey = oldStatus.toLowerCase() as keyof LeadBoard;
    const newStatusKey = newStatus.toLowerCase() as keyof LeadBoard;

    updatedBoard[oldStatusKey] = updatedBoard[oldStatusKey].filter((l: Lead) => l.id !== leadId);
    updatedBoard[newStatusKey] = [...updatedBoard[newStatusKey], { ...lead, status: newStatus }];
    setBoard(updatedBoard);

    try {
      await leadsAPI.updateLeadStatus(leadId, newStatus);
      setToast({ message: `Lead moved to ${COLUMN_CONFIG[newStatus].title}`, type: 'success' });

      // If moved to QUOTED, navigate to estimator
      if (newStatus === 'QUOTED') {
        setTimeout(() => {
          navigate(`/estimator?lead=${leadId}`);
        }, 500);
      }
    } catch (err: any) {
      console.error('Error updating lead:', err);
      setToast({ message: 'Failed to update lead. Reverting changes.', type: 'error' });
      // Revert on error
      const revertedBoard = { ...board };
      revertedBoard[newStatusKey] = revertedBoard[newStatusKey].filter((l: Lead) => l.id !== leadId);
      revertedBoard[oldStatusKey] = [...revertedBoard[oldStatusKey], lead];
      setBoard(revertedBoard);
    }
  };

  const allLeads = board ? Object.values(board).flat() : [];
  const activeLead = activeId ? allLeads.find((l: Lead) => l.id === activeId) : null;

  const getContactName = (contact: Contact) => {
    if (contact.first_name || contact.last_name) {
      return `${contact.first_name || ''} ${contact.last_name || ''}`.trim();
    }
    return contact.company || contact.email || 'Unknown';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-bg-base flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-primary border-t-transparent"></div>
          <p className="mt-4 text-text-secondary">Loading leads...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-bg-base">
        <div className="p-8 pb-6 border-b border-white/5">
          <h1 className="text-3xl font-display font-bold text-gradient">Leads Pipeline</h1>
        </div>
        <div className="p-8">
          <div className="bg-error/10 border border-error text-error p-4 rounded-lg">
            {error}
            <button
              onClick={loadLeads}
              className="ml-4 underline hover:no-underline"
            >
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-bg-base">
      {/* Page header */}
      <div className="p-8 pb-6 border-b border-white/5">
        <h1 className="text-3xl font-display font-bold text-gradient">Leads Pipeline</h1>
        <p className="text-sm text-text-muted mt-1">Drag and drop leads to update their status</p>
      </div>

      {/* Main content with right rail */}
      <div className="flex gap-6 p-8">
        {/* Kanban Board */}
        <main className="flex-1">
          <DndContext
            sensors={sensors}
            collisionDetection={closestCorners}
            onDragStart={handleDragStart}
            onDragEnd={handleDragEnd}
          >
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-6">
              {board && (
                <>
                  <div>
                    <KanbanColumn
                      status="NEW"
                      leads={board.new}
                      onLeadClick={setSelectedLead}
                    />
                  </div>
                  <div>
                    <KanbanColumn
                      status="CONTACTED"
                      leads={board.contacted}
                      onLeadClick={setSelectedLead}
                    />
                  </div>
                  <div>
                    <KanbanColumn
                      status="QUOTED"
                      leads={board.quoted}
                      onLeadClick={setSelectedLead}
                    />
                  </div>
                  <div>
                    <KanbanColumn
                      status="SCHEDULED"
                      leads={board.scheduled}
                      onLeadClick={setSelectedLead}
                    />
                  </div>
                  <div>
                    <KanbanColumn
                      status="WON"
                      leads={board.won}
                      onLeadClick={setSelectedLead}
                    />
                  </div>
                  <div>
                    <KanbanColumn
                      status="LOST"
                      leads={board.lost}
                      onLeadClick={setSelectedLead}
                    />
                  </div>
                </>
              )}
            </div>

            <DragOverlay>
              {activeLead ? (
                <LeadCard lead={activeLead} onClick={() => {}} isDragging />
              ) : null}
            </DragOverlay>
          </DndContext>
        </main>

        {/* Right Rail */}
        <aside className="w-80 space-y-6">
          {/* Unassigned Leads */}
          <Card>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">Unassigned Leads</h3>
              <span className="px-2 py-1 rounded bg-primary/20 text-primary text-xs font-medium">
                {unassignedLeads.length}
              </span>
            </div>

            <div className="space-y-3 max-h-96 overflow-y-auto">
              {unassignedLeads.length === 0 ? (
                <p className="text-sm text-text-muted italic text-center py-4">No unassigned leads</p>
              ) : (
                unassignedLeads.map((lead) => (
                  <div
                    key={lead.id}
                    className="p-3 rounded-lg bg-white/5 border border-white/10 hover:bg-white/10 transition-colors"
                  >
                    <div className="flex items-start justify-between gap-2 mb-2">
                      <p className="font-medium text-text-primary text-sm">
                        {getContactName(lead.contact)}
                      </p>
                      <span className="px-2 py-0.5 rounded text-xs bg-orange-500/20 text-orange-400 border border-orange-500">
                        {calculateDaysOld(lead.created_at)}d old
                      </span>
                    </div>

                    {lead.contact.company && (
                      <p className="text-xs text-text-muted mb-2">{lead.contact.company}</p>
                    )}

                    <div className="flex gap-2 mt-3">
                      <button
                        onClick={() => handleQuickAction(lead, 'call')}
                        className="flex-1 px-2 py-1.5 rounded bg-blue-500/20 text-blue-400 hover:bg-blue-500/30 text-xs transition-colors"
                        title="Call"
                      >
                        📞
                      </button>
                      <button
                        onClick={() => handleQuickAction(lead, 'text')}
                        className="flex-1 px-2 py-1.5 rounded bg-green-500/20 text-green-400 hover:bg-green-500/30 text-xs transition-colors"
                        title="Text"
                      >
                        💬
                      </button>
                      <button
                        onClick={() => handleQuickAction(lead, 'email')}
                        className="flex-1 px-2 py-1.5 rounded bg-purple-500/20 text-purple-400 hover:bg-purple-500/30 text-xs transition-colors"
                        title="Email"
                      >
                        📧
                      </button>
                      <button
                        onClick={() => handleAssignToMe(lead.id)}
                        className="flex-1 px-2 py-1.5 rounded bg-primary/20 text-primary hover:bg-primary/30 text-xs transition-colors"
                        title="Assign to me"
                      >
                        Assign
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>
          </Card>

          {/* Follow-ups Due */}
          <Card>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">Follow-ups Due</h3>
              <span className="px-2 py-1 rounded bg-yellow-500/20 text-yellow-400 text-xs font-medium">
                {followUpsDue.length}
              </span>
            </div>

            <div className="space-y-3 max-h-96 overflow-y-auto">
              {followUpsDue.length === 0 ? (
                <p className="text-sm text-text-muted italic text-center py-4">No follow-ups due today</p>
              ) : (
                followUpsDue.map((lead) => (
                  <div
                    key={lead.id}
                    className="p-3 rounded-lg bg-white/5 border border-white/10 hover:bg-white/10 transition-colors cursor-pointer"
                    onClick={() => setSelectedLead(lead)}
                  >
                    <p className="font-medium text-text-primary text-sm mb-1">
                      {getContactName(lead.contact)}
                    </p>
                    {lead.contact.company && (
                      <p className="text-xs text-text-muted mb-2">{lead.contact.company}</p>
                    )}
                    <div className="flex items-center gap-2">
                      <span className="px-2 py-0.5 rounded text-xs bg-yellow-500/20 text-yellow-400 border border-yellow-500">
                        Due Today
                      </span>
                      <span className="text-xs text-text-muted">
                        {COLUMN_CONFIG[lead.status as LeadStatus]?.title}
                      </span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </Card>
        </aside>
      </div>

      {/* Lead Detail Drawer */}
      <LeadDetailDrawer lead={selectedLead} onClose={() => setSelectedLead(null)} />

      {/* Quick Composer Modal */}
      <QuickComposerModal
        lead={composerLead}
        actionType={composerAction}
        onClose={() => {
          setComposerLead(null);
          setComposerAction(null);
        }}
        onSend={handleSendMessage}
      />

      {/* Toast Notification */}
      {toast && (
        <div className="fixed bottom-8 right-8 z-50 animate-slide-up">
          <div className={`px-6 py-4 rounded-lg border shadow-lg ${
            toast.type === 'success'
              ? 'bg-success/20 border-success text-success'
              : 'bg-error/20 border-error text-error'
          }`}>
            {toast.message}
          </div>
        </div>
      )}
    </div>
  );
};

export default LeadsPage;
