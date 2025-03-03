import { fetchTrades, subscribeToUpdates, transformTradesForChart } from '../../../frontend/src/api/trading';

// Mock fetch
global.fetch = jest.fn();

describe('Trading API', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  /**
   * Feature: Fetch Trades API
   * 
   * Scenario: Successfully fetching trades from API
   *   Given the API is available
   *   When fetchTrades is called
   *   Then it should return the trade data
   */
  test('fetchTrades returns trade data on success', async () => {
    // Mock successful response
    const mockTrades = [
      { id: 1, symbol: 'BTC/USD', price: 50000, amount: 0.1, timestamp: '2023-01-01T12:00:00Z' },
      { id: 2, symbol: 'ETH/USD', price: 3000, amount: 1.5, timestamp: '2023-01-01T12:05:00Z' }
    ];
    
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => mockTrades
    });
    
    // Call the function
    const result = await fetchTrades();
    
    // Verify fetch was called with correct URL
    expect(fetch).toHaveBeenCalledWith('/api/trades');
    
    // Verify result matches mock data
    expect(result).toEqual(mockTrades);
  });

  /**
   * Feature: Fetch Trades Error Handling
   * 
   * Scenario: API returns an error
   *   Given the API is not available
   *   When fetchTrades is called
   *   Then it should throw an error
   */
  test('fetchTrades throws error on API failure', async () => {
    // Mock failed response
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: false,
      status: 500,
      statusText: 'Internal Server Error'
    });
    
    // Call the function and expect it to throw
    await expect(fetchTrades()).rejects.toThrow('Failed to fetch trades: 500 Internal Server Error');
  });

  /**
   * Feature: WebSocket Subscription
   * 
   * Scenario: Successfully subscribing to trade updates
   *   Given the WebSocket connection is available
   *   When subscribeToUpdates is called with a callback
   *   Then it should set up a WebSocket connection and handle messages
   */
  test('subscribeToUpdates sets up WebSocket connection', () => {
    // Mock WebSocket
    const mockWebSocket = {
      addEventListener: jest.fn(),
      send: jest.fn(),
      close: jest.fn()
    };
    
    // Mock WebSocket constructor
    global.WebSocket = jest.fn(() => mockWebSocket) as any;
    
    // Mock callback
    const mockCallback = jest.fn();
    
    // Call the function
    const unsubscribe = subscribeToUpdates(mockCallback);
    
    // Verify WebSocket was created with correct URL
    expect(WebSocket).toHaveBeenCalledWith('ws://localhost:8000/ws/trades');
    
    // Verify event listeners were added
    expect(mockWebSocket.addEventListener).toHaveBeenCalledWith('message', expect.any(Function));
    expect(mockWebSocket.addEventListener).toHaveBeenCalledWith('error', expect.any(Function));
    
    // Simulate receiving a message
    const messageHandler = mockWebSocket.addEventListener.mock.calls.find(
      call => call[0] === 'message'
    )[1];
    
    const mockTrade = { id: 3, symbol: 'BTC/USD', price: 51000, amount: 0.2, timestamp: '2023-01-01T13:00:00Z' };
    messageHandler({ data: JSON.stringify(mockTrade) });
    
    // Verify callback was called with parsed data
    expect(mockCallback).toHaveBeenCalledWith(mockTrade);
    
    // Call unsubscribe function
    unsubscribe();
    
    // Verify WebSocket was closed
    expect(mockWebSocket.close).toHaveBeenCalled();
  });

  /**
   * Feature: Chart Data Transformation
   * 
   * Scenario: Transforming trade data for chart display
   *   Given a list of trades
   *   When transformTradesForChart is called
   *   Then it should return data formatted for Chart.js
   */
  test('transformTradesForChart formats data for Chart.js', () => {
    // Sample trade data
    const trades = [
      { id: 1, symbol: 'BTC/USD', price: 50000, amount: 0.1, timestamp: '2023-01-01T12:00:00Z' },
      { id: 2, symbol: 'BTC/USD', price: 51000, amount: 0.2, timestamp: '2023-01-01T13:00:00Z' },
      { id: 3, symbol: 'ETH/USD', price: 3000, amount: 1.5, timestamp: '2023-01-01T12:00:00Z' },
      { id: 4, symbol: 'ETH/USD', price: 3100, amount: 1.0, timestamp: '2023-01-01T13:00:00Z' }
    ];
    
    // Call the function
    const chartData = transformTradesForChart(trades);
    
    // Verify structure of returned data
    expect(chartData).toHaveProperty('labels');
    expect(chartData).toHaveProperty('datasets');
    
    // Verify labels are timestamps
    expect(chartData.labels).toEqual([
      '2023-01-01T12:00:00Z',
      '2023-01-01T13:00:00Z'
    ]);
    
    // Verify datasets are grouped by symbol
    expect(chartData.datasets).toHaveLength(2); // One for BTC/USD, one for ETH/USD
    
    // Verify first dataset (BTC/USD)
    expect(chartData.datasets[0].label).toBe('BTC/USD');
    expect(chartData.datasets[0].data).toEqual([50000, 51000]);
    
    // Verify second dataset (ETH/USD)
    expect(chartData.datasets[1].label).toBe('ETH/USD');
    expect(chartData.datasets[1].data).toEqual([3000, 3100]);
  });
}); 