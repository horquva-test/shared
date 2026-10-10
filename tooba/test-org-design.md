# Horquva Test Organization Design

**Owner:** Documentation + Failure Scripts — Person 14
**Repository:** `tooba-docs-failure-scripts`
**Document purpose:** Document the test organization's structure, platform inventory, intentional single points of failure (SPOFs), and identity mismatches.

## 1. Purpose and Scope

The test organization is a controlled replica of Horquva designed to support operational workflow testing, change simulations, and failure-injection exercises.

The documented organization represents 30 people from the assigned roster. It does not represent every person in the wider Horquva organization.

Testing should use synthetic data and controlled test resources. No real employee departure should be simulated. Synthetic personas are reserved for departure simulations.

## 2. Organization Chart

### Leadership

| Name         | Role                          | Manager      |
| ------------ | ----------------------------- | ------------ |
| Natasha Khan | Founder/CEO/CTO               | —            |
| Kia Vang     | Co-Founder/CFO/COO            | Natasha Khan |
| Taha Nadeem  | Board Member/Security Advisor | Natasha Khan |

### HR

| Name           | Role                                 | Manager        |
| -------------- | ------------------------------------ | -------------- |
| Imaan Siddiqui | People & Org Development Coordinator | Natasha Khan   |
| Mahnoor Altaf  | HR                                   | Imaan Siddiqui |

### Marketing and Sales

| Name                     | Role                     | Manager      |
| ------------------------ | ------------------------ | ------------ |
| Usman Azhar              | Marketing Manager        | Natasha Khan |
| Zuha Imtiaz              | Sales & Outreach         | Usman Azhar  |
| Muhammad Mohsin Siddiqui | Growth Marketing         | Usman Azhar  |
| Hassan Nasir             | Growth Marketing         | Usman Azhar  |
| Rehan Alam               | Growth Marketing         | Usman Azhar  |
| Aqsa Abdullah            | Growth/Digital Marketing | Usman Azhar  |
| Adil Uddin Ahmed         | Growth Marketing         | Usman Azhar  |
| Inshaa Saleem            | Growth Marketing         | Usman Azhar  |
| Sharjeel Ur Rehman       | Growth Marketing         | Usman Azhar  |
| Amanullah Khan           | Growth Marketing         | Usman Azhar  |
| Minahil Asim             | Growth Marketing         | Usman Azhar  |

### Technology

| Name                       | Role                | Manager          |
| -------------------------- | ------------------- | ---------------- |
| Affan Ahmed Khan           | Full Stack Engineer | Natasha Khan     |
| Muhammad Ibrahim Shaikh    | AI Product Engineer | Affan Ahmed Khan |
| Ahmed Abubakr              | Machine Learning    | Affan Ahmed Khan |
| Sumavia Abid               | Machine Learning    | Affan Ahmed Khan |
| Muhammad Shaheer Nawaz     | Web Development     | Affan Ahmed Khan |
| Masooma Qasim              | Web Development     | Affan Ahmed Khan |
| Syed Muhammad Taha Zaidi   | Web Development     | Affan Ahmed Khan |
| Muhammad Hamza             | AI/ML Engineer      | Affan Ahmed Khan |
| Mahnoor Baloch             | AI/ML Engineer      | Affan Ahmed Khan |
| Muhammad Bilal Askari      | DevSecOps           | Natasha Khan     |
| Saira Adil                 | DevSecOps           | Natasha Khan     |
| Areeb Ahmad                | Security Engineer   | Natasha Khan     |
| Syed Mohammad Abdur Rehman | Security Engineer   | Natasha Khan     |
| Kacho Ayoub Khan           | QA Automation       | Natasha Khan     |

## 3. Platform Inventory

The assignment identifies the following platform categories for the test organization. Actual resource counts and operational status must be verified rather than assumed.

| Platform           | Inventory targets from assignment                                      | Verification status |
| ------------------ | ---------------------------------------------------------------------- | ------------------- |
| Microsoft Entra ID | 30 users, 6 groups, 5 apps, 3 aliases                                  | Not yet verified    |
| n8n                | 15 workflows, 5 credentials, 10+ output files                          | Not yet verified    |
| GitHub             | 8 repositories, 5 teams, 20 collaborators; 5/3/2 distribution per repo | Not yet verified    |
| Slack              | 30 users, 8 channels, 50+ messages                                     | Not yet verified    |
| Jira               | 6 projects, 40 issues, 6 components                                    | Not yet verified    |
| Groq               | 2 API keys                                                             | Not yet verified    |
| Ollama             | 2 models                                                               | Not yet verified    |
| Zapier and Make    | Free accounts                                                          | Not yet verified    |
| PostgreSQL         | 3 tables, 30 seeded users, 5+ data files                               | Not yet verified    |

**Note:** These are assignment targets, not a claim that all resources already exist. Update this inventory when resources have been inspected or created.

## 4. Intentional Single Points of Failure (SPOFs)

The following are proposed areas to inspect during test design. They are not confirmed production failures.

| Area                 | Potential SPOF to inspect                         | Evidence required                                   |
| -------------------- | ------------------------------------------------- | --------------------------------------------------- |
| Workflow credentials | A workflow may depend on one credential           | Workflow configuration and controlled test result   |
| Data source          | A workflow may depend on one source URL           | Source configuration and test output                |
| Slack alerts         | A workflow may depend on one notification channel | Alert configuration and delivery result             |
| Workflow ownership   | A workflow may depend on one owner                | Ownership and access configuration                  |
| AI service           | A workflow may depend on one model or provider    | Provider configuration and controlled fallback test |

For each confirmed SPOF, record the affected workflow, impact, detection method, recovery option, and supporting evidence.

## 5. Identity Mismatches

Identity mismatches should be identified through comparison of authorized test records across platforms.

| Check                | What to compare                                        | Status             |
| -------------------- | ------------------------------------------------------ | ------------------ |
| User identity        | Email and username across platforms                    | Pending inspection |
| Account ownership    | Account owner versus documented owner                  | Pending inspection |
| Access and role      | Assigned access versus expected responsibility         | Pending inspection |
| Credential mapping   | Workflow credential versus documented account          | Pending inspection |
| Synthetic identities | Test persona clearly distinguished from real personnel | Pending inspection |

Do not invent missing identities or assume a mismatch exists without evidence. Record the expected value, observed value, platform, date, and resolution where a mismatch is confirmed.

## 6. Synthetic Personas and Safety Boundaries

The assignment specifies these synthetic personas for departure simulations only:

* `bob@horquva-test.local`
* `alice@horquva-test.local`
* `carol@horquva-test.local`

These are test personas, not employees. Departure simulations must use synthetic personas only. Never simulate the departure or disable the account of a real Horquva employee.

Use mock data first when a live connector is unavailable. Do not store real passwords, API keys, tokens, or client secrets in this document or in source control.

## 7. Evidence and Change Control

For each inspected platform or confirmed issue, record:

* Platform and resource name
* Date of inspection
* Expected configuration
* Observed configuration
* Evidence or test output
* Identified risk or mismatch
* Remediation or next action
* Verification status

Keep unverified items marked as pending. Update this document as the test environment develops.

## 8. Current Status

This document is the initial design baseline. Platform inventories, SPOFs, and identity mismatches remain unverified until supported by actual test-environment evidence.
