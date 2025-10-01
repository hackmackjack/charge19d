# Odoo User Creation Best Practices

This document outlines the standard procedures for creating demo users (`res.users`) within the `charge_erp_core` module. Following these guidelines is mandatory to ensure consistency, prevent errors, and align with Odoo 19 CE best practices.

## 1. User and Group Creation Process

In Odoo 19 CE, `groups_id` cannot be set at the same time a user is created in an XML data file. The process must be split into two separate `<record>` tags to avoid a `ValueError`.

**The correct procedure is:**
1.  Create the `res.users` record with all necessary fields except for groups.
2.  In a second `<record>` tag referencing the same user ID, update the `groups_id` field.

## 2. User Types

There is a critical distinction between Internal and Portal users that affects licensing and access rights.

### Internal Users (e.g., Faculty)

Internal users consume a full Odoo license and are intended for employees. They must be part of `base.group_user`.

**Example:**
```xml
<!-- 1. Create the internal user record -->
<record id="user_faculty_example" model="res.users">
    <field name="name">Faculty Example</field>
    <field name="partner_id" ref="partner_for_faculty_example"/>
    <field name="login">facultyex</field>
    <field name="password">demo</field>
</record>

<!-- 2. Assign groups to the internal user -->
<record id="user_faculty_example" model="res.users">
    <field name="groups_id" eval="[(6, 0, [ref('base.group_user'), ref('charge_erp_core.group_op_faculty')])]"/>
</record>
```

### Portal Users (e.g., Students)

Portal users are external users with limited access and do not consume a full license.

Two conditions are **mandatory** for creating a portal user:
1.  The user record **must** include `<field name="share" eval="True"/>`. This flag is what makes the user a portal user.
2.  The user **must** be added to the `base.group_portal`. No other custom groups (like `group_op_student`) are necessary.

**Example:**
```xml
<!-- 1. Create the portal user record with the share flag -->
<record id="user_student_example" model="res.users">
    <field name="name">Student Example</field>
    <field name="partner_id" ref="partner_for_student_example"/>
    <field name="login">studentex</field>
    <field name="password">demo</field>
    <field name="share" eval="True"/>
</record>

<!-- 2. Assign the portal group to the user -->
<record id="user_student_example" model="res.users">
    <field name="groups_id" eval="[(6, 0, [ref('base.group_portal')])]"/>
</record>
```

## 3. Idempotency

Always use `eval="[(6, 0, [refs])]"` when assigning `groups_id`. This command replaces any existing groups with the specified list, ensuring the user has exactly the intended permissions and making the data loading process stable and re-runnable. Do not use the `(4, ...)` syntax.