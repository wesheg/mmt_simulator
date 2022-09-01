import pandas as pd

class BalanceSheet:
    """
    Cumulative Balance Sheet for an economic actor
    """
    TOP_ACCOUNTS = ['Assets', 'Liabilities', 'Equity', 'Liabs & Eq']

    def __init__(self, actor):
        self.actor = actor
        self.df = pd.DataFrame(
            data={actor: [0 for i in self.TOP_ACCOUNTS]},
            index=pd.MultiIndex.from_product([self.TOP_ACCOUNTS, ['Total']])
        )
        self.df.index.names = ['Balance Sheet', 'Account']

    def add_account(self, type, name, balance=0):
        df2 = pd.DataFrame(
            data={self.actor: [balance]},
            index=pd.MultiIndex.from_arrays([[type], [name]])
        )
        self.df = self.df.append(df2)
        self.calc_totals()
        self.sort_df()

    def add_flow(self, account_in, account_out, amount):
        # add the accounts if they're not already available
        for acct in [account_in, account_out]:
            if acct not in self.df.index:
                self.add_account(acct[0], acct[1])

        in_type = account_in[0]
        out_type = account_out[0]
        self.df.loc[account_in] += amount
        if in_type == 'Assets' and out_type in ['Liabilities', 'Equity']:
            # increase an asset & increase a liab/equity to balance
            self.df.loc[account_out] += amount
        elif in_type in ['Liabilities', 'Equity'] and out_type =='Assets':
            # increase a liab/equity and increase an asset to balance
            self.df.loc[account_out] += amount
        else:
            # offset an increase with a decrease of the same account type
            self.df.loc[account_out] -= amount
        
        # recalculate the totals
        self.calc_totals()

    def calc_totals(self):
        for account in self.TOP_ACCOUNTS:
            sum_accounts = self.df.loc[account].sum()[0]
            old_total = self.df.loc[account, 'Total'][0]
            new_sum = sum_accounts - old_total
            self.df.loc[account, 'Total'] = new_sum
        self.df.loc['Liabs & Eq', 'Total'] = self.df.loc['Liabilities', 'Total'][0] + self.df.loc['Equity', 'Total'][0]

    def sort_df(self):
        l = []
        for i in self.df.index:
            if i[0] == 'Assets':
                l.append(1)
            elif i[0] == 'Liabilities':
                l.append(2)
            else:
                l.append(3)

            if i[1] == 'Total':
                l[-1] += 0.1

        self.df['sort'] = l
        self.df.sort_values(by='sort', inplace=True)
        del self.df['sort']

    def make_loan(self, amt):
        if self.actor == 'Banks':
            # add to loan asset, subtract from cash
            self.add_flow(('Assets', 'Capitalists Loans'), ('Assets', 'Cash'), amt)
            # add to capitalists accounts, subtract from reserves
            self.add_flow(('Liabilities', 'Capitalists Accounts'), ('Equity', 'Bank Reserves'), amt)
            
        elif self.actor == 'Capitalists':
            # add to cash asset, offset with loan liability
            self.add_flow(('Assets', 'Cash'), ('Liabilities', 'Capitalists Loans'), amt)
            
    def invest(self, amt):
        if self.actor == 'Firms':
            # add to cash, offset with equity
            self.add_flow(('Assets', 'Cash'), ('Equity', 'Firm Equity'), amt)
            
        elif self.actor == 'Capitalists':
            # add Firm Equity, reduce cash
            self.add_flow(('Assets', 'Investments'), ('Assets', 'Cash'), amt)
            
        elif self.actor == 'Banks':
            # move cash from capitalist accounts to firm accounts
            self.add_flow(('Liabilities', 'Firm Accounts'), ('Liabilities', 'Capitalists Accounts'), amt)
            
    def pay_workers(self, amt):
        if self.actor == 'Firms':
            # take cash, offset with reduction in equity
            self.add_flow(('Assets', 'Cash'), ('Equity', 'Firm Equity'), -amt)
            
#         elif self.actor == 'Capitalists':
#             # markdown firm equity asset
#             self.add_flow(('Assets', 'Investments'), ('Equity', 'Firm Profit(Loss)'), -amt)
        
        elif self.actor == 'Workers':
            # add to cash, offset with equity
            self.add_flow(('Assets', 'Cash'), ('Equity', 'Wages'), amt)
            
        elif self.actor == 'Banks':
            # move money from firm accounts to worker accounts
            self.add_flow(('Liabilities', 'Worker Accounts'), ('Liabilities', 'Firm Accounts'), amt)
            
    def pay_capitalists(self, amt):
        if self.actor == 'Firms':
            # take cash, offset with reduction in equity
            self.add_flow(('Assets', 'Cash'), ('Equity', 'Firm Equity'), -amt)
        
        elif self.actor == 'Capitalists':
            # add to cash, offset with equity
            self.add_flow(('Assets', 'Cash'), ('Equity', 'Dividends'), amt)
            
        elif self.actor == 'Banks':
            # move money from firm accounts to capitalists accounts
            self.add_flow(('Liabilities', 'Capitalists Accounts'), ('Liabilities', 'Firm Accounts'), amt)
            
    def workers_consume(self, amt):
        if self.actor == 'Firms':
            # record revenue
            self.add_flow(('Assets', 'Cash'), ('Equity', 'Firm Equity'), amt)
            
#         elif self.actor == 'Capitalists':
#             # markdown firm equity asset
#             self.add_flow(('Assets', 'Firm Equity'), ('Equity', 'Firm Profit(Loss)'), amt)
        
        elif self.actor == 'Workers':
            # reduce cash and equity
            self.add_flow(('Assets', 'Cash'), ('Equity', 'Consumption'), -amt)
            
        elif self.actor == 'Banks':
            # move money from worker accounts to firm accounts
            self.add_flow(('Liabilities', 'Firm Accounts'), ('Liabilities', 'Worker Accounts'), amt)
            
    def capitalists_consume(self, amt):
        if self.actor == 'Firms':
            # record revenue
            self.add_flow(('Assets', 'Cash'), ('Equity', 'Firm Equity'), amt)
            
        elif self.actor == 'Capitalists':
#             # markdown firm equity asset
#             self.add_flow(('Assets', 'Firm Equity'), ('Equity', 'Firm Profit(Loss)'), amt)
            # consumption
            self.add_flow(('Assets', 'Cash'), ('Equity', 'Consumption'), -amt)
            
        elif self.actor == 'Banks':
            # move money from capitalists accounts to firm accounts
            self.add_flow(('Liabilities', 'Firm Accounts'), ('Liabilities', 'Capitalists Accounts'), amt)
            
    def repay_loan(self, amt):
        if self.actor == 'Banks':
            # add to cash, subtract from capitalists loan
            self.add_flow(('Assets','Cash'), ('Assets', 'Capitalists Loans'), amt)
            # add to bank reserves, subtract from capitalists accounts
            self.add_flow(('Equity', 'Bank Reserves'), ('Liabilities', 'Capitalists Accounts'), amt)
            
        elif self.actor == 'Capitalists':
            # reduce cash, offset with reduction in liab
            self.add_flow(('Assets', 'Cash'), ('Liabilities', 'Capitalists Loans'), -amt)
            
    def fiscal_op(self, amt):
        if amt <= 0:
            treasury_acct = 'Spending'
            cap_acct = ('Liabilities', 'Govt Contracts')
        else:
            treasury_acct = 'Taxes'
            cap_acct = ('Equity', 'Taxes Paid')
            
        if self.actor == 'Treasury':
            # spend or tax firms
            self.add_flow(('Assets',  'Cash'), ('Equity', treasury_acct), amt)
            
        elif self.actor == 'Capitalists':
            # collect from Treasury
            self.add_flow(('Assets', 'Cash'), cap_acct, -amt)

                
                
            
