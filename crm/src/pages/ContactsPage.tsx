/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * This file is part of the RiverCityClean SaaS CRM system.
 */

/**
 * Contacts Page with TanStack Table Integration
 *
 * Demonstrates DataTable usage with:
 * - Column definitions using helper functions
 * - Row actions menu
 * - Global search and filtering
 * - Column visibility toggles
 * - CSV export
 * - Server-side pagination (simulated)
 * - Keyboard accessibility
 */

import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { ColumnDef } from '@tanstack/react-table';
import { Mail, Phone, Building2, UserCircle, Edit, Trash2, Eye } from 'lucide-react';
import { DataTable } from '@/components/data-table';
import { DataTableRowActions, RowAction } from '@/components/data-table';
import {
  createTextColumn,
  createDateColumn,
  createStatusColumn,
} from '@/components/data-table/columns';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/shadcn/dialog';
import { ContactForm, ContactFormValues } from '@/components/forms/ContactForm';
import { useToast } from '@/components/ui/shadcn/use-toast';
import { leadsAPI } from '@/lib/api';

interface Contact {
  id: number;
  first_name?: string;
  last_name?: string;
  company?: string;
  email?: string;
  phone?: string;
  title?: string;
  created_at?: string;
  updated_at?: string;
  status?: 'ACTIVE' | 'INACTIVE' | 'LEAD' | 'CUSTOMER';
}

// Status badge configuration
const STATUS_MAP = {
  ACTIVE: { label: 'Active', variant: 'default' as const },
  INACTIVE: { label: 'Inactive', variant: 'outline' as const },
  LEAD: { label: 'Lead', variant: 'secondary' as const },
  CUSTOMER: { label: 'Customer', variant: 'default' as const },
};

const ContactsPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedRows, setSelectedRows] = useState<Contact[]>([]);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingContact, setEditingContact] = useState<Contact | null>(null);
  const { toast } = useToast();

  // Server-side pagination state from URL params
  const pageIndex = Number(searchParams.get('page') || '0');
  const pageSize = Number(searchParams.get('pageSize') || '10');

  useEffect(() => {
    loadContacts();
  }, [pageIndex, pageSize]);

  const loadContacts = async () => {
    try {
      setLoading(true);
      setError('');

      // Fetch leads and extract contacts
      // In a real implementation, you'd have a dedicated contacts endpoint
      const leadsData = await leadsAPI.getLeadsBoard();
      const allLeads = Object.values(leadsData).flat();

      // Extract unique contacts from leads
      const contactsMap = new Map<number, Contact>();
      allLeads.forEach((lead: any) => {
        if (lead.contact && lead.contact.id) {
          contactsMap.set(lead.contact.id, {
            ...lead.contact,
            status: lead.status === 'WON' ? 'CUSTOMER' : 'LEAD',
            created_at: lead.created_at,
            updated_at: lead.updated_at,
          });
        }
      });

      setContacts(Array.from(contactsMap.values()));
    } catch (err: any) {
      console.error('Error loading contacts:', err);
      setError('Failed to load contacts. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateContact = async (values: ContactFormValues) => {
    try {
      // In a real implementation, call the API to create the contact
      console.log('Creating contact:', values);

      toast({
        title: 'Contact created',
        description: `${values.first_name} ${values.last_name} has been added successfully.`,
      });

      setIsFormOpen(false);
      await loadContacts();
    } catch (err: any) {
      console.error('Error creating contact:', err);
      toast({
        variant: 'destructive',
        title: 'Error',
        description: 'Failed to create contact. Please try again.',
      });
      throw err;
    }
  };

  const handleEditContact = async (values: ContactFormValues) => {
    if (!editingContact) return;

    try {
      // In a real implementation, call the API to update the contact
      console.log('Updating contact:', editingContact.id, values);

      toast({
        title: 'Contact updated',
        description: `${values.first_name} ${values.last_name} has been updated successfully.`,
      });

      setIsFormOpen(false);
      setEditingContact(null);
      await loadContacts();
    } catch (err: any) {
      console.error('Error updating contact:', err);
      toast({
        variant: 'destructive',
        title: 'Error',
        description: 'Failed to update contact. Please try again.',
      });
      throw err;
    }
  };

  const handleDeleteContact = async (contact: Contact) => {
    try {
      // In a real implementation, call the API to delete the contact
      console.log('Deleting contact:', contact.id);

      toast({
        title: 'Contact deleted',
        description: `${contact.first_name} ${contact.last_name} has been deleted.`,
      });

      await loadContacts();
    } catch (err: any) {
      console.error('Error deleting contact:', err);
      toast({
        variant: 'destructive',
        title: 'Error',
        description: 'Failed to delete contact. Please try again.',
      });
    }
  };

  const openCreateForm = () => {
    setEditingContact(null);
    setIsFormOpen(true);
  };

  const openEditForm = (contact: Contact) => {
    setEditingContact(contact);
    setIsFormOpen(true);
  };

  const closeForm = () => {
    setIsFormOpen(false);
    setEditingContact(null);
  };

  // Define row actions
  const rowActions: RowAction<Contact>[] = [
    {
      label: 'View Details',
      icon: Eye,
      onClick: (contact) => {
        console.log('View contact:', contact);
        // Navigate to contact detail page
      },
    },
    {
      label: 'Edit Contact',
      icon: Edit,
      onClick: openEditForm,
    },
    {
      label: 'Send Email',
      icon: Mail,
      onClick: (contact) => {
        if (contact.email) {
          window.location.href = `mailto:${contact.email}`;
        }
      },
    },
    {
      label: 'Call',
      icon: Phone,
      onClick: (contact) => {
        if (contact.phone) {
          window.location.href = `tel:${contact.phone}`;
        }
      },
      separator: true,
    },
    {
      label: 'Delete',
      icon: Trash2,
      onClick: (contact) => {
        if (confirm(`Delete ${contact.first_name} ${contact.last_name}?`)) {
          handleDeleteContact(contact);
        }
      },
      variant: 'destructive',
    },
  ];

  // Define columns using helper functions and custom definitions
  const columns: ColumnDef<Contact>[] = [
    // Name column with custom cell rendering
    {
      id: 'name',
      accessorFn: (row) => {
        const name = [row.first_name, row.last_name].filter(Boolean).join(' ');
        return name || row.email || 'Unnamed Contact';
      },
      header: 'Name',
      cell: ({ row }) => {
        const name = [row.original.first_name, row.original.last_name]
          .filter(Boolean)
          .join(' ') || row.original.email || 'Unnamed Contact';

        return (
          <div className="flex items-center gap-2">
            <UserCircle className="h-5 w-5 text-muted-foreground" />
            <div>
              <p className="font-medium text-text-primary">{name}</p>
              {row.original.title && (
                <p className="text-xs text-muted-foreground">{row.original.title}</p>
              )}
            </div>
          </div>
        );
      },
      enableSorting: true,
    },

    // Company column
    {
      id: 'company',
      accessorKey: 'company',
      header: 'Company',
      cell: ({ getValue }) => {
        const company = getValue() as string;
        if (!company) return <span className="text-muted-foreground">-</span>;

        return (
          <div className="flex items-center gap-2">
            <Building2 className="h-4 w-4 text-muted-foreground" />
            <span>{company}</span>
          </div>
        );
      },
      enableHiding: true,
    },

    // Email column
    createTextColumn<Contact>('email', 'Email', {
      sortable: true,
      cell: (value) => {
        if (!value) return <span className="text-muted-foreground">-</span>;
        return (
          <a
            href={`mailto:${value}`}
            className="text-primary hover:underline flex items-center gap-2"
            onClick={(e) => e.stopPropagation()}
          >
            <Mail className="h-4 w-4" />
            {value}
          </a>
        );
      },
    }),

    // Phone column
    createTextColumn<Contact>('phone', 'Phone', {
      cell: (value) => {
        if (!value) return <span className="text-muted-foreground">-</span>;
        return (
          <a
            href={`tel:${value}`}
            className="text-primary hover:underline flex items-center gap-2"
            onClick={(e) => e.stopPropagation()}
          >
            <Phone className="h-4 w-4" />
            {value}
          </a>
        );
      },
    }),

    // Status column with badges
    createStatusColumn<Contact>('status', 'Status', STATUS_MAP),

    // Created date column
    createDateColumn<Contact>('created_at', 'Created', {
      sortable: true,
    }),

    // Actions column
    {
      id: 'actions',
      cell: ({ row }) => (
        <DataTableRowActions row={row.original} actions={rowActions} />
      ),
      enableHiding: false,
    },
  ];

  const handlePaginationChange = (newPageIndex: number, newPageSize: number) => {
    setSearchParams({
      page: newPageIndex.toString(),
      pageSize: newPageSize.toString(),
    });
  };

  const handleExportCSV = () => {
    const headers = ['Name', 'Email', 'Phone', 'Company', 'Title', 'Status', 'Created'];
    const rows = contacts.map((contact) => [
      [contact.first_name, contact.last_name].filter(Boolean).join(' '),
      contact.email || '',
      contact.phone || '',
      contact.company || '',
      contact.title || '',
      contact.status || '',
      contact.created_at || '',
    ]);

    const csvContent = [
      headers.join(','),
      ...rows.map((row) =>
        row
          .map((cell) => (cell.includes(',') ? `"${cell}"` : cell))
          .join(',')
      ),
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `contacts-${new Date().toISOString()}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-bg-base flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-primary border-t-transparent"></div>
          <p className="mt-4 text-text-secondary">Loading contacts...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-bg-base">
        <div className="p-8">
          <Card variant="glass">
            <div className="text-center py-12">
              <p className="text-error text-lg mb-4">{error}</p>
              <Button onClick={loadContacts} variant="primary">
                Retry
              </Button>
            </div>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-bg-base">
      {/* Page Header */}
      <div className="p-8 pb-6 border-b border-border">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-display font-bold text-gradient">Contacts</h1>
            <p className="text-sm text-text-muted mt-1">
              Manage all your contacts in one place
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button
              variant="outline"
              size="md"
              onClick={loadContacts}
              disabled={loading}
            >
              Refresh
            </Button>
            <Button
              variant="primary"
              size="md"
              onClick={openCreateForm}
            >
              New Contact
            </Button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="p-8">
        <Card variant="glass" padding="lg">
          {/* Stats Bar */}
          <div className="flex items-center justify-between mb-6 pb-4 border-b border-border">
            <div className="flex items-center gap-6">
              <div>
                <p className="text-2xl font-bold text-primary">{contacts.length}</p>
                <p className="text-xs text-muted-foreground">Total Contacts</p>
              </div>
              {selectedRows.length > 0 && (
                <div>
                  <p className="text-2xl font-bold text-secondary">{selectedRows.length}</p>
                  <p className="text-xs text-muted-foreground">Selected</p>
                </div>
              )}
            </div>

            {selectedRows.length > 0 && (
              <div className="flex items-center gap-2">
                <Button variant="outline" size="sm">
                  Bulk Edit
                </Button>
                <Button variant="danger" size="sm">
                  Delete Selected
                </Button>
              </div>
            )}
          </div>

          {/* Data Table */}
          <DataTable
            columns={columns}
            data={contacts}
            searchPlaceholder="Search contacts by name, email, company..."
            enableRowSelection={true}
            enableVirtualization={contacts.length > 100}
            onRowSelectionChange={setSelectedRows}
            onExportCSV={handleExportCSV}
            pageIndex={pageIndex}
            pageSize={pageSize}
            onPaginationChange={handlePaginationChange}
          />
        </Card>
      </div>

      {/* Contact Form Dialog */}
      <Dialog open={isFormOpen} onOpenChange={setIsFormOpen}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>
              {editingContact ? 'Edit Contact' : 'Create New Contact'}
            </DialogTitle>
            <DialogDescription>
              {editingContact
                ? 'Update the contact information below.'
                : 'Fill in the details to add a new contact to your CRM.'}
            </DialogDescription>
          </DialogHeader>
          <ContactForm
            defaultValues={editingContact || undefined}
            onSubmit={editingContact ? handleEditContact : handleCreateContact}
            onCancel={closeForm}
            submitLabel={editingContact ? 'Update Contact' : 'Create Contact'}
            isEdit={!!editingContact}
          />
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default ContactsPage;
