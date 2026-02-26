/**
 * LLM Query Handler with Progressive Enhancement
 * Handles DeepSeek R1 queries with fast initial response + deep reasoning
 */

class LLMHandler {
    constructor(apiUrl) {
        this.apiUrl = apiUrl;
        this.activeJobs = new Map();
        this.pollingIntervals = new Map();
    }

    /**
     * Send query with AI enhancement
     */
    async sendQuery(query, onInitialResponse, onEnhancedResponse) {
        try {
            // Send query to backend
            const response = await fetch(`${this.apiUrl}/query`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    query: query,
                    use_ai: true 
                })
            });

            const data = await response.json();

            // Handle initial response
            if (data.type === 'fast') {
                // Simple query - got final answer immediately
                onInitialResponse(data);
                return { type: 'complete', data };
            }

            if (data.type === 'progressive') {
                // Complex query - got quick answer, deep reasoning in progress
                onInitialResponse(data);

                // Start polling for enhanced answer
                if (data.job_id) {
                    this.pollForEnhancedAnswer(
                        data.job_id,
                        onEnhancedResponse
                    );
                }

                return { type: 'progressive', data };
            }

            if (data.error) {
                throw new Error(data.error);
            }

            return { type: 'complete', data };

        } catch (error) {
            console.error('Query error:', error);
            throw error;
        }
    }

    /**
     * Poll for enhanced answer from DeepSeek R1
     */
    pollForEnhancedAnswer(jobId, callback) {
        // Clear any existing polling for this job
        if (this.pollingIntervals.has(jobId)) {
            clearInterval(this.pollingIntervals.get(jobId));
        }

        // Poll every 2 seconds
        const interval = setInterval(async () => {
            try {
                const response = await fetch(`${this.apiUrl}/query-status/${jobId}`);
                const status = await response.json();

                if (status.status === 'complete') {
                    // Got enhanced answer!
                    clearInterval(interval);
                    this.pollingIntervals.delete(jobId);
                    callback(status);
                } else if (status.status === 'error') {
                    // Error occurred
                    clearInterval(interval);
                    this.pollingIntervals.delete(jobId);
                    callback({ error: status.error });
                }
                // If still processing, keep polling

            } catch (error) {
                console.error('Polling error:', error);
                clearInterval(interval);
                this.pollingIntervals.delete(jobId);
            }
        }, 2000);

        this.pollingIntervals.set(jobId, interval);
    }

    /**
     * Cancel polling for a job
     */
    cancelJob(jobId) {
        if (this.pollingIntervals.has(jobId)) {
            clearInterval(this.pollingIntervals.get(jobId));
            this.pollingIntervals.delete(jobId);
        }
    }

    /**
     * Clear all active jobs
     */
    clearAllJobs() {
        this.pollingIntervals.forEach((interval) => clearInterval(interval));
        this.pollingIntervals.clear();
    }
}

// Export for use in renderer
if (typeof module !== 'undefined' && module.exports) {
    module.exports = LLMHandler;
}
