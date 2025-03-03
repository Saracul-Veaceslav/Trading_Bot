# Trading Bot Frontend

This is the frontend application for the Trading Bot project. It provides a modern React-based dashboard for monitoring trading activities in real-time.

## Features

- Real-time trading data visualization with Chart.js
- WebSocket integration for live updates
- Responsive design for desktop and mobile
- Comprehensive error handling
- TypeScript for type safety

## Getting Started

### Prerequisites

- Node.js (v14 or later)
- npm or yarn

### Installation

1. Clone the repository
2. Navigate to the frontend directory:
   ```
   cd frontend
   ```
3. Install dependencies:
   ```
   npm install
   ```
   or
   ```
   yarn install
   ```

### Development

To start the development server:

```
npm start
```

or

```
yarn start
```

This will start the application in development mode. Open [http://localhost:3000](http://localhost:3000) to view it in the browser.

### Testing

To run the tests:

```
npm test
```

or

```
yarn test
```

### Building for Production

To build the application for production:

```
npm run build
```

or

```
yarn build
```

This will create an optimized production build in the `build` folder.

## Project Structure

```
frontend/
├── public/              # Static files
├── src/                 # Source code
│   ├── api/             # API integration
│   ├── components/      # Reusable components
│   ├── pages/           # Page components
│   ├── types.ts         # TypeScript type definitions
│   ├── index.tsx        # Application entry point
│   └── index.css        # Global styles
├── package.json         # Dependencies and scripts
└── tsconfig.json        # TypeScript configuration
```

## API Integration

The frontend communicates with the backend API through:

1. RESTful API calls for data fetching
2. WebSocket connection for real-time updates

The API integration is configured in `src/api/trading.ts`.

## Dependencies

- React 18
- Chart.js 4
- React Chart.js 2
- TypeScript
- date-fns

## Browser Support

The application supports all modern browsers:

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest) 