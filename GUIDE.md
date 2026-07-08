# RBAC PROJECT MASTER GUIDE (FINAL)

---

# 🎯 PROJECT PURPOSE

Build a complete RBAC (Role-Based Access Control) system using:

- Backend → Flask + PostgreSQL
- Frontend → Vite + TypeScript
- Authentication → Token based
- Authorization → Full CRUD RBAC
- Setup → Smart automation setup.py

This project must support:
- Multiple roles
- Multiple users
- Dynamic permission control
- API-level RBAC enforcement
- Admin management panel

---

# ⚠️ IMPORTANT DEVELOPMENT RULES

- Always read this GUIDE.md before changes
- Never overwrite existing working files
- Never remove working logic unnecessarily
- Apply only minimal required changes
- Every change must be documented in CHANGE LOG
- Always fix root cause
- Keep code simple and maintainable

---

# 🧠 FINAL LOCKED REQUIREMENTS

## Modules (Fixed)

Exactly 10 modules must exist:

1. Dashboard
2. Users
3. Orders
4. Products
5. Reports
6. Settings
7. Invoices
8. Customers
9. Suppliers
10. Analytics

These are fixed modules.
Admin should not create/delete modules dynamically.

---

# 🔐 RBAC PERMISSION MODEL

Each module supports:

- Create
- Read
- Update
- Delete

Permission table structure:

- role_id
- menu_id
- can_create
- can_read
- can_update
- can_delete

---

# 👥 ROLES

Default roles:

- Admin
- Manager
- User

Admin can:
- Create roles
- Edit roles
- Delete roles

---

# 👤 USER MANAGEMENT

Admin can:

- Create users
- Edit users
- Delete users
- Assign roles

---

# 🛡️ RBAC ENFORCEMENT RULES

## Frontend

- Show menu only if can_read=True
- Block routes if permission missing
- Show "Access Denied" page for unauthorized routes

---

## Backend

Every API must validate permissions.

Examples:

- Create API → requires can_create
- Read API → requires can_read
- Update API → requires can_update
- Delete API → requires can_delete

Unauthorized requests must return:
- 401 → unauthenticated
- 403 → permission denied

---

# 🔑 AUTHENTICATION

System uses token-based authentication.

Flow:
1. User logs in
2. Backend creates token
3. Frontend stores token
4. Every API request sends:
   Authorization: Bearer <token>

Backend validates token before processing request.

---

# 🖥️ ADMIN PANEL REQUIREMENT

Admin panel must support:

## Role Management
- Create role
- Edit role
- Delete role

---

## User Management
- Create user
- Edit user
- Delete user
- Assign role

---

## Permission Management

Table UI:

| Module | Create | Read | Update | Delete |

Checkbox based.

Permissions saved dynamically.

---

# 📁 CURRENT PROJECT STRUCTURE

## Backend

backend/app/

Files:

- db.py
- models.py
- routes.py
- seed.py
- __init__.py
- run.py

---

## Frontend

frontend/dashboard/src/

Files:

- main.ts
- router.ts
- login.ts
- dashboard.ts
- admin.ts
- pages/

---

## Setup

Root file:

- setup.py

---

# ⚙️ SETUP.PY RULES

setup.py must:

## DO:
- Create venv
- Install backend dependencies
- Install frontend dependencies
- Reset DB
- Run backend
- Run frontend

---

## REMOVE ONLY:
- node_modules
- dist
- __pycache__
- .idea

---

## MUST NOT REMOVE:
- backend/
- frontend/src/
- manually created code

---

## Smart Behavior
If backend/app exists:
- skip recreation
- never overwrite files

---

# 🌱 DATABASE SEED RULES

Seed must create:

- 10 modules
- 3 default roles
- admin user
- full CRUD access for admin

Default login:

username:
admin

password:
admin123

---

# 🔄 CURRENT IMPLEMENTATION STATUS

## COMPLETED

✔ Flask backend created  
✔ PostgreSQL integration working  
✔ Vite + TypeScript frontend working  
✔ Login system working  
✔ Token-based authentication working  
✔ Sidebar dashboard working  
✔ Routing system working  
✔ Route protection working  
✔ CRUD Permission model added  
✔ 10 modules added  
✔ Default roles added  
✔ Seed system working  
✔ setup.py automation working  
✔ Admin permission APIs added  
✔ Permissions CRUD APIs added  
✔ Menu filtering via RBAC working  

---

# 🚧 REMAINING IMPLEMENTATION

## Step 2.3
Frontend permission table UI finalization

---

## Step 3
Role management UI + APIs

---

## Step 4
User management UI + APIs

---

## Step 5
API-level CRUD RBAC enforcement

---

## Step 6
Frontend CRUD permission enforcement

Examples:
- Hide Create button
- Disable Edit button
- Disable Delete button

---

## Step 7
Testing with Admin / Manager / User roles

---

## Step 8
Final cleanup + optimization + UI polish

---

# 🧠 CURRENT FLOW

## Login Flow

1. User logs in
2. Token generated
3. User stored in localStorage
4. Menus fetched using token
5. Sidebar rendered

---

## RBAC Flow

1. Permissions fetched from DB
2. Sidebar filtered using can_read
3. Router validates permissions
4. Backend validates permissions
5. Unauthorized access blocked

---

# 📝 CHANGE LOG

## Change 1
Initial project setup completed

## Change 2
Added setup.py automation

## Change 3
Prevented backend overwrite in setup.py

## Change 4
Added cleanup logic in setup.py

## Change 5
Added login system

## Change 6
Added dashboard layout

## Change 7
Added sidebar navigation

## Change 8
Added route protection

## Change 9
Added token-based authentication

## Change 10
Added admin panel base

## Change 11
Converted Permission model from can_view to CRUD permissions

## Change 12
Added 10 fixed modules

## Change 13
Added default roles

## Change 14
Updated seed.py for CRUD permissions

## Change 15
Added permissions APIs

## Change 16
Fixed duplicate endpoint issues in routes.py

## Change 17
Fixed indentation and route conflicts

## Change 18
Added CRUD permission response structure

## Change 19
Fixed admin route navigation normalization and permission save payload

## Change 20
Added RBAC protection and page routes for all sidebar modules

## Change 21
Improved admin permission UI and inline save feedback

## Change 22
Cleaned backend permission APIs with Admin-only validation and deduplicated permission updates

## Change 23
Documented routing, sidebar, token, permission, seed, and admin management flows

## Change 24
Added dynamic role CRUD, user CRUD, Products/Customers/Suppliers/Orders CRUD, current-user permission helpers, backend API RBAC enforcement, dashboard totals, and reusable frontend CRUD rendering.

## Change 25
Refactored the frontend UI layer with a reusable modern admin dashboard stylesheet, fixed sidebar shell, responsive page containers, dashboard cards, styled CRUD forms/tables/buttons, delete confirmations, loading/empty/error states, improved Admin permission matrix, polished login/access denied screens, and upgraded read-only module pages without changing RBAC, routes, APIs, or business logic.

## Change 26
Hardened setup.py into a Windows/Git Bash friendly setup utility with .env/.env.local loading, automatic PostgreSQL password detection from PGPASSWORD/config, dependency validation for Python/pip/node/npm/psql, robust venv removal/retry handling, smarter cleanup, force/no-start options, structured INFO/SUCCESS/WARNING/ERROR logs, subprocess error guidance, run preflight checks, port warnings, and graceful backend/frontend process termination.

## Change 27
Stabilized the foundation with a normalized API envelope, reusable frontend API helper, shared backend `success_response()`, `error_response()`, and `validate_permission()` helpers, relationship-based Orders linked to Customers and Products, timestamps and uniqueness constraints on core models, safer delete validation for records used by orders, lowercase route normalization, required CRUD form validation, and order customer/product dropdowns.

## Change 28
Improved setup.py further with dependency version logging, Windows `venv --copies` fallback for venvlauncher.exe failures, read-only cleanup handling, gentler then forced process tree shutdown, and SIGINT/SIGTERM cleanup.

## Change 29
Completed final CRUD/RBAC hardening with idempotent default role/menu/permission seeding, Manager/User starter permissions, protected `/order-options` dropdown data, order table display names, reusable frontend toast/loading/confirmation helpers, busy states for save/delete actions, custom delete confirmation modals for CRUD and roles, dashboard quick actions, safer localStorage parsing, and a PostgreSQL-backed CRUD/RBAC smoke test.

---

# CURRENT RBAC IMPLEMENTATION FLOW

## Token Flow

1. `frontend/dashboard/src/login.ts` sends username and password to `POST /login`.
2. `backend/app/routes.py` validates the user and creates a token.
3. Login response uses the normalized envelope: `{ success, message, data }`.
4. `data` includes `user`, `role_id`, `role_name`, and `token`.
5. `frontend/dashboard/src/api.ts` unwraps `data` and stores the login data in `localStorage.user`.
6. Protected frontend API calls send `Authorization: Bearer <token>`.
7. Backend validates the token through `current_user()`.

## Sidebar Rendering Flow

1. `frontend/dashboard/src/dashboard.ts` reads `localStorage.user`.
2. It calls `/my-menus` with the saved token.
3. `backend/app/routes.py` reads the authenticated user's role.
4. `/my-menus` returns only menus where `can_read=True`.
5. Sidebar items are generated dynamically from that API response.
6. Sidebar click calls `go('/module')`.
7. `frontend/dashboard/src/router.ts` normalizes the path and renders the matching route.

Menus must not be hardcoded in the sidebar.

## Routing Flow

Routing is controlled by `frontend/dashboard/src/router.ts`.

Rules:

- Login route renders `login.ts`.
- Authenticated routes render inside the dashboard layout.
- Dashboard layout owns `<div id="content">`.
- Routed pages render only into `#content`.
- Every sidebar module route checks `user.menus.includes("module")`.
- Unauthorized routes render Access Denied in `#content`.
- `/admin` also requires Admin role access.

Current route files:

- `/` and `/dashboard` -> `dashboard.ts`
- `/users` -> `pages/users.ts`
- `/orders` -> `pages/orders.ts`
- `/products` -> `pages/products.ts`
- `/reports` -> `pages/reports.ts`
- `/settings` -> `pages/settings.ts`
- `/invoices` -> `pages/invoices.ts`
- `/customers` -> `pages/customers.ts`
- `/suppliers` -> `pages/suppliers.ts`
- `/analytics` -> `pages/analytics.ts`
- `/admin` -> `pages/admin.ts`

## Permission Flow

Permissions are stored in the `Permission` table:

- `role_id`
- `menu_id`
- `can_create`
- `can_read`
- `can_update`
- `can_delete`

Frontend permission management:

1. `pages/admin.ts` loads roles from `/roles`.
2. It loads permissions for the selected role from `/permissions?role_id=<id>`.
3. It renders a table with Create, Read, Update, Delete checkboxes.
4. Save builds one permission row per `menu_id`.
5. Save posts to `/permissions/update`.
6. Success or error message renders inline on the admin page.

Backend permission update:

1. `/permissions/update` requires a valid token.
2. It requires Admin role.
3. It validates `role_id`.
4. It validates permission list structure.
5. It validates each `menu_id`.
6. It deduplicates by `menu_id`.
7. It replaces the role's permission rows with the cleaned permission set.

## Menu Seeding Flow

Menu seed is controlled by `backend/app/seed.py`.

Seed creates:

- Dashboard
- Users
- Orders
- Products
- Reports
- Settings
- Invoices
- Customers
- Suppliers
- Analytics
- Admin

Admin route remains `/admin` because frontend route generation uses lowercase menu names.

If an existing database contains lowercase `admin`, seed cleanup renames it to `Admin`.

## Admin Management Flow

Admin UI lives in `frontend/dashboard/src/pages/admin.ts`.

Admin page requirements:

- Render inside `#content`.
- Read token from `localStorage.user`.
- Load roles from backend.
- Load permission rows by selected role.
- Render CRUD checkboxes.
- Save permission updates with `menu_id`.
- Show success/error message after save.
- Preserve dashboard/sidebar layout.

Admin access is protected in two places:

- Frontend route requires `admin` menu read permission.
- Frontend route also requires Admin role identity.
- Backend admin APIs require Admin role identity.

## Dynamic Role Management Flow

Role management stays inside the Admin page.

Backend APIs:

- `GET /roles` lists roles.
- `POST /roles` creates a role.
- `PUT /roles/:id` updates a role name.
- `DELETE /roles/:id` deletes a role.

Rules:

- Role names are required.
- Duplicate role names are rejected.
- The Admin role cannot be renamed or deleted.
- A role assigned to any user cannot be deleted.
- New roles receive one permission row per fixed menu with all CRUD flags set to false.

Frontend flow:

1. `pages/admin.ts` loads roles from `/roles`.
2. The Role Management form creates or updates roles.
3. The role table exposes Edit/Delete for non-Admin roles.
4. The permission table continues to load `/permissions?role_id=<id>`.
5. Saving permissions posts to `/permissions/update`.
6. Role delete uses the reusable confirmation modal.
7. Role save/delete success and error feedback is shown through inline messages and toasts.

## CRUD API Flow

CRUD resources are exposed through `backend/app/routes.py`.

All API responses now follow:

- Success: `{ "success": true, "message": "...", "data": ... }`
- Error: `{ "success": false, "error": "...", "message": "..." }`

Frontend code should call the shared `api()` helper in `frontend/dashboard/src/api.ts`, which automatically sends the bearer token, parses the response, throws on API errors, and returns the unwrapped `data`.

User APIs:

- `GET /users`
- `POST /users`
- `PUT /users/:id`
- `DELETE /users/:id`
- `GET /role-options`

Business CRUD APIs:

- `GET /products`, `POST /products`, `PUT /products/:id`, `DELETE /products/:id`
- `GET /customers`, `POST /customers`, `PUT /customers/:id`, `DELETE /customers/:id`
- `GET /suppliers`, `POST /suppliers`, `PUT /suppliers/:id`, `DELETE /suppliers/:id`
- `GET /orders`, `POST /orders`, `PUT /orders/:id`, `DELETE /orders/:id`
- `GET /order-options`

Order create/update payload:

- `customer_id`
- `product_id`
- `quantity`
- `status`

`GET /order-options` is protected by Orders read permission and returns customer/product dropdown data plus valid statuses. It avoids coupling the Orders page to Products and Customers read permissions while keeping direct Products/Customers APIs protected.

Order responses include both IDs and display names:

- `customer_id`
- `customer_name`
- `product_id`
- `product_name`
- `quantity`
- `status`

Dashboard API:

- `GET /dashboard-stats`

## Database Models

Existing RBAC models remain:

- `Role`
- `User`
- `Menu`
- `Permission`

New CRUD models:

- `Product`: `name`, `price`, `stock`
- `Customer`: `name`, `phone`, `email`
- `Supplier`: `name`, `contact`, `company`
- `Order`: `customer_id`, `product_id`, `quantity`, `status`

Relationships:

- `Order.customer_id` references `Customer.id`
- `Order.product_id` references `Product.id`

Shared model behavior:

- Core models include `created_at` and `updated_at`.
- `Role.name`, `User.username`, and `Menu.name` are unique.
- `Permission` has a unique role/menu pairing.
- Products and customers used by orders are protected from unsafe deletes.
- Role/Menu permission rows use cascade cleanup.
- Customer/Product deletes are restricted while related orders exist.

`db.create_all()` creates the new tables when the backend starts against a database that does not already have them.

## Backend RBAC Enforcement Logic

`backend/app/routes.py` now contains reusable permission helpers:

- `validate_permission(user, module, action)`
- `permission_required(module, action)`
- `admin_required()`

CRUD enforcement mapping:

- `GET` requires `can_read`
- `POST` requires `can_create`
- `PUT` requires `can_update`
- `DELETE` requires `can_delete`

Admin-only APIs still require Admin role identity:

- `/roles`
- `/roles/:id`
- `/menus`
- `/permissions`
- `/permissions/update`

Unauthorized API behavior:

- Missing or invalid token returns `401`.
- Valid token without permission returns `403`.

## Frontend Permission Utility Flow

Frontend utility file:

- `frontend/dashboard/src/permissions.ts`

Helpers:

- `canCreate(module)`
- `canRead(module)`
- `canUpdate(module)`
- `canDelete(module)`
- `getModulePermission(module)`
- `clearPermissionCache()`

Shared frontend API utilities:

- `api(path, options)`
- `getStoredUser()`
- `saveStoredUser(user)`
- `clearStoredUser()`
- `escapeHtml(value)`

Shared frontend UI utilities:

- `showToast(message, type)`
- `confirmDialog(title, message, confirmText)`
- `pageLoading(title, subtitle)`
- `emptyState(title, text)`
- `setBusy(button, busy, label)`

Flow:

1. Page asks for the current module permission.
2. Permission helper reads cached `localStorage.user.permissions` if present.
3. If missing, it calls `GET /my-permissions` with the bearer token.
4. CRUD pages hide create forms when `can_create` is false.
5. CRUD pages hide Edit buttons when `can_update` is false.
6. CRUD pages hide Delete buttons when `can_delete` is false.
7. Backend still validates every request.

## Frontend CRUD Rendering Flow

Reusable CRUD renderer:

- `frontend/dashboard/src/pages/crud.ts`

Used by:

- `pages/products.ts`
- `pages/customers.ts`
- `pages/suppliers.ts`
- `pages/orders.ts`

Custom page:

- `pages/users.ts` renders user table, add/edit form, delete action, and role dropdown.

Each page still:

- Renders only into `#content`.
- Keeps the dashboard/sidebar shell untouched.
- Uses manual DOM rendering and event listeners.
- Uses the current token from `localStorage.user`.
- Supports required fields and select dropdown fields.
- Hides create, edit, delete, and form controls based on module permissions.
- Refreshes list data after create, update, and delete.
- Resets forms after successful save.
- Shows loading, success, and error feedback through shared UI helpers.
- Uses the reusable confirmation modal before delete.

## Dashboard Totals Flow

`frontend/dashboard/src/dashboard.ts` renders summary cards on `/` and `/dashboard`.

Cards:

- Total Users
- Total Products
- Total Orders
- Total Customers
- Total Suppliers

Dashboard also renders Quick Actions for readable core modules so Admin/Manager/User accounts can jump to permitted work areas without hardcoded sidebar behavior.

The frontend calls `GET /dashboard-stats`, which requires Dashboard read permission.

## Manual Testing Flow

After running the project manually:

1. Login as `admin` / `admin123`.
2. Verify dashboard cards load.
3. Create a custom role from Admin page.
4. Assign only `can_read` for Products, Customers, Suppliers, Orders, and Users.
5. Assign that role to a test user.
6. Login as the test user.
7. Verify sidebar only shows modules with read permission.
8. Verify CRUD pages show tables but hide add/edit/delete controls for read-only modules.
9. Try calling create/update/delete APIs with that user's token and verify `403`.
10. Grant `can_create`, then verify add form appears and POST succeeds.
11. Grant `can_update`, then verify Edit appears and PUT succeeds.
12. Grant `can_delete`, then verify Delete appears and DELETE succeeds.
13. Remove a module's read permission and verify sidebar/route access is blocked after permission cache refresh or relogin.
14. Verify Admin role cannot be deleted.
15. Verify roles assigned to users cannot be deleted.

## Automated Smoke Testing Flow

The final smoke verification used Flask's test client, not a running server:

1. Login as Admin.
2. Create a temporary read-only role.
3. Save read-only permissions for Users, Products, Customers, Suppliers, and Orders.
4. Create a temporary user assigned to that role.
5. Verify the read-only user can list but receives `403` for create/update/delete.
6. As Admin, create/update/list Products, Customers, Suppliers, Orders, Users, and Roles.
7. Verify products/customers linked to orders cannot be deleted.
8. Delete the order, then verify product/customer deletes succeed.
9. Clean up temporary users, roles, permissions, and CRUD records.

## File Ownership

- `frontend/dashboard/src/main.ts` starts router rendering.
- `frontend/dashboard/src/login.ts` owns login screen and token storage.
- `frontend/dashboard/src/router.ts` owns route protection and page imports.
- `frontend/dashboard/src/dashboard.ts` owns dashboard shell and sidebar rendering.
- `frontend/dashboard/src/permissions.ts` owns current-user CRUD permission helpers.
- `frontend/dashboard/src/pages/crud.ts` owns reusable manual CRUD page rendering.
- `frontend/dashboard/src/pages/*.ts` own content rendering inside `#content`.
- `frontend/dashboard/src/pages/admin.ts` owns permission management UI.
- `backend/app/routes.py` owns auth, menu, role, permission, CRUD, and dashboard stats APIs.
- `backend/app/seed.py` owns default roles, menus, admin user, and admin permissions.
- `backend/app/models.py` owns database models.

---

# 🧠 HOW TO CONTINUE DEVELOPMENT

Before every change:

1. Read GUIDE.md
2. Understand current step
3. Apply minimal required change
4. Test
5. Update CHANGE LOG

---

# 🚀 MASTER DEVELOPMENT GOAL

Final system should support:

✔ Full RBAC  
✔ CRUD permissions  
✔ Multiple roles  
✔ Multiple users  
✔ Admin management panel  
✔ API security  
✔ Route security  
✔ Smart setup automation  
✔ Clean UI  
✔ Stable architecture  

---

# 🛑 FINAL RULE

Every change must be:

- Correct
- Minimal
- Safe
- Documented
- Tested
