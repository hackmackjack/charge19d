/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onWillStart } from "@odoo/owl";

/**
 * Student Dashboard Root Component
 *
 * This is the main component that renders the entire student dashboard.
 * It receives student data as a JSON string from the controller,
 * parses it, and manages the state for all visual sub-components
 * (profile, courses, progress charts, etc.).
 */
class StudentDashboard extends Component {
    static template = "charge_erp_core.StudentDashboardTemplate";
    static props = {
        data: { type: String },
    };

    /**
     * Formats an Odoo server datetime string into a human-readable format.
     * @param {string} dateTimeString - The ISO 8601 datetime string.
     * @returns {string} - Formatted date and time (e.g., "Oct 25, 2023, 5:30 PM").
     */
    formatDateTime(dateTimeString) {
        if (!dateTimeString) return "";
        const options = {
            year: 'numeric', month: 'short', day: 'numeric',
            hour: 'numeric', minute: '2-digit', hour12: true
        };
        try {
            const date = new Date(dateTimeString);
            return new Intl.DateTimeFormat('en-US', options).format(date);
        } catch (e) {
            console.error("Invalid date-time format:", dateTimeString, e);
            return dateTimeString; // Fallback to original string
        }
    }

    setup() {
        // Initialize a reactive state for the component.
        // When this state changes, the component will re-render automatically.
        this.state = useState({
            profile: {},
            academics: {},
            courses: [],
            sessions: [],
            library: [],
            notifications: [],
            progress: {},
        });

        // The onWillStart hook runs asynchronously before the component is
        // first rendered. It's the ideal place to fetch and process initial data.
        onWillStart(async () => {
            if (this.props.data) {
                try {
                    const parsedData = JSON.parse(this.props.data);

                    // Populate the state with data from the controller
                    this.state.profile = parsedData.profile || {};
                    this.state.academics = parsedData.academics || {};
                    this.state.courses = parsedData.courses || [];
                    this.state.library = parsedData.library || [];
                    this.state.notifications = parsedData.notifications || [];
                    this.state.progress = parsedData.progress || {};

                    // Format session dates before rendering
                    if (parsedData.sessions) {
                        this.state.sessions = parsedData.sessions.map(s => ({
                            ...s,
                            start: this.formatDateTime(s.start),
                        }));
                    }
                } catch (e) {
                    console.error("Failed to parse student dashboard data:", e);
                    // Keep state empty on error to avoid render failures
                }
            }
        });
    }
}

// Register the component in the public components registry so it can be
// used in QWeb templates with the t-component directive.
registry.category("public_components").add("charge_erp_core.StudentDashboard", StudentDashboard);