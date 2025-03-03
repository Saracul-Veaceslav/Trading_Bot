import { Trade } from '../types';
import { ChartData } from 'chart.js';

/**
 * Fetches trade data from the API
 * @returns Promise resolving to an array of trades
 */
export const fetchTrades = async (): Promise<Trade[]> => {
  const response = await fetch('/api/v1/trades');
  
  if (!response.ok) {
    throw new Error(`Failed to fetch trades: ${response.status} ${response.statusText}`);
  }
  
  return await response.json();
};

/**
 * Subscribes to real-time trade updates via WebSocket
 * @param callback Function to call when a new trade is received
 * @returns Function to unsubscribe from updates
 */
export const subscribeToUpdates = (callback: (trade: Trade) => void): () => void => {
  // Create WebSocket connection
  const ws = new WebSocket('ws://localhost:8000/ws/v1/trades');
  
  // Handle incoming messages
  ws.addEventListener('message', (event) => {
    try {
      const trade = JSON.parse(event.data);
      callback(trade);
    } catch (error) {
      console.error('Error parsing WebSocket message:', error);
    }
  });
  
  // Handle errors
  ws.addEventListener('error', (error) => {
    console.error('WebSocket error:', error);
  });
  
  // Return unsubscribe function
  return () => {
    ws.close();
  };
};

/**
 * Transforms trade data into a format suitable for Chart.js
 * @param trades Array of trades to transform
 * @returns ChartData object for use with Chart.js
 */
export const transformTradesForChart = (trades: Trade[]): ChartData<'line'> => {
  // Extract unique timestamps and sort them
  const timestamps = Array.from(new Set(trades.map(trade => trade.timestamp))).sort();
  
  // Extract unique symbols
  const symbols = Array.from(new Set(trades.map(trade => trade.symbol)));
  
  // Generate random colors for each symbol
  const colors = symbols.map(() => {
    const r = Math.floor(Math.random() * 200);
    const g = Math.floor(Math.random() * 200);
    const b = Math.floor(Math.random() * 200);
    return `rgb(${r}, ${g}, ${b})`;
  });
  
  // Create datasets for each symbol
  const datasets = symbols.map((symbol, index) => {
    // Filter trades for this symbol
    const symbolTrades = trades.filter(trade => trade.symbol === symbol);
    
    // Create data points for each timestamp
    const data = timestamps.map(timestamp => {
      const trade = symbolTrades.find(t => t.timestamp === timestamp);
      return trade ? trade.price : null;
    });
    
    return {
      label: symbol,
      data,
      borderColor: colors[index],
      backgroundColor: `${colors[index].replace('rgb', 'rgba').replace(')', ', 0.1)')}`,
      borderWidth: 2,
      pointBackgroundColor: colors[index],
      pointRadius: 3,
      fill: false,
      tension: 0.1
    };
  });
  
  return {
    labels: timestamps,
    datasets
  };
}; 