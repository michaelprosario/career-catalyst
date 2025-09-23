// Career Catalyst Frontend Application
class CareerCatalystApp {
    constructor() {
        this.apiBaseUrl = '/api/user-opportunities';
        this.currentUserId = 'demo-user-123'; // In production, this would come from authentication
        this.opportunities = [];
        this.currentPage = 1;
        this.pageSize = 10;
        this.totalPages = 1;
        this.currentViewingOpportunity = null;
        this.currentEditingOpportunity = null;

        this.init();
    }

    init() {
        this.bindEvents();
        this.loadOpportunities();
    }

    bindEvents() {
        // Form submission
        document.getElementById('opportunityForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveOpportunity();
        });

        // Search functionality
        document.getElementById('searchKeywords').addEventListener('input',
            this.debounce(() => this.searchOpportunities(), 500));

        // Reset modal when it's closed
        document.getElementById('addOpportunityModal').addEventListener('hidden.bs.modal', () => {
            this.resetForm();
        });
    }

    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    async loadOpportunities() {
        try {
            this.showLoading(true);

            const response = await fetch(`${this.apiBaseUrl}/user/${this.currentUserId}?limit=${this.pageSize * 5}`);
            const data = await response.json();

            if (data.success) {
                this.opportunities = data.results || [];
                this.renderOpportunities();
                this.updateOpportunityCount();
            } else {
                this.showToast('Error', data.message || 'Failed to load opportunities', 'error');
            }
        } catch (error) {
            console.error('Error loading opportunities:', error);
            this.showToast('Error', 'Failed to load opportunities', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    async searchOpportunities() {
        const keywords = document.getElementById('searchKeywords').value;
        const location = document.getElementById('filterLocation').value;
        const type = document.getElementById('filterType').value;
        const status = document.getElementById('filterStatus').value;
        const isRemote = document.getElementById('filterRemote').checked;

        // If no filters are applied, load all opportunities
        if (!keywords && !location && !type && !status && !isRemote) {
            this.loadOpportunities();
            return;
        }

        try {
            this.showLoading(true);

            const searchRequest = {
                keywords: keywords || undefined,
                location: location || undefined,
                type: type || undefined,
                is_remote: isRemote || undefined,
                limit: this.pageSize * 5
            };

            // Remove undefined properties
            Object.keys(searchRequest).forEach(key =>
                searchRequest[key] === undefined && delete searchRequest[key]);

            const response = await fetch(`${this.apiBaseUrl}/search`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(searchRequest)
            });

            const data = await response.json();

            if (data.success) {
                let filteredResults = data.results || [];

                // Apply application status filter client-side since it's not in search API
                if (status) {
                    filteredResults = filteredResults.filter(opp =>
                        opp.application_status === status);
                }

                this.opportunities = filteredResults;
                this.renderOpportunities();
                this.updateOpportunityCount();
            } else {
                this.showToast('Error', data.message || 'Search failed', 'error');
            }
        } catch (error) {
            console.error('Error searching opportunities:', error);
            this.showToast('Error', 'Search failed', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    clearFilters() {
        document.getElementById('searchKeywords').value = '';
        document.getElementById('filterLocation').value = '';
        document.getElementById('filterType').value = '';
        document.getElementById('filterStatus').value = '';
        document.getElementById('filterRemote').checked = false;
        this.loadOpportunities();
    }

    renderOpportunities() {
        const container = document.getElementById('opportunitiesList');
        const noOpportunities = document.getElementById('noOpportunities');

        if (this.opportunities.length === 0) {
            container.innerHTML = '';
            noOpportunities.style.display = 'block';
            return;
        }

        noOpportunities.style.display = 'none';

        container.innerHTML = this.opportunities.map(opportunity =>
            this.createOpportunityCard(opportunity)).join('');
    }

    createOpportunityCard(opportunity) {
        const statusBadgeClass = this.getStatusBadgeClass(opportunity.application_status);
        const typeBadgeClass = this.getTypeBadgeClass(opportunity.type);
        const salaryInfo = this.formatSalaryRange(opportunity.salary_range);

        return `
            <div class="col-md-6 col-lg-4">
                <div class="card opportunity-card h-100" onclick="app.viewOpportunity('${opportunity.id}')">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start mb-2">
                            <h5 class="card-title mb-0">${this.escapeHtml(opportunity.title)}</h5>
                            <span class="badge ${statusBadgeClass} status-badge">${opportunity.application_status}</span>
                        </div>
                        <h6 class="card-subtitle mb-2 text-muted">${this.escapeHtml(opportunity.company)}</h6>

                        <div class="mb-2">
                            <span class="badge ${typeBadgeClass} me-1">${opportunity.type.replace('_', ' ')}</span>
                            ${opportunity.is_remote ? '<span class="badge bg-success">Remote</span>' : ''}
                        </div>

                        ${opportunity.location ? `<p class="card-text small mb-1"><i class="bi bi-geo-alt"></i> ${this.escapeHtml(opportunity.location)}</p>` : ''}
                        ${salaryInfo ? `<p class="card-text small salary-info mb-2">${salaryInfo}</p>` : ''}

                        <p class="card-text">${this.truncateText(opportunity.description, 100)}</p>

                        <div class="d-flex justify-content-between align-items-center">
                            <small class="text-muted">
                                ${this.formatDate(opportunity.created_at)}
                            </small>
                            <div class="btn-group" role="group">
                                <button type="button" class="btn btn-sm btn-outline-primary" onclick="event.stopPropagation(); app.editOpportunityById('${opportunity.id}')">
                                    <i class="bi bi-pencil"></i>
                                </button>
                                <button type="button" class="btn btn-sm btn-outline-danger" onclick="event.stopPropagation(); app.deleteOpportunityById('${opportunity.id}')">
                                    <i class="bi bi-trash"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    async viewOpportunity(id) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/${id}`);
            const data = await response.json();

            if (data.success && data.document) {
                this.currentViewingOpportunity = data.document;
                this.showOpportunityDetails(data.document);
            } else {
                this.showToast('Error', 'Failed to load opportunity details', 'error');
            }
        } catch (error) {
            console.error('Error loading opportunity:', error);
            this.showToast('Error', 'Failed to load opportunity details', 'error');
        }
    }

    showOpportunityDetails(opportunity) {
        const modal = new bootstrap.Modal(document.getElementById('viewOpportunityModal'));
        const title = document.getElementById('viewModalTitle');
        const body = document.getElementById('viewModalBody');

        title.textContent = opportunity.title;

        const salaryInfo = this.formatSalaryRange(opportunity.salary_range);
        const requirements = opportunity.requirements && opportunity.requirements.length > 0
            ? opportunity.requirements.map(req => `<li>${this.escapeHtml(req)}</li>`).join('')
            : '<li>No specific requirements listed</li>';

        body.innerHTML = `
            <div class="row g-3">
                <div class="col-md-8">
                    <h6 class="fw-bold">Company</h6>
                    <p>${this.escapeHtml(opportunity.company)}</p>

                    <h6 class="fw-bold">Description</h6>
                    <p>${this.escapeHtml(opportunity.description)}</p>

                    <h6 class="fw-bold">Requirements</h6>
                    <ul>${requirements}</ul>

                    ${opportunity.notes ? `
                        <h6 class="fw-bold">Notes</h6>
                        <p>${this.escapeHtml(opportunity.notes)}</p>
                    ` : ''}
                </div>
                <div class="col-md-4">
                    <h6 class="fw-bold">Details</h6>
                    <table class="table table-sm">
                        <tr><td><strong>Type:</strong></td><td>${opportunity.type.replace('_', ' ')}</td></tr>
                        <tr><td><strong>Status:</strong></td><td><span class="badge ${this.getStatusBadgeClass(opportunity.application_status)}">${opportunity.application_status}</span></td></tr>
                        <tr><td><strong>Remote:</strong></td><td>${opportunity.is_remote ? 'Yes' : 'No'}</td></tr>
                        ${opportunity.location ? `<tr><td><strong>Location:</strong></td><td>${this.escapeHtml(opportunity.location)}</td></tr>` : ''}
                        ${salaryInfo ? `<tr><td><strong>Salary:</strong></td><td class="salary-info">${salaryInfo}</td></tr>` : ''}
                        <tr><td><strong>Posted:</strong></td><td>${this.formatDate(opportunity.posted_at)}</td></tr>
                        ${opportunity.applied_at ? `<tr><td><strong>Applied:</strong></td><td>${this.formatDate(opportunity.applied_at)}</td></tr>` : ''}
                        <tr><td><strong>Added:</strong></td><td>${this.formatDate(opportunity.created_at)}</td></tr>
                    </table>

                    ${opportunity.source_url ? `
                        <a href="${opportunity.source_url}" target="_blank" class="btn btn-outline-primary btn-sm w-100 mt-2">
                            <i class="bi bi-box-arrow-up-right me-1"></i>View Original Posting
                        </a>
                    ` : ''}
                </div>
            </div>
        `;

        modal.show();
    }

    editOpportunity() {
        if (this.currentViewingOpportunity) {
            bootstrap.Modal.getInstance(document.getElementById('viewOpportunityModal')).hide();
            this.editOpportunityById(this.currentViewingOpportunity.id);
        }
    }

    async editOpportunityById(id) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/${id}`);
            const data = await response.json();

            if (data.success && data.document) {
                this.currentEditingOpportunity = data.document;
                this.populateForm(data.document);
                const modal = new bootstrap.Modal(document.getElementById('addOpportunityModal'));
                modal.show();
            } else {
                this.showToast('Error', 'Failed to load opportunity for editing', 'error');
            }
        } catch (error) {
            console.error('Error loading opportunity for edit:', error);
            this.showToast('Error', 'Failed to load opportunity for editing', 'error');
        }
    }

    populateForm(opportunity) {
        document.getElementById('modalTitle').textContent = 'Edit Opportunity';
        document.getElementById('opportunityId').value = opportunity.id;
        document.getElementById('title').value = opportunity.title;
        document.getElementById('company').value = opportunity.company;
        document.getElementById('description').value = opportunity.description;
        document.getElementById('type').value = opportunity.type;
        document.getElementById('applicationStatus').value = opportunity.application_status;
        document.getElementById('location').value = opportunity.location || '';
        document.getElementById('sourceUrl').value = opportunity.source_url || '';
        document.getElementById('isRemote').checked = opportunity.is_remote;
        document.getElementById('notes').value = opportunity.notes || '';

        // Handle requirements
        if (opportunity.requirements && opportunity.requirements.length > 0) {
            document.getElementById('requirements').value = opportunity.requirements.join('\n');
        }

        // Handle salary range
        if (opportunity.salary_range) {
            document.getElementById('salaryMin').value = opportunity.salary_range.min;
            document.getElementById('salaryMax').value = opportunity.salary_range.max;
            document.getElementById('salaryCurrency').value = opportunity.salary_range.currency;
            document.getElementById('salaryPeriod').value = opportunity.salary_range.period;
        }
    }

    resetForm() {
        document.getElementById('modalTitle').textContent = 'Add New Opportunity';
        document.getElementById('opportunityForm').reset();
        document.getElementById('opportunityId').value = '';
        document.getElementById('userId').value = this.currentUserId;
        document.getElementById('applicationStatus').value = 'SAVED';
        document.getElementById('salaryCurrency').value = 'USD';
        document.getElementById('salaryPeriod').value = 'YEARLY';
        this.currentEditingOpportunity = null;
    }

    async saveOpportunity() {
        const formData = this.getFormData();
        const isEdit = !!document.getElementById('opportunityId').value;

        try {
            let response;

            if (isEdit) {
                response = await fetch(`${this.apiBaseUrl}/${formData.id}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(formData)
                });
            } else {
                response = await fetch(this.apiBaseUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(formData)
                });
            }

            const data = await response.json();

            if (data.success) {
                this.showToast('Success',
                    isEdit ? 'Opportunity updated successfully' : 'Opportunity created successfully',
                    'success');

                bootstrap.Modal.getInstance(document.getElementById('addOpportunityModal')).hide();
                this.loadOpportunities();
            } else {
                this.showToast('Error', data.message || 'Failed to save opportunity', 'error');
            }
        } catch (error) {
            console.error('Error saving opportunity:', error);
            this.showToast('Error', 'Failed to save opportunity', 'error');
        }
    }

    getFormData() {
        const id = document.getElementById('opportunityId').value;
        const title = document.getElementById('title').value;
        const company = document.getElementById('company').value;
        const description = document.getElementById('description').value;
        const requirements = document.getElementById('requirements').value
            .split('\n')
            .map(req => req.trim())
            .filter(req => req.length > 0);
        const type = document.getElementById('type').value;
        const applicationStatus = document.getElementById('applicationStatus').value;
        const location = document.getElementById('location').value;
        const sourceUrl = document.getElementById('sourceUrl').value;
        const isRemote = document.getElementById('isRemote').checked;
        const notes = document.getElementById('notes').value;
        const salaryMin = parseFloat(document.getElementById('salaryMin').value);
        const salaryMax = parseFloat(document.getElementById('salaryMax').value);
        const salaryCurrency = document.getElementById('salaryCurrency').value;
        const salaryPeriod = document.getElementById('salaryPeriod').value;

        const formData = {
            user_id: this.currentUserId,
            title,
            company,
            description,
            requirements,
            type,
            status: 'ACTIVE',
            application_status: applicationStatus,
            is_remote: isRemote,
            location: location || undefined,
            source_url: sourceUrl || undefined,
            notes: notes || undefined
        };

        // Add salary range if both min and max are provided
        if (!isNaN(salaryMin) && !isNaN(salaryMax) && salaryMin <= salaryMax) {
            formData.salary_range = {
                min: salaryMin,
                max: salaryMax,
                currency: salaryCurrency,
                period: salaryPeriod
            };
        }

        if (id) {
            // For updates, include the ID and preserve the posted_at from the original opportunity
            formData.id = id;
            if (this.currentEditingOpportunity) {
                formData.posted_at = this.currentEditingOpportunity.posted_at;
                formData.applied_at = this.currentEditingOpportunity.applied_at;
            } else {
                // Fallback if we don't have the original opportunity data
                formData.posted_at = new Date().toISOString();
                formData.applied_at = null;
            }
        }

        return formData;
    }

    async deleteOpportunity() {
        if (this.currentViewingOpportunity) {
            bootstrap.Modal.getInstance(document.getElementById('viewOpportunityModal')).hide();
            this.deleteOpportunityById(this.currentViewingOpportunity.id);
        }
    }

    async deleteOpportunityById(id) {
        if (!confirm('Are you sure you want to delete this opportunity?')) {
            return;
        }

        try {
            const response = await fetch(`${this.apiBaseUrl}/${id}`, {
                method: 'DELETE'
            });

            const data = await response.json();

            if (data.success) {
                this.showToast('Success', 'Opportunity deleted successfully', 'success');
                this.loadOpportunities();
            } else {
                this.showToast('Error', data.message || 'Failed to delete opportunity', 'error');
            }
        } catch (error) {
            console.error('Error deleting opportunity:', error);
            this.showToast('Error', 'Failed to delete opportunity', 'error');
        }
    }

    showLoading(show) {
        const loadingIndicator = document.getElementById('loadingIndicator');
        const opportunitiesList = document.getElementById('opportunitiesList');

        if (show) {
            loadingIndicator.style.display = 'block';
            opportunitiesList.style.display = 'none';
        } else {
            loadingIndicator.style.display = 'none';
            opportunitiesList.style.display = 'block';
        }
    }

    updateOpportunityCount() {
        const count = this.opportunities.length;
        document.getElementById('opportunityCount').textContent = `${count} opportunities`;
    }

    showToast(title, message, type = 'info') {
        const toast = document.getElementById('toast');
        const toastIcon = document.getElementById('toastIcon');
        const toastTitle = document.getElementById('toastTitle');
        const toastMessage = document.getElementById('toastMessage');

        // Set icon and styling based on type
        switch (type) {
            case 'success':
                toastIcon.className = 'bi bi-check-circle-fill text-success me-2';
                break;
            case 'error':
                toastIcon.className = 'bi bi-exclamation-triangle-fill text-danger me-2';
                break;
            default:
                toastIcon.className = 'bi bi-info-circle-fill text-primary me-2';
        }

        toastTitle.textContent = title;
        toastMessage.textContent = message;

        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
    }

    getStatusBadgeClass(status) {
        const classes = {
            'SAVED': 'bg-secondary',
            'APPLIED': 'bg-primary',
            'SCREENING': 'bg-info',
            'INTERVIEWING': 'bg-warning',
            'OFFER': 'bg-success',
            'REJECTED': 'bg-danger',
            'WITHDRAWN': 'bg-dark',
            'ACCEPTED': 'bg-success'
        };
        return classes[status] || 'bg-secondary';
    }

    getTypeBadgeClass(type) {
        const classes = {
            'FULL_TIME': 'bg-primary',
            'PART_TIME': 'bg-info',
            'CONTRACT': 'bg-warning',
            'FREELANCE': 'bg-success',
            'INTERNSHIP': 'bg-light text-dark',
            'TEMPORARY': 'bg-secondary'
        };
        return classes[type] || 'bg-secondary';
    }

    formatSalaryRange(salaryRange) {
        if (!salaryRange) return null;

        const formatter = new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: salaryRange.currency,
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        });

        const min = formatter.format(salaryRange.min);
        const max = formatter.format(salaryRange.max);
        const period = salaryRange.period.toLowerCase();

        return `${min} - ${max} ${period}`;
    }

    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    }

    truncateText(text, maxLength) {
        if (text.length <= maxLength) return this.escapeHtml(text);
        return this.escapeHtml(text.substring(0, maxLength)) + '...';
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize the application when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new CareerCatalystApp();
});

// Global functions for HTML onclick handlers
function searchOpportunities() {
    window.app.searchOpportunities();
}

function clearFilters() {
    window.app.clearFilters();
}

function editOpportunity() {
    window.app.editOpportunity();
}

function deleteOpportunity() {
    window.app.deleteOpportunity();
}