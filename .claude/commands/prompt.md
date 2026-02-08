Build a client time tracker for freelancers with the following requirements:

## Core Requirements
Stack: 
- Frontend: HTML + Tailwind CSS (mobile first responsive design)
- Backend: Python FastAPI, uvicorn
- DB: Sqlite with SQLAlchemy ORM
- Authentication: JWT tokens
- Package management: uv
- Deployment: fly.io

Data:
- Client: { id: crypto.randomUUID(), name: string, rate: number }
- TimeEntry: { id: crypto.randomUUID(), clientId: string, date: string (ISO), hours: number, note: string }
- A client has many time entries.

Flow:
- Client list → click client → time entries for that client → back to list

Client list screen:
- Add client via inline form (name + hourly rate). Button is disabled if either field is empty.
- Each client card shows name, rate, and total logged hours.
- Empty state: "No clients yet. Add your first client above."
- Click a client card to see their time entries.

Time entries screen:
- Header shows client name and rate. Back button returns to client list.
- Add entry form: date (defaults to today), hours (number input), note (text).
- Submit disabled if hours ≤ 0. Inline error if submitted with invalid hours.
- On success, clear form, prepend entry to list.
- Entries listed in reverse chronological order showing date, hours, note, and line total (hours × rate).
- Footer shows total hours and total earnings for this client.
- Empty state: "No time logged for this client yet."

Layout: 
- Centered card, max-width 640px, toggle light/dark theme. Mobile-friendly, single column.
- Responsive: single column, max-width 640px centered. Touch targets minimum 44px on mobile.

UI/UX:
- Hover: cards lift with subtle shadow, buttons darken. Focus: 2px indigo ring on inputs.
- Deleting a client: confirmation modal with "Cancel" and red "Delete" button.
- Color scheme: 
  - Primary: Blue (#3B82F6)
  - Success: Green (#10B981)
  - Warning: Yellow (#F59E0B)
  - Danger: Red (#EF4444)