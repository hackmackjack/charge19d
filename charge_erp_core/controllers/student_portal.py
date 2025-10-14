# -*- coding: utf-8 -*-
import json
from odoo import http, fields
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal


class StudentPortal(CustomerPortal):

    def _get_student(self):
        """Helper to get the student record for the current user."""
        return request.env['op.student'].search([
            ('user_id', '=', request.env.user.id)
        ], limit=1)

    def _get_faculty(self):
        """Helper to get the faculty record for the current user."""
        return request.env['op.faculty'].search([
            ('user_id', '=', request.env.user.id)
        ], limit=1)

    @http.route(['/my', '/my/home'], type='http', auth="user", website=True)
    def home(self, **kw):
        """
        Overrides the default portal homepage to render the new, enhanced
        student dashboard.

        This single method fetches all data required for the dashboard,
        serializes it to JSON, and passes it to the QWeb template
        for the OWL component to consume.
        """
        values = self._prepare_portal_layout_values()
        student = self._get_student()

        if student:
            # Fetch enrolled courses
            courses = request.env['op.course.enrollment'].search(
                [('student_id', '=', student.id)]).mapped('course_id')

            # Fetch the next 5 upcoming sessions
            sessions = request.env['op.session'].search([
                ('attendee_ids', 'in', [student.id]),
                ('start_datetime', '>=', fields.Datetime.now())
            ], order='start_datetime asc', limit=5)

            # Fetch currently issued library books
            issued_books = request.env['op.book.issue'].search(
                [('student_id', '=', student.id), ('state', '=', 'issue')])

            # Prepare data for serialization
            dashboard_data = {
                'profile': {
                    'name': student.name,
                    'program': student.program_id.name or 'N/A',
                    'roll_number': student.roll_number,
                    'email': student.email,
                    'phone': student.phone,
                    'image_url': f'/web/image/op.student/{student.id}/image_1920',
                },
                'academics': {
                    'program': student.program_id.name or 'N/A',
                    'batch': student.batch_id.name or 'N/A',
                    'admission_date': fields.Date.to_string(student.admission_date),
                },
                'courses': [
                    {'name': course.name, 'faculty': course.faculty_id.name or 'N/A'}
                    for course in courses
                ],
                'sessions': [
                    {
                        'course': session.course_id.name,
                        'start': fields.Datetime.to_string(session.start_datetime),
                    }
                    for session in sessions
                ],
                'library': [
                    {
                        'name': book.book_id.name,
                        'due_date': fields.Date.to_string(book.due_date),
                    }
                    for book in issued_books
                ],
                # Add placeholders for future implementation
                'notifications': [
                    {'id': 1, 'message': 'Your fee payment is due next week.', 'is_read': False},
                    {'id': 2, 'message': 'New materials uploaded for CS101.', 'is_read': True},
                ],
                'progress': {
                    'course_completion': 75,
                    'attendance': 92,
                }
            }
            values['student_dashboard_data'] = json.dumps(dashboard_data)

        else:
            # Fallback for non-student users (e.g., faculty)
            values['student_dashboard_data'] = json.dumps({})

        return request.render("charge_erp_core.portal_student_dashboard", values)