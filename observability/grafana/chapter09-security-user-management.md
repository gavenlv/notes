# Chapter 9: Security and User Management

## 9.1 Authentication

### 9.1.1 Basic Authentication

Default username/password login.

**Configuration (`grafana.ini`):**
```ini
[auth]
disable_login_form = false
disable_signout_menu = false

[security]
admin_user = admin
admin_password = admin
allow_embedding = false
```

### 9.1.2 LDAP/Active Directory

```ini
[auth.ldap]
enabled = true
config_file = /etc/grafana/ldap.toml
allow_sign_up = true
```

**LDAP Configuration (`ldap.toml`):**
```toml
[[servers]]
host = "ldap.company.com"
port = 389
use_ssl = false
start_tls = false
bind_dn = "cn=admin,dc=company,dc=com"
bind_password = "password"
search_filter = "(cn=%s)"
search_base_dns = ["dc=company,dc=com"]

[servers.attributes]
name = "givenName"
surname = "sn"
username = "cn"
member_of = "memberOf"
email = "email"

[[servers.group_mappings]]
group_dn = "cn=admins,ou=groups,dc=company,dc=com"
org_role = "Admin"

[[servers.group_mappings]]
group_dn = "cn=editors,ou=groups,dc=company,dc=com"
org_role = "Editor"
```

### 9.1.3 OAuth (Google, GitHub, GitLab)

**Google OAuth:**
```ini
[auth.google]
enabled = true
client_id = YOUR_CLIENT_ID
client_secret = YOUR_CLIENT_SECRET
scopes = https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/userinfo.email
auth_url = https://accounts.google.com/o/oauth2/auth
token_url = https://accounts.google.com/o/oauth2/token
allowed_domains = company.com
allow_sign_up = true
```

**GitHub OAuth:**
```ini
[auth.github]
enabled = true
client_id = YOUR_CLIENT_ID
client_secret = YOUR_CLIENT_SECRET
scopes = user:email,read:org
auth_url = https://github.com/login/oauth/authorize
token_url = https://github.com/login/oauth/access_token
api_url = https://api.github.com/user
allowed_organizations = your-org
allow_sign_up = true
```

### 9.1.4 SAML

```ini
[auth.saml]
enabled = true
certificate_path = /etc/grafana/saml-cert.pem
private_key_path = /etc/grafana/saml-key.pem
idp_metadata_url = https://sso.company.com/metadata
assertion_attribute_name = login
assertion_attribute_login = login
assertion_attribute_email = email
assertion_attribute_org = org
assertion_attribute_role = role
```

### 9.1.5 Anonymous Access

```ini
[auth.anonymous]
enabled = true
org_name = Main Org.
org_role = Viewer
```

---

## 9.2 Authorization

### 9.2.1 User Roles

**Organization Roles:**
- **Viewer**: Read-only access
- **Editor**: Can create/edit dashboards
- **Admin**: Full organizational control

**Server Roles (for server admins):**
- **Grafana Admin**: Manage server settings

### 9.2.2 Managing Users

**Add user:**
1. Configuration → Users
2. New user
3. Fill details
4. Set role: Viewer/Editor/Admin

**Via API:**
```bash
curl -X POST \
  -H "Authorization: Bearer <API-KEY>" \
  -H "Content-Type: application/json" \
  -d '{
    "name":"John Doe",
    "email":"john@company.com",
    "login":"john",
    "password":"password"
  }' \
  http://localhost:3000/api/admin/users
```

### 9.2.3 Teams

**Create team:**
1. Configuration → Teams
2. New team
3. Name: "DevOps Team"
4. Email: devops@company.com

**Add members:**
- Select team → Add member
- Choose user and role

**Team permissions:**
```yaml
Team: DevOps
Members:
  - john@company.com (Admin)
  - jane@company.com (Member)
  
Dashboard permissions:
  - Production folder: Edit
  - Staging folder: Edit
  - Development folder: View
```

---

## 9.3 Permissions

### 9.3.1 Dashboard Permissions

**Set permissions:**
1. Dashboard settings → Permissions
2. Add permission
3. Select: User/Team/Role
4. Permission: View/Edit/Admin

**Example:**
```yaml
Dashboard: Production Metrics

Permissions:
  - Role: Viewer → View
  - Team: DevOps → Edit
  - User: john@company.com → Admin
  - Role: Editor → No access (inherited)
```

### 9.3.2 Folder Permissions

```yaml
Folder: Production Dashboards

Permissions:
  - Role: Viewer → View
  - Team: SRE → Edit
  - Team: Management → View
```

All dashboards in folder inherit permissions!

### 9.3.3 Data Source Permissions

1. Data source → Permissions tab
2. Enable permissions
3. Add user/team

```yaml
Data source: Production Prometheus

Permissions:
  - Team: DevOps → Query
  - Team: Analytics → Query
  - Role: Viewer → No access
```

---

## 9.4 Organizations

Multi-tenancy support.

### 9.4.1 Create Organization

1. Server Admin → Orgs
2. New org
3. Name: "Engineering"

**Switch organization:**
- User menu → Switch org

### 9.4.2 Organization Isolation

Each organization has:
- Separate dashboards
- Separate data sources
- Separate users and teams
- Separate settings

### 9.4.3 Cross-Organization Users

User can belong to multiple orgs with different roles:

```yaml
User: john@company.com

Organizations:
  - Engineering (Editor)
  - Sales (Viewer)
  - Management (Admin)
```

---

## 9.5 API Keys and Service Accounts

### 9.5.1 API Keys

```yaml
Name: CI/CD Pipeline
Role: Editor
Expiration: 30d
```

**Use:**
```bash
curl -H "Authorization: Bearer <API-KEY>" \
  http://localhost:3000/api/dashboards/db
```

### 9.5.2 Service Accounts

Long-lived accounts for automation.

1. Configuration → Service accounts
2. Add service account
3. Name: "Terraform"
4. Role: Admin
5. Add token

**Usage:**
```bash
export GRAFANA_TOKEN=<service-account-token>
terraform apply
```

---

## 9.6 Security Best Practices

### 9.6.1 HTTPS/TLS

```ini
[server]
protocol = https
cert_file = /etc/grafana/grafana.crt
cert_key = /etc/grafana/grafana.key
```

### 9.6.2 Secrets Management

**Use environment variables:**
```ini
[security]
admin_password = $__env{GF_SECURITY_ADMIN_PASSWORD}

[auth.google]
client_secret = $__env{GF_AUTH_GOOGLE_CLIENT_SECRET}
```

**Docker:**
```yaml
environment:
  - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_ADMIN_PASSWORD}
secrets:
  - grafana_admin_password
```

### 9.6.3 Security Headers

```ini
[security]
cookie_secure = true
cookie_samesite = lax
strict_transport_security = true
x_content_type_options = true
x_xss_protection = true
```

### 9.6.4 Password Policy

```ini
[security]
password_policy_pattern = ^.{12,}$
```

---

## 9.7 Summary

✅ **Authentication**: LDAP, OAuth, SAML, anonymous  
✅ **Authorization**: Roles and permissions  
✅ **Users**: User and team management  
✅ **Organizations**: Multi-tenancy  
✅ **API Keys**: Automation authentication  
✅ **Security**: Best practices for production  

**Next Chapter**: [Chapter 10: Performance Optimization](chapter10-performance-optimization.md)
