# PayrollEdge Platform - Frontend

## Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create a `.env` file (optional):
   ```bash
   VITE_API_URL=http://localhost:8000/api
   ```

4. Start the development server:
   ```bash
   npm run dev
   ```

The app will be available at: `http://localhost:5173`

## Project Structure

```
frontend/
├── src/
│   ├── components/     # Reusable UI components
│   ├── pages/        # Page components
│   ├── services/     # API services
│   ├── store/        # Zustand state management
│   ├── types/        # TypeScript types
│   ├── App.tsx       # Main app component
│   └── main.tsx      # Entry point
├── package.json
├── tailwind.config.js
├── vite.config.ts
└── tsconfig.json
```

## Features

- Dashboard with quick stats and actions
- Employee Management (CRUD)
- Attendance Tracking
- Leave Management with approval workflow
- Payroll Processing
- Department Management
- Settings with payroll configuration

## Tech Stack

- React 18 with TypeScript
- Vite for build
- Tailwind CSS for styling
- Zustand for state management
- React Router for routing
- Axios for API calls
- Lucide React for icons
