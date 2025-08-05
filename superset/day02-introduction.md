# Day 2: Introduction & Basic Concepts

## User Story 1: Navigate Superset Interface

**Title**: As a new user, I want to understand the Superset interface so that I can navigate the application effectively.

**Description**: 
Superset has a comprehensive web interface with multiple sections for different functionalities. Understanding the layout helps users work efficiently.

**Acceptance Criteria**:
- [ ] User can access all main sections
- [ ] Navigation menu is functional
- [ ] User understands the purpose of each section
- [ ] Interface is responsive and user-friendly

**Step-by-Step Guide**:

1. **Access Superset**
   - Open browser: http://localhost:8088
   - Login with admin credentials (admin/admin)

2. **Explore Main Sections**
   - **Dashboards**: View and create dashboards
   - **Charts**: Create and manage visualizations
   - **SQL Lab**: Write and execute SQL queries
   - **Data**: Manage databases and datasets
   - **Security**: Manage users and permissions

3. **Understand Navigation**
   - Top navigation bar contains main sections
   - Left sidebar shows recent items
   - Breadcrumbs show current location
   - Search functionality available

4. **Key Interface Elements**
   - **+** button: Create new items
   - **Settings** gear: Configuration options
   - **User menu**: Profile and logout
   - **Help**: Documentation and support

**Reference Documents**:
- [Superset Interface Guide](https://superset.apache.org/docs/using-superset/exploring-superset)
- [User Interface Overview](https://superset.apache.org/docs/using-superset/exploring-superset#interface-overview)

---

## User Story 2: Understand Data Sources

**Title**: As a data analyst, I want to understand how data sources work in Superset so that I can connect to my databases.

**Description**: 
Data sources are the foundation of Superset. Understanding how to connect and manage data sources is essential for creating visualizations.

**Acceptance Criteria**:
- [ ] User understands database connections
- [ ] User can view available datasets
- [ ] User understands data source types
- [ ] User can explore data structure

**Step-by-Step Guide**:

1. **Access Data Sources**
   - Navigate to Data → Databases
   - View list of connected databases
   - Check connection status

2. **Explore Datasets**
   - Navigate to Data → Datasets
   - View available tables and views
   - Check dataset properties

3. **Understand Data Types**
   - **Databases**: Direct database connections
   - **Datasets**: Tables and views from databases
   - **Virtual Datasets**: SQL-based datasets
   - **Uploaded Files**: CSV, Excel files

4. **Test Connections**
   - Click "Test Connection" for databases
   - Verify data access permissions
   - Check query performance

**Reference Documents**:
- [Data Sources Guide](https://superset.apache.org/docs/using-superset/databases)
- [Database Connections](https://superset.apache.org/docs/installation/databases)

---

## User Story 3: Create Your First Chart

**Title**: As a business user, I want to create my first chart in Superset so that I can visualize data and gain insights.

**Description**: 
Charts are the building blocks of dashboards. Creating your first chart helps understand the visualization process and data exploration.

**Acceptance Criteria**:
- [ ] User can access chart creation interface
- [ ] User can select data source
- [ ] User can choose chart type
- [ ] User can configure chart properties
- [ ] Chart displays correctly

**Step-by-Step Guide**:

1. **Start Chart Creation**
   - Click "+" button → "Chart"
   - Or navigate to Charts → + Chart

2. **Select Data Source**
   - Choose from available datasets
   - Select "World Bank's Health Stats" (example dataset)
   - Click "Create Chart"

3. **Choose Chart Type**
   - Select "Bar Chart" for first chart
   - Other options: Line, Pie, Scatter, etc.

4. **Configure Chart**
   - **Metrics**: Choose what to measure (e.g., SUM(population))
   - **Group By**: Choose dimension (e.g., country)
   - **Filters**: Add any data filters
   - **Time Range**: Set time period if applicable

5. **Save Chart**
   - Click "Save" button
   - Enter chart name: "Population by Country"
   - Choose dashboard or create new one

**Reference Documents**:
- [Chart Creation Guide](https://superset.apache.org/docs/creating-charts-dashboards/creating-charts)
- [Chart Types Reference](https://superset.apache.org/docs/creating-charts-dashboards/exploring-charts)

---

## User Story 4: Explore SQL Lab

**Title**: As a SQL developer, I want to explore SQL Lab so that I can write and test SQL queries for data analysis.

**Description**: 
SQL Lab provides a powerful interface for writing, testing, and saving SQL queries. It's essential for complex data analysis and custom datasets.

**Acceptance Criteria**:
- [ ] User can access SQL Lab
- [ ] User can write SQL queries
- [ ] User can execute queries
- [ ] User can view query results
- [ ] User can save queries

**Step-by-Step Guide**:

1. **Access SQL Lab**
   - Navigate to SQL Lab → SQL Editor
   - Or click "SQL Lab" in top navigation

2. **Select Database**
   - Choose database from dropdown
   - Select schema/database if applicable
   - Verify connection status

3. **Write Simple Query**
   ```sql
   SELECT 
       country,
       SUM(population) as total_population
   FROM world_bank_population
   WHERE year = 2020
   GROUP BY country
   ORDER BY total_population DESC
   LIMIT 10
   ```

4. **Execute Query**
   - Click "Run" button
   - Wait for results to load
   - Review query performance

5. **Save Query**
   - Click "Save" button
   - Enter query name: "Top 10 Countries by Population"
   - Add description if needed

**Reference Documents**:
- [SQL Lab Guide](https://superset.apache.org/docs/using-superset/sql-lab)
- [SQL Best Practices](https://superset.apache.org/docs/using-superset/sql-lab-best-practices)

---

## User Story 5: Understand User Roles and Permissions

**Title**: As an administrator, I want to understand user roles and permissions in Superset so that I can manage access control effectively.

**Description**: 
Superset has a comprehensive role-based access control system that determines what users can see and do within the application.

**Acceptance Criteria**:
- [ ] User understands different roles
- [ ] User can view role permissions
- [ ] User understands access control
- [ ] User can manage basic permissions

**Step-by-Step Guide**:

1. **Access Security Settings**
   - Navigate to Security → Users
   - View list of users and their roles
   - Click on specific user to see details

2. **Understand Default Roles**
   - **Admin**: Full access to all features
   - **Alpha**: Can access all data sources
   - **Gamma**: Limited access to specific data sources
   - **Public**: No access (default for new users)

3. **View Role Permissions**
   - Navigate to Security → Roles
   - Click on role to see permissions
   - Understand permission categories:
     - **Data Source Access**: Which databases/tables
     - **Dashboard Access**: Which dashboards
     - **Chart Access**: Which charts
     - **Feature Access**: Which features

4. **Create Custom Role**
   - Click "Add Role"
   - Enter role name: "Analyst"
   - Select appropriate permissions
   - Save role

**Reference Documents**:
- [Security and Permissions](https://superset.apache.org/docs/using-superset/security)
- [Role-Based Access Control](https://superset.apache.org/docs/using-superset/security#role-based-access-control)

---

## Key Concepts Summary

### 1. Data Hierarchy
- **Databases**: Connection to data sources
- **Datasets**: Tables and views from databases
- **Charts**: Visualizations based on datasets
- **Dashboards**: Collections of charts

### 2. User Interface
- **Top Navigation**: Main sections and features
- **Left Sidebar**: Recent items and quick access
- **Content Area**: Main working area
- **Settings**: Configuration and preferences

### 3. Workflow
- Connect data sources
- Create charts and visualizations
- Build dashboards
- Share and collaborate

### 4. Best Practices
- Use descriptive names for charts and dashboards
- Test queries before creating charts
- Organize dashboards logically
- Document data sources and assumptions

## Next Steps

After completing the introduction, proceed to:
- [Day 3: Configuration & Administration](../day3-configuration/configuration.md)
- [Day 4: Security & Permissions](../day4-security/security.md) 