# Odoo User Creation Best Practices

This document outlines the standard procedures for creating demo users (`res.users`) within the `charge_erp_core` module. Following these guidelines ensures consistency, prevents unintended side effects, and aligns with modern Odoo development practices.

## 1. Programmatic User Creation via XML

To gain more control over the user creation process, especially for passing context, we do not use the standard `<record>` tag for `res.users`. Instead, we use the `<function>` tag to call the `create` method of the `res.users` model directly from XML.

This approach is mandatory for all new demo users.

### Preventing Password Reset Emails

To prevent Odoo from automatically sending a password reset email to a newly created demo user, always include `context="{'no_reset_password': True}"` in the `<function>` tag.

## 2. User Types and Group Assignment

Users are assigned to groups directly upon creation using the `groups_id` field. This is the modern, idempotent way to handle group membership and avoids the need for separate steps to add users to groups.

### Internal Users (e.g., Faculty)

Internal users must be part of `base.group_user`. To create an internal user, include both `base.group_user` and the specific application group (e.g., `charge_erp_core.group_op_faculty`) in the `groups_id` field.

**Example:**
```xml
<function model="res.users" name="create" eval="[{
    'name': 'Faculty Name',
    'partner_id': ref('partner_for_faculty'),
    'login': 'facultylogin',
    'password': 'demo',
    'groups_id': [(6, 0, [ref('base.group_user'), ref('charge_erp_core.group_op_faculty')])],
}]" context="{'no_reset_password': True}"/>
```

### Portal Users (e.g., Students)

Portal users must be part of `base.group_portal`. The legacy `share="True"` field is deprecated and **must not** be used. Instead, include `base.group_portal` and the specific application group (e.g., `charge_erp_core.group_op_student`) in the `groups_id` field.

**Example:**
```xml
<function model="res.users" name="create" eval="[{
    'name': 'Student Name',
    'partner_id': ref('partner_for_student'),
    'login': 'studentlogin',
    'password': 'demo',
    'groups_id': [(6, 0, [ref('base.group_portal'), ref('charge_erp_core.group_op_student')])],
}]" context="{'no_reset_password': True}"/>
```

## 3. Linking Users to Other Records

Since the `<function>` tag does not create an XML ID for the new user record, you cannot use `ref()` to link it in subsequent records (e.g., in an `op.student` or `op.faculty` record).

Instead, use a search on the `user_id` field, using the user's unique login to find the correct record.

**Example:**
```xml
<record id="demo_student_record" model="op.student">
    <field name="partner_id" ref="partner_for_student"/>
    <field name="user_id" model="res.users" search="[('login', '=', 'studentlogin')]"/>
    ...
</record>
```