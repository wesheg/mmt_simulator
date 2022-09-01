from Python.view import View
from Python.model import Model
from time import sleep
from threading import Thread
import pandas as pd
from math import inf, log

class Controller:
    def __init__(self, economy='credit'):
        self.economy = economy
        self.model = Model(self)
        self.view = View(self)
        self.economy_init()
        self.view_init()
    
    @property
    def app(self):
        return self.view.build_app()
    
    def view_init(self):
        if self.economy == 'credit':
            self.view.build_credit_widgets()
        elif self.economy == 'fiat':
            self.view.build_fiat_widgets()
            
    def economy_init(self):
        if self.economy == 'credit':
            self.credit_econ_init()
        elif self.economy == 'fiat':
            self.fiat_econ_init()
            
    def credit_econ_init(self):
        """Initialize Credit Economy Simulation"""
        total_money_supply = 100
        # add bank accounts
        self.model.balance_sheets['Banks'].add_account('Assets', 'Cash', total_money_supply)
        self.model.balance_sheets['Banks'].add_account('Equity', 'Bank Reserves', total_money_supply)
        
    def fiat_econ_init(self):
        """Initialize Fiat Economy Simulation"""
        # add bank accounts
        self.model.balance_sheets['Treasury'].add_account('Assets', 'Cash', 0)
        self.model.balance_sheets['Treasury'].add_account('Equity', 'Spending', 0)
        self.model.balance_sheets['Treasury'].add_account('Equity', 'Taxes', 0)
        
    def refresh_balance_sheets(self):
        for actor, bs in self.view.widgets['datagrids'].items():
            bs.data = self.model.balance_sheets[actor].df
            
    def make_loan(self, amt):
        for actor, bs in self.model.balance_sheets.items():
            bs.make_loan(amt)
        self.refresh_balance_sheets()
        
    def invest(self, amt):
        for actor, bs in self.model.balance_sheets.items():
            bs.invest(amt)
        self.refresh_balance_sheets()
        
    def pay_workers(self, amt):
        for actor, bs in self.model.balance_sheets.items():
            bs.pay_workers(amt)
        self.refresh_balance_sheets()
        
    def workers_consume(self, amt):
        for actor, bs in self.model.balance_sheets.items():
            bs.workers_consume(amt)
        self.refresh_balance_sheets()
        
    def capitalists_consume(self, amt):
        for actor, bs in self.model.balance_sheets.items():
            bs.capitalists_consume(amt)
        self.refresh_balance_sheets()
        
    def pay_capitalists(self, amt):
        for actor, bs in self.model.balance_sheets.items():
            bs.pay_capitalists(amt)
        self.refresh_balance_sheets()
        
    def repay_loan(self, amt):
        for actor, bs in self.model.balance_sheets.items():
            bs.repay_loan(amt)
        self.refresh_balance_sheets()
        
    def fiscal_op(self, amt):
        for actor, bs in self.model.balance_sheets.items():
            bs.fiscal_op   (amt)
        self.refresh_balance_sheets()
        
    @staticmethod
    def loan_payment(principal, annual_r, years):
        n = years * 12  # number of monthly payments
        r = (annual_r / 100) / 12  # decimal monthly interest rate from APR
        pmt = (r * principal * ((1+r) ** n)) / (((1+r) ** n) - 1)
        return pmt
        
    def _simulate_credit_econ(self):
        # simulate for 25 years
        for i in range(25*12):
            self.credit_econ_frame()
            sleep(0.2)
            
    def simulate_credit_econ(self, evt):
        myThread = Thread(target=self._simulate_credit_econ)
        myThread.start()
        
    def _simulate_fiat_econ(self):
        # simulate for 10 years
        for i in range(10*12):
            self.fiat_econ_frame()
            sleep(0.2)
            
    def _simulate_fiat_econ_1yr(self):
        # simulate for 1 year
        for i in range(12):
            self.fiat_econ_frame()
            sleep(0.2)
        
    def fiat_econ_1yr(self, evt):
        myThread = Thread(target=self._simulate_fiat_econ_1yr)
        myThread.start()
        
    def simulate_fiat_econ(self, evt):
        myThread = Thread(target=self._simulate_fiat_econ)
        myThread.start()
           
    @staticmethod
    def cpi_growth(unemp, full_emp_counter):
        """full_emp_counter will accelerate inflation the longer the economy stays in full employment
        minimum is zero
        """
        if full_emp_counter > 0:
            adj_unemp = 0.01 * 10**-full_emp_counter
        else:
            adj_unemp = max(0.01, unemp)
        logit_func = log(adj_unemp / (1 - adj_unemp))
        annualized_growth = -logit_func / (100)
        monthly_change = (annualized_growth / 12)
        return monthly_change
    
    @staticmethod
    def cpi(current_cpi, cpi_growth):
        return current_cpi * (1 + cpi_growth)
    
    def fiat_econ_frame(self):
        balance_sheets = self.model.balance_sheets
        deflator = 1 / (self.model.current_cpi / self.model.starting_cpi)
        wage_deflator = 1 / (self.model.current_worker_wage / self.model.starting_worker_wage) # <-- wages inflate half as fast as prices
        # check govt surplus
        govt_surplus = self.view.widgets['inputs'][0].value / 12.0
        govt_spending = 0
        if govt_surplus < 0:
            govt_spending = -govt_surplus
        
        # spend or tax capitalists
        self.fiscal_op(govt_surplus)
        
        # invest if possible
        i = 0 # <-- addition to GDP
        new_businesses = 0 # <-- addition to business formation
        capitalists_cash = balance_sheets['Capitalists'].df.loc['Assets', 'Cash'][0]
        capitalists_reserve = 3
        nom_startup_capital = self.model.real_startup_cap / deflator
        if capitalists_cash - capitalists_reserve > nom_startup_capital:
            new_businesses += int((capitalists_cash - capitalists_reserve) / nom_startup_capital)
            i += nom_startup_capital * new_businesses
            self.invest(i)
            
        # firms hire workers
        try:
            firm_cash = balance_sheets['Firms'].df.loc['Assets', 'Cash'][0]
        except KeyError:
            firm_cash = 0
        workers_needed = new_businesses * 3
        if new_businesses == 0:
            workers_needed = -1
        self.model.idle_workers = min(self.model.worker_pool, max(0, self.model.idle_workers - workers_needed))
        if self.model.idle_workers == 0:
            self.model.full_employment_counter += 1
        else:
            self.model.full_employment_counter = max(self.model.full_employment_counter - 1, 0)
        unemp = min(0.99, self.model.idle_workers / self.model.worker_pool)
        price_inflation = self.cpi_growth(unemp, self.model.full_employment_counter)
        wage_inflation = price_inflation * 0.5
        self.model.current_cpi = self.cpi(self.model.current_cpi, price_inflation)
        
        # firms pay workers
        payroll = self.model.current_worker_wage * (self.model.worker_pool - self.model.idle_workers)
        self.model.current_worker_wage * (1 + wage_inflation)
        self.pay_workers(payroll)
        
        # capitalists consume
        try:
            capitalists_investments = balance_sheets['Capitalists'].df.loc['Assets', 'Investments'][0]
        except KeyError:
            capitalists_investments = 0
        k_consumption = max(0, 0.4 * (capitalists_cash - capitalists_reserve))
        if capitalists_investments > 0:
            self.capitalists_consume(k_consumption)
            
        # workers consume
        try:
            worker_cash = balance_sheets['Workers'].df.loc['Assets', 'Cash'][0]
        except KeyError:
            worker_cash = 0
        w_consumption = 0.9 * worker_cash
        if capitalists_investments > 0:
            self.workers_consume(w_consumption)
        
        # firms pay capitalists
        earnings = 0.1 * firm_cash
        self.pay_capitalists(earnings)
        
        # calculate econ indicators
        gdp = w_consumption + k_consumption + i + govt_spending
        real_gdp = gdp * deflator
        
        # append to indicators dataframe
        df = pd.DataFrame(
            data = {
                'Nom GDP': [gdp],
                'Real GDP': [real_gdp],
                '12M Nom GDP': [gdp + sum(list(self.model.fiat_indicators['Nom GDP'])[-11:])],
                '12M Real GDP': [real_gdp + sum(list(self.model.fiat_indicators['Real GDP'])[-11:])],
                'Unemployment': [unemp],
                'Nom Wages': [payroll],
                'Real Wages': [payroll * wage_deflator],
                'TTM Nom Wages': [payroll + sum(list(self.model.fiat_indicators['Nom Wages'])[-11:])],
                'TTM Real Wages': [payroll * deflator + sum(list(self.model.fiat_indicators['Real Wages'])[-11:])],
                'New Business Formation': [new_businesses],
                'TTM New Business Formation': [new_businesses + sum(list(self.model.fiat_indicators['New Business Formation'])[-11:])],
                'CPI': [self.model.current_cpi]
            }
        )
        
        self.model.fiat_indicators = self.model.fiat_indicators.append(df, ignore_index=True)
        
        # refresh charts
        self.refresh_charts()
        

        
    def credit_econ_frame(self):
        balance_sheets = self.model.balance_sheets
    
        # make a loan if possible
        required_bank_reserves = self.view.widgets['inputs'][0].value
        current_bank_reserves = balance_sheets['Banks'].df.loc['Equity', 'Bank Reserves'][0]
        lending_amt = 5
        if current_bank_reserves >= lending_amt + required_bank_reserves:
            self.make_loan(lending_amt)
            
        # invest in a firm if possible
        required_startup_capital = 2.5
        i = 0  # <-- addition to GDP
        new_businesses = 0 # <-- addition to business formation
        capitalists_cash = balance_sheets['Capitalists'].df.loc['Assets', 'Cash'][0]
        capitalists_reserve = 10
        if capitalists_cash - capitalists_reserve > required_startup_capital:
            new_businesses += int((capitalists_cash - capitalists_reserve) / required_startup_capital)
            i += required_startup_capital * new_businesses
            self.invest(i)
            
        # firms pay workers
        try:
            firm_cash = balance_sheets['Firms'].df.loc['Assets', 'Cash'][0]
        except KeyError:
            firm_cash = 0
        payroll = 0.6 * firm_cash
        self.pay_workers(payroll)
            
        # workers consume
        try:
            worker_cash = balance_sheets['Workers'].df.loc['Assets', 'Cash'][0]
        except KeyError:
            worker_cash = 0
        w_consumption = 0.9 * worker_cash
        self.workers_consume(w_consumption)
        
        # capitalists consume
        k_consumption = max(0, 0.4 * (capitalists_cash - capitalists_reserve))
        self.capitalists_consume(k_consumption)
            
        # firms pay capitalists
        earnings = 0.1 * firm_cash
        self.pay_capitalists(earnings)
            
        # capitalists repay loans
        interest_rate = 0.04
        try:
            loan_balance = balance_sheets['Capitalists'].df.loc['Liabilities', 'Capitalists Loans'][0]
        except KeyError:
            loan_balance = 0
        pmt = self.loan_payment(loan_balance, interest_rate, 5)
        if capitalists_cash >= pmt:
            self.repay_loan(pmt)
            
        
        # calculate econ indicators
        gdp = w_consumption + k_consumption + i
        money_supply = 100 - balance_sheets['Banks'].df.loc['Equity', 'Bank Reserves'][0]
        
        # append to indicators dataframe
        df = pd.DataFrame(
            data = {
                'GDP': [gdp],
                '12M GDP': [gdp + sum(list(self.model.indicators['GDP'])[-11:])],
                'Money Supply': [money_supply],
                'TTM Average Money Supply': [(money_supply + sum(list(self.model.indicators['Money Supply'])[-11:])) / 12],
                'Worker Incomes': [payroll],
                'Capitalist Incomes': [earnings],
                'Firm Incomes': [w_consumption + k_consumption],
                'New Business Formation': [new_businesses],
                'TTM New Business Formation': [new_businesses + sum(list(self.model.indicators['New Business Formation'])[-11:])]
            }
        )
        
        self.model.indicators = self.model.indicators.append(df, ignore_index=True)
        
        # refresh charts
        self.refresh_charts()
        
    def refresh_charts(self):
        if self.economy == 'credit':
            # update x axis
            for i in ['gdp', 'money_supply', 'incomes']:
                for j in range(len(self.view.widgets[i].data)):
                    self.view.widgets[i].data[j].x = self.model.indicators.index


            self.view.widgets['gdp'].data[0].y = self.model.indicators['12M GDP']
            self.view.widgets['gdp'].data[1].y = self.model.indicators['TTM New Business Formation']
            self.view.widgets['money_supply'].data[0].y = self.model.indicators['TTM Average Money Supply']
            self.view.widgets['incomes'].data[0].y = self.model.indicators['Worker Incomes']
            self.view.widgets['incomes'].data[1].y = self.model.indicators['Capitalist Incomes']
            self.view.widgets['incomes'].data[2].y = self.model.indicators['Firm Incomes']
            
        elif self.economy == 'fiat':
            # update x axis
            for i in ['gdp', 'incomes', 'unemployment']:
                for j in range(len(self.view.widgets[i].data)):
                    self.view.widgets[i].data[j].x = self.model.fiat_indicators.index
                    
            self.view.widgets['gdp'].data[0].y = self.model.fiat_indicators['12M Nom GDP']
            self.view.widgets['gdp'].data[1].y = self.model.fiat_indicators['12M Real GDP']
            self.view.widgets['gdp'].data[2].y = self.model.fiat_indicators['TTM New Business Formation']
            self.view.widgets['unemployment'].data[0].y = self.model.fiat_indicators['Unemployment']
            self.view.widgets['inflation'].data[0].y = self.model.fiat_indicators['CPI']
        
        
        
        
            
            
        
            
            