# Odoo User Creation Best Practices

This document outlines the standard procedures for creating demo users (`res.users`) within the `charge_erp_core` module. Following these guidelines ensures consistency, prevents errors during installation, and aligns with Odoo 19 CE best practices.

## 1. User and Group Creation Process

In Odoo 19 CE, the `groups_id` field cannot be set at the same time a user is created via XML data files. The process must be split into two separate steps to avoid a `ValueError` during module installation.

**The correct, mandatory procedure is:**
1.  Create the `res.users` record using a standard `<record>` tag.
2.  In a second, subsequent `<record>` tag, update the user record to assign the necessary groups.

### Internal Users (e.g., Faculty)

Internal users must be part of `base.group_user`.

**Example:**
```xml
<!-- 1. Create the user record -->
<record id="user_faculty_example" model="res.users">
    <field name="name">Faculty Example</field>
    <field name="partner_id" ref="partner_for_faculty_example"/>
    <field name="login">facultyex</field>
    <field name="password">demo</field>
</record>

<!-- 2. Assign groups to the user -->
<record id="user_faculty_example" model="res.users">
    <field name="groups_id" eval="[(6, 0, [ref('base.group_user'), ref('charge_erp_core.group_op_faculty')])]"/>
</record>
```

### Portal Users (e.g., Students)

Portal users must be part of `base.group_portal`. The legacy `share="True"` field is deprecated and **must not** be used. Assigning the `base.group_portal` group is sufficient to make a user a portal user.

**Example:**
```xml
<!-- 1. Create the user record -->
<record id="user_student_example" model="res.users">
    <field name="name">Student Example</field>
    <field name="partner_id" ref="partner_for_student_example"/>
    <field name="login">studentex</field>
    <field name="password">demo</field>
</record>

<!-- 2. Assign groups to the user -->
<record id="user_student_example" model="res.users">
    <field name="groups_id" eval="[(6, 0, [ref('base.group_portal'), ref('charge_erp_core.group_op_student')])]"/>
</record>
```

## 2. Idempotency

Using `eval="[(6, 0, [refs])]"` for the `groups_id` field is crucial. This command replaces any existing groups with the specified list, ensuring that the user has exactly the intended permissions. This makes the data loading process stable and re-runnable without causing issues. Do not use the `(4, ...)` syntax for adding groups in demo files.