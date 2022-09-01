from Python.balancesheet import BalanceSheet
import pandas as pd

class Model:
    def __init__(self, controller):
        self.controller = controller
        self.balance_sheets = dict(zip(self.actors, [BalanceSheet(i) for i in self.actors]))
        self.worker_pool = 100
        self.idle_workers = 100
        self.starting_cpi = 100
        self.current_cpi = 100
        self.starting_worker_wage = 0.6
        self.current_worker_wage = 0.6
        self.real_startup_cap = 2.5
        self.full_employment_counter = 0
        self.indicators = pd.DataFrame(
            data = {
                'GDP': [0],
                '12M GDP': [0],
                'Money Supply': [0],
                'TTM Average Money Supply': [0],
                'Worker Incomes': [0],
                'Capitalist Incomes': [0],
                'Firm Incomes': [0],
                'New Business Formation': [0],
                'TTM New Business Formation': [0]
            }
        )
        
        self.fiat_indicators = pd.DataFrame(
            data = {
                'Nom GDP': [0],
                'Real GDP': [0],
                '12M Nom GDP': [0],
                '12M Real GDP': [0],
                'Unemployment': [self.idle_workers / self.worker_pool],
                'Nom Wages': [0],
                'Real Wages': [0],
                'TTM Nom Wages': [0],
                'TTM Real Wages': [0],
                'New Business Formation': [0],
                'TTM New Business Formation': [0],
                'CPI': [self.current_cpi]
            }
        )
    
    @property
    def actors(self):
        if self.controller.economy == 'credit':
            return ['Banks', 'Capitalists', 'Firms', 'Workers']
        elif self.controller.economy == 'fiat':
            return ['Treasury', 'Capitalists', 'Firms', 'Workers']
        
    
        
        
        