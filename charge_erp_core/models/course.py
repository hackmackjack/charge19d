# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

class OpCourse(models.Model):
    """
    Represents an academic course offered by the institution. Each course has a
    unique code and can be associated with a department and have a parent
    course to create a hierarchy.
    """
    _name = "op.course"
    _description = "Course"

    name = fields.Char('Name', required=True, translate=True)
    code = fields.Char('Code', size=16, required=True)
    parent_id = fields.Many2one('op.course', 'Parent Course', index=True, ondelete='cascade')
    department_id = fields.Many2one('op.department', string='Department')
    evaluation_type = fields.Selection(
        [('normal', 'Normal'), ('GPA', 'GPA'),
         ('CWA', 'CWA'), ('CCE', 'CCE')],
        'Evaluation Type', default="normal", required=True)
    active = fields.Boolean(default=True)
    session_ids = fields.One2many(
        'op.session', 'course_id', string="Sessions")
    enrollment_ids = fields.One2many(
        'op.course.enrollment', 'course_id',
        string='Enrollments')
    faculty_ids = fields.Many2many(
        'op.faculty', 'course_faculty_rel', 'course_id', 'faculty_id', string='Faculties')
    session_count = fields.Integer(
        string='Session Count', compute='_compute_session_count')

    def _compute_session_count(self):
        for course in self:
            course.session_count = len(course.session_ids)

    @api.constrains('parent_id')
    def _check_category_recursion(self):
        if not self._check_recursion():
            raise ValidationError(_('You cannot create recursive courses.'))

    @api.constrains('code')
    def _check_unique_code(self):
        """Ensures that the course code is unique across all courses."""
        for course in self:
            if course.code:
                domain = [('code', '=', course.code), ('id', '!=', course.id)]
                if self.search_count(domain):
                    raise ValidationError(_('Course Code must be unique!'))
