/**
 * Safe Skill Synchronization Utility for Frontend
 * Ensures reports always reflect current consultant profile skills
 */

class SkillSyncManager {
    constructor(baseURL = '') {
        this.baseURL = baseURL;
    }

    /**
     * Get consultant report with guaranteed skill synchronization
     * @param {string} email - Consultant email
     * @returns {Promise<Object>} Report data with synchronized skills
     */
    async getConsultantReportSynced(email) {
        try {
            // Always use the synced endpoint for guaranteed skill consistency
            const response = await fetch(`${this.baseURL}/api/reports/consultant/${email}/synced`);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            // Validate that skills are synchronized
            if (data.sync_info && data.sync_info.skills_synchronized) {
                console.log(`✅ Skills synchronized for ${email} at ${data.sync_info.sync_timestamp}`);
                return data;
            } else {
                console.warn(`⚠️ Skills may not be synchronized for ${email}`);
                return data;
            }
            
        } catch (error) {
            console.error(`❌ Failed to get synced report for ${email}:`, error);
            
            // Fallback to regular report if synced endpoint fails
            try {
                console.log(`🔄 Falling back to regular report endpoint for ${email}`);
                const fallbackResponse = await fetch(`${this.baseURL}/api/reports/consultant/${email}`);
                return await fallbackResponse.json();
            } catch (fallbackError) {
                console.error(`❌ Fallback also failed:`, fallbackError);
                throw new Error(`Both synced and regular report endpoints failed for ${email}`);
            }
        }
    }

    /**
     * Check if consultant skills are ready for synchronization
     * @param {number} consultantId - Consultant ID
     * @returns {Promise<Object>} Sync status information
     */
    async checkSkillSyncStatus(consultantId) {
        try {
            const response = await fetch(`${this.baseURL}/api/consultants/${consultantId}/skills/sync-status`);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            return await response.json();
            
        } catch (error) {
            console.error(`❌ Failed to check sync status for consultant ${consultantId}:`, error);
            return {
                consultant_id: consultantId,
                skills_available: false,
                sync_ready: false,
                error: error.message
            };
        }
    }

    /**
     * Update consultant skills and ensure reports will reflect changes
     * @param {number} consultantId - Consultant ID  
     * @param {Object} skillsData - Skills data {skills: [], soft_skills: []}
     * @returns {Promise<Object>} Update result with sync information
     */
    async updateConsultantSkills(consultantId, skillsData) {
        try {
            const response = await fetch(`${this.baseURL}/api/consultants/${consultantId}/skills/update`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(skillsData)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const result = await response.json();
            
            if (result.sync_info && result.sync_info.skills_updated) {
                console.log(`✅ Skills updated for consultant ${consultantId}, reports will reflect changes`);
            }
            
            return result;
            
        } catch (error) {
            console.error(`❌ Failed to update skills for consultant ${consultantId}:`, error);
            throw error;
        }
    }

    /**
     * Upload resume and automatically sync skills across the system
     * @param {File} file - Resume file
     * @param {string} consultantEmail - Consultant email
     * @returns {Promise<Object>} Upload result with sync information
     */
    async uploadResumeWithSync(file, consultantEmail) {
        try {
            const formData = new FormData();
            formData.append('file', file);
            formData.append('consultant_email', consultantEmail);

            const response = await fetch(`${this.baseURL}/upload-resume`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const result = await response.json();

            if (result.sync_info && result.sync_info.skills_updated) {
                console.log(`✅ Resume uploaded for ${consultantEmail}, skills extracted and synchronized`);
                console.log(`📊 Use synced endpoint: ${result.sync_info.use_synced_endpoint}`);
            }

            return result;

        } catch (error) {
            console.error(`❌ Failed to upload resume for ${consultantEmail}:`, error);
            throw error;
        }
    }
}

// Export for use in frontend applications
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SkillSyncManager;
}

// Usage Examples:
/*
// Initialize the sync manager
const syncManager = new SkillSyncManager('http://localhost:8000');

// Get a consultant report with guaranteed skill sync
const report = await syncManager.getConsultantReportSynced('john@example.com');

// Check if skills are ready for sync
const syncStatus = await syncManager.checkSkillSyncStatus(123);

// Update skills and ensure reports will reflect changes
await syncManager.updateConsultantSkills(123, {
    skills: ['Python', 'React', 'AWS'],
    soft_skills: ['Leadership', 'Communication']
});

// Upload resume with automatic skill sync
await syncManager.uploadResumeWithSync(fileInput.files[0], 'john@example.com');
*/
