

\# Entra Connector — Mock Implementation



\## Purpose

A Python connector that reads and validates mock Entra directory data.



\## Mock Data

\- Users: 30

\- Groups: 6

\- Apps: 5

\- Aliases: 3



\## Files

\- create\_mock\_data.py: Generates mock data.

\- mock\_entra\_data.json: Contains mock records.

\- entra\_connector.py: Reads and validates the data.

\- test\_entra\_connector.py: Runs automated tests.



\## How to Run

Generate mock data:

py create\_mock\_data.py



Run connector:

py entra\_connector.py



Run tests:

py -m unittest -v



\## Test Results

\- Data count validation: PASS

\- Mock source validation: PASS

\- Total tests: 2 passed



\## Integration Status

Mock implementation only.

Live Microsoft Entra ID integration has not been verified.
