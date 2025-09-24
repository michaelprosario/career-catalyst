// Career Catalyst Frontend Application
class CareerCatalystApp {
    constructor() {
        this.apiBaseUrl = '/api/user-opportunities';
        this.jobSearchApiBaseUrl = '/api/job-search';
        this.currentUserId = 'demo-user-123'; // In production, this would come from authentication
        this.opportunities = [];
        this.jobSearchResults = [];
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

        // Job search form submission
        document.getElementById('jobSearchForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.performJobSearch();
        });

        // Export jobs button
        document.getElementById('exportJobsBtn').addEventListener('click', () => {
            this.exportJobSearchResults();
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
                this.showOpportunityDetailScreen(data.document);
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

    showOpportunityDetailScreen(opportunity) {
        // Show the opportunity detail tab navigation and switch to it
        document.getElementById('opportunity-detail-nav').style.display = 'block';
        const detailTab = new bootstrap.Tab(document.getElementById('opportunity-detail-tab'));
        detailTab.show();

        // Update the title
        document.getElementById('detailOpportunityTitle').textContent = opportunity.title;

        // Populate the content
        const content = document.getElementById('opportunityDetailContent');
        const salaryInfo = this.formatSalaryRange(opportunity.salary_range);
        const requirements = opportunity.requirements && opportunity.requirements.length > 0
            ? opportunity.requirements.map(req => `<li>${this.escapeHtml(req)}</li>`).join('')
            : '<li>No specific requirements listed</li>';

        content.innerHTML = `
            <div class="row g-4">
                <div class="col-lg-8">
                    <div class="card mb-4">
                        <div class="card-header">
                            <h5 class="card-title mb-0"><i class="bi bi-building me-2"></i>Company Information</h5>
                        </div>
                        <div class="card-body">
                            <h6>${this.escapeHtml(opportunity.company)}</h6>
                            <p class="text-muted mb-0">${opportunity.location ? this.escapeHtml(opportunity.location) : 'Location not specified'}</p>
                        </div>
                    </div>

                    <div class="card mb-4">
                        <div class="card-header">
                            <h5 class="card-title mb-0"><i class="bi bi-file-text me-2"></i>Job Description</h5>
                        </div>
                        <div class="card-body">
                            <p>${this.escapeHtml(opportunity.description)}</p>
                        </div>
                    </div>

                    <div class="card mb-4">
                        <div class="card-header">
                            <h5 class="card-title mb-0"><i class="bi bi-check2-square me-2"></i>Requirements</h5>
                        </div>
                        <div class="card-body">
                            <ul>${requirements}</ul>
                        </div>
                    </div>

                    ${opportunity.notes ? `
                        <div class="card mb-4">
                            <div class="card-header">
                                <h5 class="card-title mb-0"><i class="bi bi-sticky me-2"></i>My Notes</h5>
                            </div>
                            <div class="card-body">
                                <p>${this.escapeHtml(opportunity.notes)}</p>
                            </div>
                        </div>
                    ` : ''}
                </div>

                <div class="col-lg-4">
                    <div class="card mb-4">
                        <div class="card-header">
                            <h5 class="card-title mb-0"><i class="bi bi-info-circle me-2"></i>Job Details</h5>
                        </div>
                        <div class="card-body">
                            <table class="table table-sm table-borderless">
                                <tr><td><strong>Type:</strong></td><td>${opportunity.type.replace('_', ' ')}</td></tr>
                                <tr><td><strong>Status:</strong></td><td><span class="badge ${this.getStatusBadgeClass(opportunity.application_status)}">${opportunity.application_status}</span></td></tr>
                                <tr><td><strong>Remote:</strong></td><td>${opportunity.is_remote ? 'Yes' : 'No'}</td></tr>
                                ${salaryInfo ? `<tr><td><strong>Salary:</strong></td><td class="salary-info">${salaryInfo}</td></tr>` : ''}
                                <tr><td><strong>Posted:</strong></td><td>${this.formatDate(opportunity.posted_at)}</td></tr>
                                ${opportunity.applied_at ? `<tr><td><strong>Applied:</strong></td><td>${this.formatDate(opportunity.applied_at)}</td></tr>` : ''}
                                <tr><td><strong>Added:</strong></td><td>${this.formatDate(opportunity.created_at)}</td></tr>
                            </table>
                        </div>
                    </div>

                    <div class="card mb-4">
                        <div class="card-header">
                            <h5 class="card-title mb-0"><i class="bi bi-tools me-2"></i>Actions</h5>
                        </div>
                        <div class="card-body">
                            <div class="d-grid gap-2">
                                <button class="btn btn-primary" id="draftCoverLetterBtn">
                                    <i class="bi bi-file-earmark-text me-2"></i>Draft Cover Letter
                                </button>
                                <button class="btn btn-outline-primary" id="editOpportunityBtn" data-opportunity-id="${opportunity.id}">
                                    <i class="bi bi-pencil me-2"></i>Edit Opportunity
                                </button>
                                ${opportunity.source_url ? `
                                    <a href="${opportunity.source_url}" target="_blank" class="btn btn-outline-secondary">
                                        <i class="bi bi-box-arrow-up-right me-2"></i>View Original Posting
                                    </a>
                                ` : ''}
                                <button class="btn btn-outline-danger" id="deleteOpportunityBtn">
                                    <i class="bi bi-trash me-2"></i>Delete
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Add event listeners after the HTML is inserted
        setTimeout(() => {
            const draftBtn = document.getElementById('draftCoverLetterBtn');
            const editBtn = document.getElementById('editOpportunityBtn');
            const deleteBtn = document.getElementById('deleteOpportunityBtn');

            if (draftBtn) {
                draftBtn.addEventListener('click', () => this.draftCoverLetter());
            }

            if (editBtn) {
                editBtn.addEventListener('click', () => {
                    const opportunityId = editBtn.getAttribute('data-opportunity-id');
                    this.editOpportunityById(opportunityId);
                });
            }

            if (deleteBtn) {
                deleteBtn.addEventListener('click', () => this.deleteOpportunity());
            }
        }, 0);
    }

    backToOpportunities() {
        // Switch back to the opportunities tab and hide the detail tab
        const opportunitiesTab = new bootstrap.Tab(document.getElementById('opportunities-tab'));
        opportunitiesTab.show();
        document.getElementById('opportunity-detail-nav').style.display = 'none';
        this.currentViewingOpportunity = null;
    }

    draftCoverLetter() {
        if (!this.currentViewingOpportunity) {
            this.showToast('Error', 'No opportunity selected for cover letter generation', 'error');
            return;
        }

        // For now, show a placeholder functionality
        // In a real implementation, this would integrate with AI/template services
        const coverLetterContent = `Dear Hiring Manager,

I am writing to express my strong interest in the ${this.currentViewingOpportunity.title} position at ${this.currentViewingOpportunity.company}.

${this.currentViewingOpportunity.description ? 'Based on the job description, I believe my skills and experience align well with your requirements.' : ''}

${this.currentViewingOpportunity.requirements && this.currentViewingOpportunity.requirements.length > 0 ? `I am particularly excited about this opportunity because of my experience with: ${this.currentViewingOpportunity.requirements.slice(0, 3).join(', ')}.` : ''}

I would welcome the opportunity to discuss how my background and enthusiasm can contribute to your team's success.

Thank you for considering my application.

Best regards,
[Your Name]`;

        // Create a modal to show the cover letter draft
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Cover Letter Draft - ${this.escapeHtml(this.currentViewingOpportunity.title)}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <textarea class="form-control" rows="15" id="coverLetterText">${coverLetterContent}</textarea>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                        <button type="button" class="btn btn-primary" onclick="app.copyCoverLetter()">
                            <i class="bi bi-clipboard me-1"></i>Copy to Clipboard
                        </button>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();

        // Clean up when modal is closed
        modal.addEventListener('hidden.bs.modal', () => {
            document.body.removeChild(modal);
        });

        this.showToast('Success', 'Cover letter draft generated! You can edit and copy it.', 'success');
    }

    copyCoverLetter() {
        const coverLetterText = document.getElementById('coverLetterText');
        if (coverLetterText) {
            coverLetterText.select();
            navigator.clipboard.writeText(coverLetterText.value).then(() => {
                this.showToast('Success', 'Cover letter copied to clipboard!', 'success');
            }).catch(() => {
                this.showToast('Error', 'Failed to copy to clipboard', 'error');
            });
        }
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

    // Job Search Methods
    async performJobSearch() {
        const searchTerm = document.getElementById('jobSearchTerm').value.trim();
        const location = document.getElementById('jobSearchLocation').value.trim();
        const resultsWanted = parseInt(document.getElementById('jobSearchResults').value);

        if (!searchTerm || !location) {
            this.showToast('Error', 'Please enter both search term and location', 'error');
            return;
        }

        try {
            this.showJobSearchLoading(true);

            const response = await fetch(`${this.jobSearchApiBaseUrl}/search`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    search_term: searchTerm,
                    location: location,
                    results_wanted: resultsWanted
                })
            });

            const data = await response.json();

            if (data.success) {
                this.jobSearchResults = data.results || [];
                this.renderJobSearchResults();
                this.showToast('Success', `Found ${data.total} job opportunities`, 'success');
            } else {
                this.showToast('Error', data.message || 'Job search failed', 'error');
                this.showNoJobResults(true);
            }
        } catch (error) {
            console.error('Job search error:', error);
            this.showToast('Error', 'Job search failed', 'error');
            this.showNoJobResults(true);
        } finally {
            this.showJobSearchLoading(false);
        }
    }

    renderJobSearchResults() {
        const container = document.getElementById('jobSearchResultsList');
        const noResults = document.getElementById('noJobResults');
        const exportSection = document.getElementById('exportSection');

        if (this.jobSearchResults.length === 0) {
            container.innerHTML = '';
            noResults.style.display = 'block';
            exportSection.style.display = 'none';
            return;
        }

        noResults.style.display = 'none';
        exportSection.style.display = 'flex';

        container.innerHTML = this.jobSearchResults.map(job =>
            this.createJobResultCard(job)).join('');
    }

    createJobResultCard(job) {
        const datePosted = job.date_posted ?
            `<small class="text-muted"><i class="bi bi-calendar me-1"></i>${this.formatJobDate(job.date_posted)}</small>` : '';

        const remoteTag = job.is_remote ?
            '<span class="badge bg-success me-1">Remote</span>' : '';

        const description = job.description && job.description !== 'nan' ?
            this.truncateText(job.description, 150) : 'No description available';

        return `
            <div class="col-md-6">
                <div class="card job-result-card h-100">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start mb-2">
                            <h5 class="card-title mb-0">${this.escapeHtml(job.title)}</h5>
                            ${remoteTag}
                        </div>
                        <h6 class="card-subtitle mb-2 text-muted">${this.escapeHtml(job.company)}</h6>

                        ${job.location ? `<p class="card-text small mb-1"><i class="bi bi-geo-alt me-1"></i>${this.escapeHtml(job.location)}</p>` : ''}
                        ${datePosted}

                        <p class="card-text mt-2">${description}</p>

                        <div class="d-flex justify-content-between align-items-center mt-3">
                            <div>
                                ${job.job_url ? `<a href="${job.job_url}" target="_blank" class="btn btn-sm btn-outline-primary external-link">
                                    <i class="bi bi-box-arrow-up-right me-1"></i>View Job
                                </a>` : ''}
                            </div>
                            <button class="btn btn-sm btn-success bookmark-btn" onclick="app.bookmarkJob('${this.escapeJobData(job)}')">
                                <i class="bi bi-bookmark-plus me-1"></i>Bookmark
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    escapeJobData(job) {
        try {
            const jobData = {
                title: job.title,
                company: job.company,
                location: job.location,
                job_url: job.job_url,
                is_remote: job.is_remote,
                description: job.description && job.description !== 'nan' ? job.description : null
            };

            // Use encodeURIComponent to handle Unicode characters, then btoa for base64 encoding
            return btoa(encodeURIComponent(JSON.stringify(jobData)));
        } catch (error) {
            console.error('Error encoding job data:', error);
            // Fallback: use a simplified version without description if encoding fails
            return btoa(encodeURIComponent(JSON.stringify({
                title: job.title || 'Unknown Title',
                company: job.company || 'Unknown Company',
                location: job.location || '',
                job_url: job.job_url || null,
                is_remote: job.is_remote || false,
                description: null // Skip description if it causes encoding issues
            })));
        }
    }

    async bookmarkJob(encodedJobData) {
        try {
            // Decode the base64 and then decode the URI component
            const job = JSON.parse(decodeURIComponent(atob(encodedJobData)));

            const response = await fetch(`${this.jobSearchApiBaseUrl}/bookmark`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    user_id: this.currentUserId,
                    job_title: job.title,
                    company: job.company,
                    job_url: job.job_url,
                    location: job.location,
                    is_remote: job.is_remote,
                    description: job.description,
                    notes: `Bookmarked from job search on ${new Date().toLocaleDateString()}`
                })
            });

            const data = await response.json();

            if (data.success) {
                this.showToast('Success', 'Job bookmarked successfully!', 'success');
                // Refresh opportunities if we're on that tab
                if (document.getElementById('opportunities-tab').classList.contains('active')) {
                    this.loadOpportunities();
                }
            } else {
                this.showToast('Error', data.message || 'Failed to bookmark job', 'error');
            }
        } catch (error) {
            console.error('Bookmark error:', error);
            this.showToast('Error', 'Failed to bookmark job', 'error');
        }
    }

    showJobSearchLoading(show) {
        const loading = document.getElementById('jobSearchLoading');
        const resultsList = document.getElementById('jobSearchResultsList');
        const noResults = document.getElementById('noJobResults');

        if (show) {
            loading.style.display = 'block';
            resultsList.style.display = 'none';
            noResults.style.display = 'none';
        } else {
            loading.style.display = 'none';
            resultsList.style.display = 'block';
        }
    }

    showNoJobResults(show) {
        const noResults = document.getElementById('noJobResults');
        const resultsList = document.getElementById('jobSearchResultsList');

        if (show) {
            noResults.style.display = 'block';
            resultsList.style.display = 'none';
        } else {
            noResults.style.display = 'none';
            resultsList.style.display = 'block';
        }
    }

    formatJobDate(dateString) {
        try {
            const date = new Date(dateString);
            return date.toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'short',
                day: 'numeric'
            });
        } catch {
            return dateString;
        }
    }

    showJobSearchSection() {
        // Switch to the job search tab
        const jobSearchTab = document.getElementById('job-search-tab');
        const tab = new bootstrap.Tab(jobSearchTab);
        tab.show();
    }

    exportJobSearchResults() {
        if (!this.jobSearchResults || this.jobSearchResults.length === 0) {
            this.showToast('Error', 'No job search results to export', 'error');
            return;
        }

        try {
            // Generate CSV content
            const csvContent = this.generateJobSearchCSV();

            // Create download
            this.downloadCSV(csvContent, 'job-search-results.csv');

            this.showToast('Success', `Exported ${this.jobSearchResults.length} job results to CSV`, 'success');
        } catch (error) {
            console.error('Error exporting job search results:', error);
            this.showToast('Error', 'Failed to export job search results', 'error');
        }
    }

    generateJobSearchCSV() {
        // Define CSV headers
        const headers = [
            'Title',
            'Company',
            'Location',
            'Remote',
            'Date Posted',
            'Description',
            'Job URL'
        ];

        // Convert job data to CSV rows
        const rows = this.jobSearchResults.map(job => [
            this.cleanCSVValue(job.title || ''),
            this.cleanCSVValue(job.company || ''),
            this.cleanCSVValue(job.location || ''),
            job.is_remote ? 'Yes' : 'No',
            job.date_posted || '',
            this.cleanCSVValue(job.description && job.description !== 'nan' ? job.description : ''),
            job.job_url || ''
        ]);

        // Combine headers and rows
        const allRows = [headers, ...rows];

        // Convert to CSV format
        return allRows.map(row =>
            row.map(field => `"${field.replace(/"/g, '""')}"`).join(',')
        ).join('\n');
    }

    cleanCSVValue(value) {
        if (!value || value === 'nan') return '';

        // Remove HTML tags and excessive whitespace
        return value
            .replace(/<[^>]*>/g, '')
            .replace(/\s+/g, ' ')
            .trim();
    }

    downloadCSV(csvContent, filename) {
        // Create blob with CSV content
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });

        // Create download link
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);

        link.setAttribute('href', url);
        link.setAttribute('download', filename);
        link.style.visibility = 'hidden';

        // Add to DOM, click, and remove
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        // Clean up object URL
        URL.revokeObjectURL(url);
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