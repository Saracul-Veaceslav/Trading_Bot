import React, { useState, useEffect } from 'react';
import { TradingChart } from '../components/TradingChart';
import { TradeList } from '../components/TradeList';
import { fetchTrades, subscribeToUpdates, transformTradesForChart } from '../api/trading';
import { Trade } from '../types';
import './Dashboard.css';

export const Dashboard: React.FC = () => {
  const [trades, setTrades] = useState<Trade[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  
  useEffect(() => {
    const loadData = async () => {
      try {
        setIsLoading(true);
        setError(null);
        const data = await fetchTrades();
        setTrades(data);
      } catch (err) {
        console.error('Failed to fetch trades:', err);
        setError('Failed to load trade data. Please try again later.');
      } finally {
        setIsLoading(false);
      }
    };
    
    loadData();
    
    // Subscribe to real-time updates
    const unsubscribe = subscribeToUpdates((update) => {
      setTrades(current => {
        // Check if this trade already exists (by ID)
        const exists = current.some(trade => trade.id === update.id);
        if (exists) {
          // Replace the existing trade
          return current.map(trade => 
            trade.id === update.id ? update : trade
          );
        } else {
          // Add the new trade
          return [...current, update];
        }
      });
    });
    
    // Cleanup function to unsubscribe when component unmounts
    return () => unsubscribe();
  }, []);
  
  if (isLoading) {
    return (
      <div className="dashboard-loading">
        <div className="spinner"></div>
        <p>Loading...</p>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="dashboard-error">
        <h2>Error</h2>
        <p>{error}</p>
        <button onClick={() => window.location.reload()}>Retry</button>
      </div>
    );
  }
  
  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>Trading Dashboard</h1>
        <div className="dashboard-controls">
          <button className="refresh-button" onClick={async () => {
            setIsLoading(true);
            try {
              const data = await fetchTrades();
              setTrades(data);
              setError(null);
            } catch (err) {
              console.error('Failed to refresh trades:', err);
              setError('Failed to refresh trade data.');
            } finally {
              setIsLoading(false);
            }
          }}>
            Refresh
          </button>
        </div>
      </header>
      
      <div className="dashboard-content">
        <section className="chart-section">
          <h2>Price Chart</h2>
          <div className="chart-container">
            <TradingChart 
              data={transformTradesForChart(trades)}
            />
          </div>
        </section>
        
        <section className="trades-section">
          <TradeList trades={trades} />
        </section>
      </div>
    </div>
  );
}; 