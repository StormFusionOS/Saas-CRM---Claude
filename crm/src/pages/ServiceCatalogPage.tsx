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
  pricing_formula?: string;
  modifiers: Record<string, number>;
  is_active: boolean;
  display_order: number;
  metadata: Record<string, string>;
  created_at: string;
  updated_at?: string;
}

interface ServiceFormData {
  name: string;
  description: string;
  category: string;
  base_price: string;
  unit: string;
  min_price: string;
  pricing_formula: string;
  is_active: boolean;
}

const initialFormData: ServiceFormData = {
  name: '',
  description: '',
  category: '',
  base_price: '',
  unit: 'sq_ft',
  min_price: '',
  pricing_formula: '',
  is_active: true,
};

const ServiceCatalogPage: React.FC = () => {
  const { token } = useAuth();
  const [services, setServices] = useState<Service[]>([]);
  const [filteredServices, setFilteredServices] = useState<Service[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [showForm, setShowForm] = useState(false);
  const [editingService, setEditingService] = useState<Service | null>(null);
  const [formData, setFormData] = useState<ServiceFormData>(initialFormData);
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});
  const [submitLoading, setSubmitLoading] = useState(false);

  // Fetch services from API
  const fetchServices = async () => {
    try {
      setLoading(true);
      setError('');
      const response = await fetch('http://localhost:8000/api/v1/sales/services', {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch services');
      }

      const data = await response.json();
      setServices(data);
      setFilteredServices(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchServices();
  }, [token]);

  // Filter services based on search and category
  useEffect(() => {
    let filtered = services;

    if (searchTerm) {
      filtered = filtered.filter(
        (service) =>
          service.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
          service.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
          service.category.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    if (categoryFilter !== 'all') {
      filtered = filtered.filter((service) => service.category === categoryFilter);
    }

    setFilteredServices(filtered);
  }, [searchTerm, categoryFilter, services]);

  // Get unique categories
  const categories = Array.from(new Set(services.map((s) => s.category)));

  // Validate form
  const validateForm = (): boolean => {
    const errors: Record<string, string> = {};

    if (!formData.name.trim()) {
      errors.name = 'Service name is required';
    }

    if (!formData.description.trim()) {
      errors.description = 'Description is required';
    }

    if (!formData.category.trim()) {
      errors.category = 'Category is required';
    }

    if (!formData.base_price || parseFloat(formData.base_price) < 0) {
      errors.base_price = 'Base price must be a positive number';
    }

    if (!formData.unit.trim()) {
      errors.unit = 'Unit is required';
    }

    if (formData.min_price && parseFloat(formData.min_price) < 0) {
      errors.min_price = 'Minimum price must be a positive number';
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setSubmitLoading(true);
    setError('');

    try {
      const payload = {
        name: formData.name,
        description: formData.description,
        category: formData.category,
        base_price: parseFloat(formData.base_price),
        unit: formData.unit,
        min_price: formData.min_price ? parseFloat(formData.min_price) : null,
        pricing_formula: formData.pricing_formula || null,
        modifiers: {},
        is_active: formData.is_active,
        display_order: 0,
        metadata: {},
      };

      let response;
      if (editingService) {
        response = await fetch(
          `http://localhost:8000/api/v1/sales/services/${editingService.id}`,
          {
            method: 'PATCH',
            headers: {
              'Content-Type': 'application/json',
              Authorization: `Bearer ${token}`,
            },
            body: JSON.stringify(payload),
          }
        );
      } else {
        response = await fetch('http://localhost:8000/api/v1/sales/services', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify(payload),
        });
      }

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to save service');
      }

      await fetchServices();
      setShowForm(false);
      setEditingService(null);
      setFormData(initialFormData);
      setFormErrors({});
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setSubmitLoading(false);
    }
  };

  // Handle edit
  const handleEdit = (service: Service) => {
    setEditingService(service);
    setFormData({
      name: service.name,
      description: service.description,
      category: service.category,
      base_price: service.base_price.toString(),
      unit: service.unit,
      min_price: service.min_price?.toString() || '',
      pricing_formula: service.pricing_formula || '',
      is_active: service.is_active,
    });
    setShowForm(true);
  };

  // Handle delete
  const handleDelete = async (serviceId: number) => {
    if (!confirm('Are you sure you want to delete this service?')) {
      return;
    }

    try {
      const response = await fetch(
        `http://localhost:8000/api/v1/sales/services/${serviceId}`,
        {
          method: 'DELETE',
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error('Failed to delete service');
      }

      await fetchServices();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    }
  };

  // Calculate price preview
  const calculatePricePreview = (basePrice: number, minPrice?: number, quantity: number = 1) => {
    const calculatedPrice = basePrice * quantity;
    const finalPrice = minPrice ? Math.max(calculatedPrice, minPrice) : calculatedPrice;
    return finalPrice.toFixed(2);
  };

  return (
    <div className="min-h-screen bg-bg-base">
      {/* Page header */}
      <div className="p-8 pb-6 border-b border-white/5">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-3xl font-display font-bold text-gradient">Service Catalog</h1>
            <p className="text-sm text-text-muted mt-1">
              Manage your service offerings and pricing
            </p>
          </div>
          <Button
            onClick={() => {
              setShowForm(!showForm);
              setEditingService(null);
              setFormData(initialFormData);
              setFormErrors({});
            }}
            variant={showForm ? 'outline' : 'primary'}
          >
            {showForm ? 'Cancel' : '+ New Service'}
          </Button>
        </div>
      </div>

      {/* Main content */}
      <main className="p-8">
        {error && (
          <div className="mb-6 p-4 bg-error/10 border border-error rounded-base text-error">
            {error}
          </div>
        )}

        {/* Create/Edit Form */}
        {showForm && (
          <Card className="mb-8">
            <h2 className="text-xl font-display font-semibold mb-6">
              {editingService ? 'Edit Service' : 'Create New Service'}
            </h2>
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Input
                  id="name"
                  label="Service Name"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  error={formErrors.name}
                  placeholder="e.g., House Wash"
                  required
                />

                <Input
                  id="category"
                  label="Category"
                  value={formData.category}
                  onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                  error={formErrors.category}
                  placeholder="e.g., house_wash"
                  helperText="Use snake_case (e.g., house_wash, gutter_clean)"
                  required
                />

                <Input
                  id="base_price"
                  label="Base Price"
                  type="number"
                  step="0.01"
                  min="0"
                  value={formData.base_price}
                  onChange={(e) => setFormData({ ...formData, base_price: e.target.value })}
                  error={formErrors.base_price}
                  placeholder="0.00"
                  required
                />

                <Input
                  id="unit"
                  label="Unit"
                  value={formData.unit}
                  onChange={(e) => setFormData({ ...formData, unit: e.target.value })}
                  error={formErrors.unit}
                  placeholder="sq_ft, linear_ft, each, hour"
                  helperText="Unit of measurement for pricing"
                  required
                />

                <Input
                  id="min_price"
                  label="Minimum Price (Optional)"
                  type="number"
                  step="0.01"
                  min="0"
                  value={formData.min_price}
                  onChange={(e) => setFormData({ ...formData, min_price: e.target.value })}
                  error={formErrors.min_price}
                  placeholder="0.00"
                  helperText="Price floor for this service"
                />

                <Input
                  id="pricing_formula"
                  label="Pricing Formula (Optional)"
                  value={formData.pricing_formula}
                  onChange={(e) =>
                    setFormData({ ...formData, pricing_formula: e.target.value })
                  }
                  placeholder="base_price * quantity"
                  helperText="Advanced pricing calculation"
                />
              </div>

              <div>
                <label htmlFor="description" className="block text-sm font-medium text-text-primary mb-2">
                  Description <span className="text-error ml-1">*</span>
                </label>
                <textarea
                  id="description"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="w-full px-4 py-2 bg-bg-elev text-text-primary border border-border-default rounded-base transition-all duration-base placeholder:text-text-muted focus-ring hover:border-border-strong min-h-[100px]"
                  placeholder="Detailed service description..."
                  required
                />
                {formErrors.description && (
                  <p className="mt-1 text-sm text-error">{formErrors.description}</p>
                )}
              </div>

              {/* Pricing Preview */}
              {formData.base_price && (
                <div className="p-4 bg-bg-hover rounded-base border border-border-default">
                  <h3 className="text-sm font-medium text-text-secondary mb-2">
                    Pricing Preview
                  </h3>
                  <div className="grid grid-cols-3 gap-4 text-sm">
                    <div>
                      <p className="text-text-muted">10 {formData.unit}</p>
                      <p className="text-lg font-semibold text-primary">
                        $
                        {calculatePricePreview(
                          parseFloat(formData.base_price),
                          formData.min_price ? parseFloat(formData.min_price) : undefined,
                          10
                        )}
                      </p>
                    </div>
                    <div>
                      <p className="text-text-muted">50 {formData.unit}</p>
                      <p className="text-lg font-semibold text-primary">
                        $
                        {calculatePricePreview(
                          parseFloat(formData.base_price),
                          formData.min_price ? parseFloat(formData.min_price) : undefined,
                          50
                        )}
                      </p>
                    </div>
                    <div>
                      <p className="text-text-muted">100 {formData.unit}</p>
                      <p className="text-lg font-semibold text-primary">
                        $
                        {calculatePricePreview(
                          parseFloat(formData.base_price),
                          formData.min_price ? parseFloat(formData.min_price) : undefined,
                          100
                        )}
                      </p>
                    </div>
                  </div>
                  {formData.min_price && (
                    <p className="text-xs text-text-muted mt-2">
                      Minimum price: ${parseFloat(formData.min_price).toFixed(2)}
                    </p>
                  )}
                </div>
              )}

              <div className="flex gap-3 pt-4">
                <Button type="submit" disabled={submitLoading}>
                  {submitLoading ? 'Saving...' : editingService ? 'Update Service' : 'Create Service'}
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => {
                    setShowForm(false);
                    setEditingService(null);
                    setFormData(initialFormData);
                    setFormErrors({});
                  }}
                >
                  Cancel
                </Button>
              </div>
            </form>
          </Card>
        )}

        {/* Search and Filter */}
        <div className="mb-6 flex flex-col sm:flex-row gap-4">
          <div className="flex-1">
            <Input
              id="search"
              placeholder="Search services..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="px-4 py-2 bg-bg-elev text-text-primary border border-border-default rounded-base transition-all duration-base focus-ring hover:border-border-strong"
          >
            <option value="all">All Categories</option>
            {categories.map((category) => (
              <option key={category} value={category}>
                {category.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase())}
              </option>
            ))}
          </select>
        </div>

        {/* Services List */}
        {loading ? (
          <Card>
            <div className="text-center py-12">
              <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-primary border-r-transparent"></div>
              <p className="mt-4 text-text-muted">Loading services...</p>
            </div>
          </Card>
        ) : filteredServices.length === 0 ? (
          <Card>
            <div className="text-center py-12">
              <div className="text-6xl mb-4">📦</div>
              <h3 className="text-xl font-display font-semibold mb-2">No Services Found</h3>
              <p className="text-text-muted mb-6">
                {searchTerm || categoryFilter !== 'all'
                  ? 'No services match your filters. Try adjusting your search.'
                  : 'Get started by creating your first service.'}
              </p>
              {!searchTerm && categoryFilter === 'all' && (
                <Button onClick={() => setShowForm(true)}>Create First Service</Button>
              )}
            </div>
          </Card>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {filteredServices.map((service) => (
              <Card key={service.id} className="glow-hover">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="text-xl font-display font-semibold text-gradient">
                      {service.name}
                    </h3>
                    <p className="text-sm text-text-muted mt-1">
                      {service.category.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase())}
                    </p>
                  </div>
                  <div className="flex gap-2">
                    <Button size="sm" variant="ghost" onClick={() => handleEdit(service)}>
                      Edit
                    </Button>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => handleDelete(service.id)}
                      className="text-error hover:bg-error/10"
                    >
                      Delete
                    </Button>
                  </div>
                </div>

                <p className="text-text-secondary mb-4">{service.description}</p>

                <div className="grid grid-cols-2 gap-4 p-4 bg-bg-base rounded-base border border-border-default">
                  <div>
                    <p className="text-xs text-text-muted">Base Price</p>
                    <p className="text-lg font-semibold text-primary">
                      ${service.base_price.toFixed(2)}{' '}
                      <span className="text-sm text-text-muted">/ {service.unit}</span>
                    </p>
                  </div>
                  {service.min_price && (
                    <div>
                      <p className="text-xs text-text-muted">Min Price</p>
                      <p className="text-lg font-semibold text-warning">
                        ${service.min_price.toFixed(2)}
                      </p>
                    </div>
                  )}
                </div>

                {service.pricing_formula && (
                  <div className="mt-4 p-3 bg-bg-hover rounded-base">
                    <p className="text-xs text-text-muted mb-1">Pricing Formula</p>
                    <code className="text-sm text-accent">{service.pricing_formula}</code>
                  </div>
                )}

                <div className="mt-4 flex items-center gap-2">
                  <span
                    className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      service.is_active
                        ? 'bg-success/10 text-success'
                        : 'bg-text-muted/10 text-text-muted'
                    }`}
                  >
                    {service.is_active ? 'Active' : 'Inactive'}
                  </span>
                </div>
              </Card>
            ))}
          </div>
        )}
      </main>
    </div>
  );
};

export default ServiceCatalogPage;
