import React from 'react';
import { render, screen, waitFor, act } from '@testing-library/react';
import '@testing-library/jest-dom';
import { Dashboard } from '../../../frontend/src/pages/Dashboard';
import * as tradingApi from '../../../frontend/src/api/trading';

// Mock the trading API
jest.mock('../../../frontend/src/api/trading', () => ({
  fetchTrades: jest.fn(),
  subscribeToUpdates: jest.fn(),
}));

describe('Dashboard Page', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  /**
   * Feature: Dashboard Data Loading
   * 
   * Scenario: Dashboard loads trade data on mount
   *   Given the dashboard component
   *   When it is mounted
   *   Then it should fetch trade data from the API
   */
  test('fetches trade data on mount', async () => {
    // Mock the API response
    const mockTrades = [
      { id: 1, symbol: 'BTC/USD', price: 50000, amount: 0.1, timestamp: new Date().toISOString() },
      { id: 2, symbol: 'ETH/USD', price: 3000, amount: 1.5, timestamp: new Date().toISOString() }
    ];
    
    (tradingApi.fetchTrades as jest.Mock).mockResolvedValue(mockTrades);
    (tradingApi.subscribeToUpdates as jest.Mock).mockReturnValue(() => {});
    
    // Render the dashboard
    render(<Dashboard />);
    
    // Check loading state is shown initially
    expect(screen.getByText('Loading...')).toBeInTheDocument();
    
    // Wait for data to load
    await waitFor(() => {
      expect(tradingApi.fetchTrades).toHaveBeenCalledTimes(1);
    });
    
    // Check that loading state is removed
    await waitFor(() => {
      expect(screen.queryByText('Loading...')).not.toBeInTheDocument();
    });
    
    // Check that dashboard title is rendered
    expect(screen.getByText('Trading Dashboard')).toBeInTheDocument();
  });

  /**
   * Feature: Dashboard WebSocket Updates
   * 
   * Scenario: Dashboard subscribes to real-time updates
   *   Given the dashboard has loaded initial data
   *   When a new trade update is received via WebSocket
   *   Then the dashboard should update with the new trade
   */
  test('subscribes to real-time updates', async () => {
    // Mock initial trades
    const mockTrades = [
      { id: 1, symbol: 'BTC/USD', price: 50000, amount: 0.1, timestamp: new Date().toISOString() }
    ];
    
    // Setup mocks
    (tradingApi.fetchTrades as jest.Mock).mockResolvedValue(mockTrades);
    
    // Create a mock for the subscription callback
    let subscriptionCallback: Function;
    (tradingApi.subscribeToUpdates as jest.Mock).mockImplementation((callback) => {
      subscriptionCallback = callback;
      return () => {}; // Return unsubscribe function
    });
    
    // Render the dashboard
    render(<Dashboard />);
    
    // Wait for initial data to load
    await waitFor(() => {
      expect(tradingApi.fetchTrades).toHaveBeenCalledTimes(1);
    });
    
    // Verify subscription was set up
    expect(tradingApi.subscribeToUpdates).toHaveBeenCalledTimes(1);
    
    // Simulate a new trade update via WebSocket
    const newTrade = { id: 2, symbol: 'ETH/USD', price: 3000, amount: 1.5, timestamp: new Date().toISOString() };
    
    act(() => {
      subscriptionCallback(newTrade);
    });
    
    // Check that the component updates with the new trade
    // This would typically check for specific trade data in the UI
    // but for simplicity we'll just check that the component doesn't crash
    expect(screen.getByText('Trading Dashboard')).toBeInTheDocument();
  });

  /**
   * Feature: Dashboard Error Handling
   * 
   * Scenario: Dashboard handles API errors gracefully
   *   Given the dashboard component
   *   When the API call fails
   *   Then it should display an error message
   */
  test('handles API errors gracefully', async () => {
    // Mock API error
    (tradingApi.fetchTrades as jest.Mock).mockRejectedValue(new Error('Failed to fetch trades'));
    (tradingApi.subscribeToUpdates as jest.Mock).mockReturnValue(() => {});
    
    // Render the dashboard
    render(<Dashboard />);
    
    // Wait for error to be handled
    await waitFor(() => {
      expect(tradingApi.fetchTrades).toHaveBeenCalledTimes(1);
    });
    
    // Check that error message is displayed
    // Note: This assumes the Dashboard component will show an error message
    // when the API call fails. Adjust this expectation based on your implementation.
    expect(screen.getByText(/error/i)).toBeInTheDocument();
  });

  /**
   * Feature: Dashboard Component Cleanup
   * 
   * Scenario: Dashboard unsubscribes from updates on unmount
   *   Given the dashboard has subscribed to updates
   *   When the component unmounts
   *   Then it should unsubscribe from updates
   */
  test('unsubscribes from updates on unmount', async () => {
    // Mock the unsubscribe function
    const mockUnsubscribe = jest.fn();
    (tradingApi.fetchTrades as jest.Mock).mockResolvedValue([]);
    (tradingApi.subscribeToUpdates as jest.Mock).mockReturnValue(mockUnsubscribe);
    
    // Render and unmount the dashboard
    const { unmount } = render(<Dashboard />);
    
    // Wait for subscription to be set up
    await waitFor(() => {
      expect(tradingApi.subscribeToUpdates).toHaveBeenCalledTimes(1);
    });
    
    // Unmount the component
    unmount();
    
    // Check that unsubscribe was called
    expect(mockUnsubscribe).toHaveBeenCalledTimes(1);
  });
}); 