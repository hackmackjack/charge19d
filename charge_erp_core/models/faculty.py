# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class OpFaculty(models.Model):
    _name = "op.faculty"
    _description = "Faculty"
    _inherits = {'res.partner': 'partner_id'}

    partner_id = fields.Many2one(
        'res.partner', string='Partner', required=True, ondelete='cascade')
    image_128 = fields.Image(related='partner_id.image_128', readonly=True)
    title = fields.Selection([
        ('mr', 'Mr.'),
        ('ms', 'Ms.'),
        ('mrs', 'Mrs.'),
        ('dr', 'Dr.'),
        ('prof', 'Prof.')
    ], string='Title')

    # Personal Information
    gender = fields.Selection([
        ('male', 'Male'), ('female', 'Female'), ('other', 'Other')
    ], 'Gender', required=True)
    birth_date = fields.Date('Date of Birth', required=True)
    blood_group = fields.Selection([
        ('A+', 'A+'), ('B+', 'B+'), ('O+', 'O+'), ('AB+', 'AB+'),
        ('A-', 'A-'), ('B-', 'B-'), ('O-', 'O-'), ('AB-', 'AB-')
    ], string='Blood Group')
    nationality = fields.Many2one('res.country', string='Nationality')
    visa_info = fields.Char('Visa Information')
    lang_ids = fields.Many2many(
        'res.lang', 'op_faculty_lang_rel', 'faculty_id', 'lang_id',
        string='Languages')
    emergency_contact_id = fields.Many2one(
        'res.partner', string='Emergency Contact', ondelete='set null')

    # Contact Information
    phone = fields.Char(string='Phone')
    mobile = fields.Char(string='Mobile')
    email = fields.Char(related='partner_id.email', readonly=False)
    street = fields.Char(related='partner_id.street', readonly=False)
    street2 = fields.Char(related='partner_id.street2', readonly=False)
    city = fields.Char(related='partner_id.city', readonly=False)
    state_id = fields.Many2one(
        'res.country.state', related='partner_id.state_id', readonly=False)
    zip = fields.Char(related='partner_id.zip', readonly=False)
    country_id = fields.Many2one(
        'res.country', related='partner_id.country_id', readonly=False)

    # Academics
    highest_qualification = fields.Char('Highest Qualification')
    specialization = fields.Char('Specialization / Expertise Area')
    previous_experience = fields.Text('Previous Experience')
    certifications = fields.Text('Certifications / Achievements')

    # Subjects & Courses
    department_id = fields.Many2one('op.department', string='Department')
    subject_ids = fields.Many2many(
        'op.subject', 'op_faculty_subject_rel',
        'faculty_id', 'subject_id', string='Subjects')
    course_ids = fields.Many2many(
        'op.course', 'course_faculty_rel', 'faculty_id', 'course_id', string='Courses')

    # Sessions
    session_ids = fields.One2many(
        'op.session', 'faculty_id', string="Sessions")

    # Library (Placeholder)
    library_card_id = fields.Many2one(
        'op.library.card', 'Library Card ID', ondelete='restrict')
    issued_book_ids = fields.One2many(
        'op.book.issue', 'faculty_id', 'Issued Books')

    # Health (Placeholder)
    medical_conditions = fields.Text('Medical Conditions')
    allergies = fields.Text('Allergies')
    emergency_instructions = fields.Text('Emergency Instructions')

    # HR Link
    employee_id = fields.Many2one(
        'hr.employee', string='Linked Employee',
        ondelete='restrict', copy=False)
    user_id = fields.Many2one(
        'res.users', string='System User',
        help="The user account linked to this faculty member for system access.",
        copy=False)

    # Smart Button Counts
    session_count = fields.Integer(
        string='Session Count', compute='_compute_session_count')
    subject_count = fields.Integer(
        string='Subject Count', compute='_compute_subject_count')
    library_count = fields.Integer(
        string='Library Items', compute='_compute_library_count')

    @api.constrains('birth_date')
    def _check_birthdate(self):
        for record in self:
            if record.birth_date and record.birth_date > fields.Date.today():
                raise ValidationError(
                    _("Birth Date can't be greater than current date!"))

    def _compute_session_count(self):
        for faculty in self:
            faculty.session_count = len(faculty.session_ids)

    def _compute_subject_count(self):
        for faculty in self:
            faculty.subject_count = len(faculty.subject_ids)

    def _compute_library_count(self):
        for faculty in self:
            faculty.library_count = len(faculty.issued_book_ids)

    def action_create_employee(self):
        for faculty in self:
            if not faculty.employee_id:
                hr_department = self.env['hr.department'].search(
                    [('name', '=', faculty.department_id.name)], limit=1)
                employee_vals = {
                    'name': faculty.name,
                    'work_email': faculty.email,
                    'work_phone': faculty.mobile or faculty.phone,
                    'work_contact_id': faculty.partner_id.id,
                    'department_id': hr_department.id if hr_department else False,
                }
                employee = self.env['hr.employee'].create(employee_vals)
                faculty.employee_id = employee.id
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'hr.employee',
            'res_id': self.employee_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_create_user(self):
        """
        Creates a new system user for each faculty member in the recordset.
        This method is designed to be idempotent and safe for bulk actions,
        and it follows the Odoo 19 best practice of separating user creation
        from group assignment.
        """
        faculty_group = self.env.ref('charge_erp_core.group_op_faculty')
        base_internal_group = self.env.ref('base.group_user')

        for faculty in self.filtered(lambda f: not f.user_id):
            # Step 1: Create the user without assigning groups.
            user = self.env['res.users'].create({
                'name': faculty.name,
                'login': faculty.email or faculty.name.lower().replace(' ', '.'),
                'partner_id': faculty.partner_id.id,
            })

            # Step 2: Assign groups using write().
            user.write({'group_ids': [(6, 0, [base_internal_group.id, faculty_group.id])]})

            # Step 3: Link the new user back to the faculty record.
            faculty.user_id = user.id
