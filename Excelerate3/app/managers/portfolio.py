from enum import Enum
from typing import List

class Portfolio(Enum):
    ALDER = "Alder"
    WHITE_RABBIT = "White Rabbit"

class PortfolioStructure:
    """Configuration for portfolio structure and funders"""
    
    # Updated to match exact names from parser classes
    SHARED_FUNDERS = ["ACS", "BHB", "Boom", "Kings", "EFIN", "ClearView"]  # Fixed eFin -> EFIN, Clear View -> ClearView
    ALDER_SPECIFIC_FUNDERS = ["Vesper"]
    
    @classmethod
    def get_portfolio_funders(cls, portfolio: Portfolio) -> List[str]:
        """Get list of funders for a specific portfolio"""
        funders = cls.SHARED_FUNDERS.copy()
        if portfolio == Portfolio.ALDER:
            funders.extend(cls.ALDER_SPECIFIC_FUNDERS)
        return funders

    @classmethod
    def validate_portfolio_funder(cls, portfolio: Portfolio, funder: str) -> bool:
        """
        Validate that a funder belongs to a portfolio.
        
        Args:
            portfolio: Portfolio to check against
            funder: Name of the funder to validate
            
        Returns:
            bool: True if the funder is authorized for the portfolio
        """
        valid_funders = cls.get_portfolio_funders(portfolio)
        return funder in valid_funders