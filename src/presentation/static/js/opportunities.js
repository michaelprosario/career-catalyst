// Opportunities page functionality

// Get reference to CareerCatalyst utilities
const { showAlert, showLoading, apiRequest, validateForm, clearFormValidation, API_BASE_URL, DEFAULT_USER_ID } = window.CareerCatalyst;

// DOM elements
let addOpportunityModal, editOpportunityModal, viewOpportunityModal;
let addOpportunityForm, editOpportunityForm;

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize modal references
    addOpportunityModal = new bootstrap.Modal(document.getElementById('addOpportunityModal'));
    editOpportunityModal = new bootstrap.Modal(document.getElementById('editOpportunityModal'));
    viewOpportunityModal = new bootstrap.Modal(document.getElementById('viewOpportunityModal'));
    
    addOpportunityForm = document.getElementById('addOpportunityForm');
    editOpportunityForm = document.getElementById('editOpportunityForm');
    
    // Set up form handlers
    setupFormHandlers();
});

function setupFormHandlers() {
    // Add opportunity form handler
    if (addOpportunityForm) {
        addOpportunityForm.addEventListener('submit', handleAddOpportunity);
    }
    
    // Edit opportunity form handler
    if (editOpportunityForm) {
        editOpportunityForm.addEventListener('submit', handleEditOpportunity);
    }
}

// Add opportunity handler
async function handleAddOpportunity(e) {
    e.preventDefault();
    
    const submitBtn = e.target.querySelector('button[type="submit"]');
    
    if (!validateForm(addOpportunityForm)) {
        return;
    }
    
    showLoading(submitBtn);
    
    try {
        const formData = new FormData(addOpportunityForm);
        const opportunityData = {
            user_id: DEFAULT_USER_ID,
            title: formData.get('title'),
            company: formData.get('company'),
            description: formData.get('description'),
            location: formData.get('location') || null,
            type: formData.get('type'),
            application_status: formData.get('application_status'),
            is_remote: formData.has('is_remote'),
            source_url: formData.get('source_url') || null,
            notes: formData.get('notes') || null,
            requirements: [] // TODO: Add requirements handling
        };
        
        const response = await apiRequest(`${API_BASE_URL}/`, {
            method: 'POST',
            body: JSON.stringify(opportunityData)
        });
        
        if (response.success) {
            showAlert('Opportunity added successfully!', 'success');
            addOpportunityModal.hide();
            addOpportunityForm.reset();
            clearFormValidation(addOpportunityForm);
            
            // Reload the page to show the new opportunity
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            showAlert(response.error || 'Failed to add opportunity', 'danger');
        }
    } catch (error) {
        console.error('Error adding opportunity:', error);
        showAlert('An error occurred while adding the opportunity', 'danger');
    } finally {
        showLoading(submitBtn, false);
    }
}

// Edit opportunity handler
async function handleEditOpportunity(e) {
    e.preventDefault();
    
    const submitBtn = e.target.querySelector('button[type="submit"]');
    
    if (!validateForm(editOpportunityForm)) {
        return;
    }
    
    showLoading(submitBtn);
    
    try {
        const formData = new FormData(editOpportunityForm);
        const opportunityId = formData.get('opportunity_id');
        
        const opportunityData = {
            title: formData.get('title'),
            company: formData.get('company'),
            description: formData.get('description'),
            location: formData.get('location') || null,
            type: formData.get('type'),
            application_status: formData.get('application_status'),
            is_remote: formData.has('is_remote'),
            source_url: formData.get('source_url') || null,
            notes: formData.get('notes') || null
        };
        
        const response = await apiRequest(`${API_BASE_URL}/${opportunityId}`, {
            method: 'PUT',
            body: JSON.stringify(opportunityData)
        });
        
        if (response.success) {
            showAlert('Opportunity updated successfully!', 'success');
            editOpportunityModal.hide();
            
            // Reload the page to show the updated opportunity
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            showAlert(response.error || 'Failed to update opportunity', 'danger');
        }
    } catch (error) {
        console.error('Error updating opportunity:', error);
        showAlert('An error occurred while updating the opportunity', 'danger');
    } finally {
        showLoading(submitBtn, false);
    }
}

// View opportunity
async function viewOpportunity(opportunityId) {
    try {
        const response = await apiRequest(`${API_BASE_URL}/${opportunityId}`);
        
        if (response.success) {
            const opportunity = response.user_opportunity;
            displayOpportunityDetails(opportunity);
            viewOpportunityModal.show();
        } else {
            showAlert('Failed to load opportunity details', 'danger');
        }
    } catch (error) {
        console.error('Error viewing opportunity:', error);
        showAlert('An error occurred while loading the opportunity', 'danger');
    }
}

// Display opportunity details in view modal
function displayOpportunityDetails(opportunity) {
    const content = document.getElementById('viewOpportunityContent');
    
    const html = `
        <div class="row">
            <div class="col-md-6">
                <h5>${opportunity.title}</h5>
                <p class="text-muted">${opportunity.company}</p>
            </div>
            <div class="col-md-6 text-end">
                <span class="badge bg-${window.CareerCatalyst.getStatusBadgeClass(opportunity.application_status)} fs-6">
                    ${window.CareerCatalyst.formatStatus(opportunity.application_status)}
                </span>
            </div>
        </div>
        
        <hr>
        
        <div class="row mb-3">
            <div class="col-md-4">
                <strong>Location:</strong><br>
                ${opportunity.location || 'Not specified'}
                ${opportunity.is_remote ? '<span class="badge bg-info ms-1">Remote</span>' : ''}
            </div>
            <div class="col-md-4">
                <strong>Type:</strong><br>
                ${window.CareerCatalyst.formatStatus(opportunity.type)}
            </div>
            <div class="col-md-4">
                <strong>Status:</strong><br>
                ${window.CareerCatalyst.formatStatus(opportunity.status)}
            </div>
        </div>
        
        ${opportunity.description ? `
        <div class="mb-3">
            <strong>Description:</strong>
            <div class="mt-2 p-3 bg-light rounded">
                ${opportunity.description.replace(/\n/g, '<br>')}
            </div>
        </div>
        ` : ''}
        
        ${opportunity.notes ? `
        <div class="mb-3">
            <strong>Notes:</strong>
            <div class="mt-2 p-3 bg-light rounded">
                ${opportunity.notes.replace(/\n/g, '<br>')}
            </div>
        </div>
        ` : ''}
        
        ${opportunity.source_url ? `
        <div class="mb-3">
            <strong>Source:</strong><br>
            <a href="${opportunity.source_url}" target="_blank" class="btn btn-outline-primary btn-sm">
                <i class="bi bi-box-arrow-up-right me-1"></i>
                View Original Posting
            </a>
        </div>
        ` : ''}
        
        <div class="row">
            <div class="col-md-6">
                <strong>Created:</strong><br>
                <small class="text-muted">${window.CareerCatalyst.formatDate(opportunity.created_at)}</small>
            </div>
            <div class="col-md-6">
                <strong>Last Updated:</strong><br>
                <small class="text-muted">${window.CareerCatalyst.formatDate(opportunity.updated_at)}</small>
            </div>
        </div>
        
        ${opportunity.applied_at ? `
        <div class="mt-2">
            <strong>Applied:</strong><br>
            <small class="text-muted">${window.CareerCatalyst.formatDate(opportunity.applied_at)}</small>
        </div>
        ` : ''}
    `;
    
    content.innerHTML = html;
}

// Edit opportunity
async function editOpportunity(opportunityId) {
    try {
        const response = await apiRequest(`${API_BASE_URL}/${opportunityId}`);
        
        if (response.success) {
            const opportunity = response.user_opportunity;
            populateEditForm(opportunity);
            editOpportunityModal.show();
        } else {
            showAlert('Failed to load opportunity details', 'danger');
        }
    } catch (error) {
        console.error('Error loading opportunity for edit:', error);
        showAlert('An error occurred while loading the opportunity', 'danger');
    }
}

// Populate edit form with opportunity data
function populateEditForm(opportunity) {
    document.getElementById('edit_opportunity_id').value = opportunity.id;
    document.getElementById('edit_title').value = opportunity.title;
    document.getElementById('edit_company').value = opportunity.company;
    document.getElementById('edit_description').value = opportunity.description;
    document.getElementById('edit_location').value = opportunity.location || '';
    document.getElementById('edit_type').value = opportunity.type;
    document.getElementById('edit_application_status').value = opportunity.application_status;
    document.getElementById('edit_is_remote').checked = opportunity.is_remote;
    document.getElementById('edit_source_url').value = opportunity.source_url || '';
    document.getElementById('edit_notes').value = opportunity.notes || '';
}

// Delete opportunity
async function deleteOpportunity(opportunityId, opportunityTitle) {
    const confirmed = confirm(`Are you sure you want to delete "${opportunityTitle}"? This action cannot be undone.`);
    
    if (!confirmed) {
        return;
    }
    
    try {
        const response = await apiRequest(`${API_BASE_URL}/${opportunityId}`, {
            method: 'DELETE'
        });
        
        if (response.success) {
            showAlert('Opportunity deleted successfully!', 'success');
            
            // Remove the row from the table
            const row = document.querySelector(`tr[data-opportunity-id="${opportunityId}"]`);
            if (row) {
                row.remove();
            } else {
                // If no data attribute, reload the page
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            }
        } else {
            showAlert(response.error || 'Failed to delete opportunity', 'danger');
        }
    } catch (error) {
        console.error('Error deleting opportunity:', error);
        showAlert('An error occurred while deleting the opportunity', 'danger');
    }
}

// Make functions globally available
window.viewOpportunity = viewOpportunity;
window.editOpportunity = editOpportunity;
window.deleteOpportunity = deleteOpportunity;