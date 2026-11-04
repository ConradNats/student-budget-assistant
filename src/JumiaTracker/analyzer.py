"""Price analysis and visualization tools for Jumia price tracking."""

import os
from typing import Optional

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd


class PriceAnalyzer:
    """Analyze and visualize product price history."""
    
    def __init__(self, csv_path: str, product_name: str = "Product"):
        """
        Initialize the analyzer.
        
        Args:
            csv_path: Path to CSV file with price history
            product_name: Name of the product for display
        """
        self.csv_path = csv_path
        self.product_name = product_name
        self.df = None
    
    def load_data(self) -> pd.DataFrame:
        """Load and preprocess price data."""
        try:
            self.df = pd.read_csv(self.csv_path)
            self.df['Date'] = pd.to_datetime(self.df['Date'])
            self.df = self.df.sort_values('Date')
            return self.df
        except FileNotFoundError:
            raise FileNotFoundError(f"Error: {self.csv_path} not found. Run the scraper or test data generator first.")
    
    def analyze(self) -> dict:
        """
        Perform price analysis.
        
        Returns:
            Dictionary with analysis results
        """
        if self.df is None:
            self.load_data()
        
        current_price = self.df['Price_UGX'].iloc[-1]
        average_price = self.df['Price_UGX'].mean()
        highest_price = self.df['Price_UGX'].max()
        lowest_price = self.df['Price_UGX'].min()
        median_price = self.df['Price_UGX'].median()
        
        diff_percent = ((current_price - average_price) / average_price) * 100
        
        if diff_percent < 0:
            status = "BELOW"
            message = f"GOOD DEAL! Current price is {abs(diff_percent):.1f}% below the average."
        elif diff_percent > 0:
            status = "ABOVE"
            message = f"OVERPRICED. Current price is {abs(diff_percent):.1f}% above the average."
        else:
            status = "AT"
            message = "Current price is equal to the average."
        
        results = {
            "product_name": self.product_name,
            "start_date": self.df['Date'].iloc[0].date(),
            "end_date": self.df['Date'].iloc[-1].date(),
            "current_price": current_price,
            "average_price": average_price,
            "median_price": median_price,
            "highest_price": highest_price,
            "lowest_price": lowest_price,
            "diff_percent": diff_percent,
            "status": status,
            "message": message
        }
        
        return results
    
    def print_analysis(self):
        """Print analysis results to console."""
        results = self.analyze()
        print(f"--- Price Analysis for {results['product_name']} ---")
        print(f"Data range: {results['start_date']} to {results['end_date']}")
        print(f"Current Price:  {results['current_price']:,.0f} UGX")
        print(f"Average Price:  {results['average_price']:,.0f} UGX")
        print(f"Median Price:   {results['median_price']:,.0f} UGX")
        print(f"Highest Price:  {results['highest_price']:,.0f} UGX")
        print(f"Lowest Price:   {results['lowest_price']:,.0f} UGX")
        print(f"\n{results['message']}")
    
    def plot_price_history(self, save_path: str = "price_history_chart.png", show: bool = False):
        """
        Generate and save price history visualization.
        
        Args:
            save_path: Path to save the chart
            show: Whether to display the plot
        """
        if self.df is None:
            self.load_data()
        
        results = self.analyze()
        average_price = results['average_price']
        
        plt.figure(figsize=(10, 6))
        plt.plot(self.df['Date'], self.df['Price_UGX'], marker='o', 
                linestyle='-', color='blue', label='Daily Price')
        plt.axhline(y=average_price, color='r', linestyle='--', 
                   label=f'Average ({average_price:,.0f} UGX)')
        
        formatter = ticker.StrMethodFormatter('{x:,.0f} UGX')
        plt.gca().yaxis.set_major_formatter(formatter)
        plt.gcf().autofmt_xdate()
        
        plt.title(f'Price History: {self.product_name}\n{results["message"]}')
        plt.xlabel('Date')
        plt.ylabel('Price (UGX)')
        plt.legend()
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Chart saved as {save_path}")
        
        if show:
            plt.show()
        else:
            plt.close()
    
    def analyze_and_visualize(self, save_path: str = "price_history_chart.png"):
        """Run full analysis with visualization."""
        self.load_data()
        self.print_analysis()
        self.plot_price_history(save_path=save_path)


def analyze_prices(csv_path: str, product_name: str = "Example Product", 
                   save_path: str = "price_history_chart.png"):
    """
    Convenience function for price analysis.
    
    Args:
        csv_path: Path to CSV file
        product_name: Product name
        save_path: Output chart path
    """
    analyzer = PriceAnalyzer(csv_path, product_name)
    analyzer.analyze_and_visualize(save_path)
