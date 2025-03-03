/**
 * Represents a trade in the system
 */
export interface Trade {
  /** Unique identifier for the trade */
  id: number;
  /** Trading pair symbol (e.g., BTC/USD) */
  symbol: string;
  /** Price at which the trade was executed */
  price: number;
  /** Amount of the base asset traded */
  amount: number;
  /** ISO timestamp of when the trade occurred */
  timestamp: string;
}

/**
 * Represents a trading strategy
 */
export interface Strategy {
  /** Unique identifier for the strategy */
  id: number;
  /** Name of the strategy */
  name: string;
  /** Description of how the strategy works */
  description: string;
  /** Whether the strategy is currently active */
  isActive: boolean;
  /** Performance metrics for the strategy */
  performance?: {
    /** Total profit/loss percentage */
    totalProfitLoss: number;
    /** Number of winning trades */
    winCount: number;
    /** Number of losing trades */
    loseCount: number;
    /** Sharpe ratio */
    sharpeRatio?: number;
  };
}

/**
 * Represents a user's portfolio
 */
export interface Portfolio {
  /** Total value of the portfolio in USD */
  totalValue: number;
  /** List of assets in the portfolio */
  assets: {
    /** Asset symbol */
    symbol: string;
    /** Amount of the asset */
    amount: number;
    /** Current value in USD */
    valueUSD: number;
    /** Percentage of the portfolio */
    percentage: number;
  }[];
  /** Performance metrics */
  performance: {
    /** Daily change percentage */
    dailyChange: number;
    /** Weekly change percentage */
    weeklyChange: number;
    /** Monthly change percentage */
    monthlyChange: number;
    /** All-time change percentage */
    allTimeChange: number;
  };
}

/**
 * Represents an API error
 */
export interface ApiError {
  /** HTTP status code */
  status: number;
  /** Error message */
  message: string;
  /** Additional error details */
  details?: Record<string, any>;
} 