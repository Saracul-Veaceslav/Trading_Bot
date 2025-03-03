import React from 'react';
import { Trade } from '../types';

interface TradeListProps {
  trades: Trade[];
}

export const TradeList: React.FC<TradeListProps> = ({ trades }) => {
  if (trades.length === 0) {
    return <div className="trade-list-empty">No trades available</div>;
  }

  return (
    <div className="trade-list" data-testid="trade-list">
      <h2>Recent Trades</h2>
      <table>
        <thead>
          <tr>
            <th>Symbol</th>
            <th>Price</th>
            <th>Amount</th>
            <th>Value</th>
            <th>Time</th>
          </tr>
        </thead>
        <tbody>
          {trades.map((trade) => (
            <tr key={trade.id} data-testid={`trade-${trade.id}`}>
              <td>{trade.symbol}</td>
              <td>
                {new Intl.NumberFormat('en-US', {
                  style: 'currency',
                  currency: 'USD'
                }).format(trade.price)}
              </td>
              <td>{trade.amount.toFixed(6)}</td>
              <td>
                {new Intl.NumberFormat('en-US', {
                  style: 'currency',
                  currency: 'USD'
                }).format(trade.price * trade.amount)}
              </td>
              <td>
                {new Date(trade.timestamp).toLocaleString()}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}; 