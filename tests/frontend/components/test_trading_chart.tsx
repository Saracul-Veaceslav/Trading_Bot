import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import { TradingChart } from '../../../frontend/src/components/TradingChart';
import { Chart } from 'chart.js/auto';

// Register required Chart.js components
Chart.register();

describe('TradingChart Component', () => {
  /**
   * Feature: Trading Chart Rendering
   * 
   * Scenario: Chart renders with provided data
   *   Given a set of trading data
   *   When the TradingChart component is rendered
   *   Then the chart should be visible in the document
   */
  test('renders chart with provided data', () => {
    // Mock chart data
    const mockData = {
      labels: ['Jan', 'Feb', 'Mar'],
      datasets: [
        {
          label: 'Price',
          data: [100, 120, 110],
          borderColor: 'rgb(75, 192, 192)',
          tension: 0.1
        }
      ]
    };
    
    // Render component with mock data
    render(<TradingChart data={mockData} />);
    
    // Check if chart container is in the document
    const chartElement = screen.getByTestId('trading-chart');
    expect(chartElement).toBeInTheDocument();
  });

  /**
   * Feature: Trading Chart Responsiveness
   * 
   * Scenario: Chart adapts to different screen sizes
   *   Given a trading chart component
   *   When rendered with responsive option set to true
   *   Then the chart should have responsive styling
   */
  test('chart is responsive', () => {
    const mockData = {
      labels: ['Jan', 'Feb', 'Mar'],
      datasets: [
        {
          label: 'Price',
          data: [100, 120, 110],
          borderColor: 'rgb(75, 192, 192)',
          tension: 0.1
        }
      ]
    };
    
    // Render with default options (which includes responsive: true)
    render(<TradingChart data={mockData} />);
    
    // Check if chart container has the appropriate class for responsiveness
    const chartElement = screen.getByTestId('trading-chart');
    expect(chartElement).toHaveClass('trading-chart');
  });

  /**
   * Feature: Trading Chart Custom Options
   * 
   * Scenario: Chart accepts and applies custom options
   *   Given a set of custom chart options
   *   When the TradingChart is rendered with these options
   *   Then the chart should apply these custom options
   */
  test('applies custom options when provided', () => {
    const mockData = {
      labels: ['Jan', 'Feb', 'Mar'],
      datasets: [
        {
          label: 'Price',
          data: [100, 120, 110],
          borderColor: 'rgb(75, 192, 192)',
          tension: 0.1
        }
      ]
    };
    
    const customOptions = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        title: {
          display: true,
          text: 'Custom Chart Title'
        }
      }
    };
    
    render(<TradingChart data={mockData} options={customOptions} />);
    
    // Verify chart container exists
    const chartElement = screen.getByTestId('trading-chart');
    expect(chartElement).toBeInTheDocument();
    
    // Note: We can't directly test if Chart.js applied the options
    // as it's internal to the Chart.js library, but we can check
    // if the component rendered without errors
  });

  /**
   * Feature: Trading Chart Data Updates
   * 
   * Scenario: Chart updates when data changes
   *   Given a trading chart with initial data
   *   When the data prop is updated
   *   Then the chart should re-render with the new data
   */
  test('updates when data changes', () => {
    // This test would ideally use act() and rerender()
    // to test component updates, but for simplicity we'll
    // just verify the component renders with different data
    
    const initialData = {
      labels: ['Jan', 'Feb', 'Mar'],
      datasets: [
        {
          label: 'Price',
          data: [100, 120, 110],
          borderColor: 'rgb(75, 192, 192)',
          tension: 0.1
        }
      ]
    };
    
    const { rerender } = render(<TradingChart data={initialData} />);
    
    // Verify initial render
    expect(screen.getByTestId('trading-chart')).toBeInTheDocument();
    
    // New data to test update
    const updatedData = {
      labels: ['Jan', 'Feb', 'Mar', 'Apr'],
      datasets: [
        {
          label: 'Price',
          data: [100, 120, 110, 130],
          borderColor: 'rgb(75, 192, 192)',
          tension: 0.1
        }
      ]
    };
    
    // Re-render with new data
    rerender(<TradingChart data={updatedData} />);
    
    // Verify component still renders after update
    expect(screen.getByTestId('trading-chart')).toBeInTheDocument();
  });
}); 