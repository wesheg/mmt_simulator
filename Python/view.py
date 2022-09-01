import pandas as pd
import ipywidgets
import plotly.graph_objects as go
from ipydatagrid import DataGrid, TextRenderer
from Python.balancesheet import BalanceSheet
from plotly.subplots import make_subplots

class View:
    def __init__(self, controller):
        self.controller = controller
        
    def build_balance_sheets(self):
        actors = self.controller.model.actors
        bs_dict = dict(zip(actors, [
            DataGrid(
                dataframe=balance_sheet.df,
                layout={'height': '300px'},
                column_widths={'Balance Sheet': 110,
                               'Account': 110,
                               name: 75},
                renderers={name: TextRenderer(format='.2f', horizontal_alignment='center')}
            )
            for name, balance_sheet in self.controller.model.balance_sheets.items()
        ]))
        return bs_dict
        
    def build_fiat_widgets(self):
        self.widgets = {}
        self.widgets['datagrids'] = self.build_balance_sheets()
        
        self.widgets['gdp'] = self.make_real_gdp_plot()
        
        self.widgets['incomes'] = go.FigureWidget(
            data = [
                go.Scatter(name='Nominal Worker Wages'),
                go.Scatter(name='Real Worker Wages')
            ],
            layout = {
                'margin': dict(zip(['t', 'l', 'b', 'r'], [60]+[20]*3)),
                'height': 250,
                'title': {
                    'text': 'Incomes',
                    'y': 0.85
                },
                'legend': {
                    'yanchor': 'top',
                    'y': 0.99,
                    'xanchor': 'left',
                    'x': 0.01,
                    'bgcolor': 'rgba(0,0,0,0)'
                }
            }
        )
        
        self.widgets['unemployment'] = go.FigureWidget(
            data=[
                go.Scatter()
            ],
            layout = {
                'margin': dict(zip(['t', 'l', 'b', 'r'], [60]+[20]*3)),
                'height': 250,
                'title': {
                    'text': 'TTM Average Unemployment',
                    'y': 0.85
                },
                'yaxis': {'range': [0, 1]}
            }
        )

        self.widgets['inflation'] = go.FigureWidget(
            data=[
                go.Scatter()
            ],
            layout = {
                'margin': dict(zip(['t', 'l', 'b', 'r'], [60]+[20]*3)),
                'height': 250,
                'title': {
                    'text': 'Inflation (CPI)',
                    'y': 0.85
                }
            }
        )
        
        self.widgets['inputs'] = [
            ipywidgets.IntSlider(
                value=0,
                min=-100,
                max=100,
                description='Annual Budget Surplus',
                style={'description_width': 'initial'},
                layout={'width': '400px'},
                readout_format='$.0f'
            ),
            ipywidgets.Button(
                description='Run 1 Year', 
                layout={'width': '100px'}, 
                style=ipywidgets.ButtonStyle(button_color='green')
            ),
            ipywidgets.Button(
                description='Run 10 Years', 
                layout={'width': '100px'}, 
                style=ipywidgets.ButtonStyle(button_color='green')
            )
        ]
        
        self.widgets['inputs'][1].on_click(self.controller.fiat_econ_1yr)
        self.widgets['inputs'][2].on_click(self.controller.simulate_fiat_econ)
        
    
    def build_credit_widgets(self):
        self.widgets = {}

        self.widgets['datagrids'] = self.build_balance_sheets()
        
        self.widgets['gdp'] = self.make_gdp_plot()
        
        self.widgets['incomes'] = go.FigureWidget(
            data=[
                go.Scatter(name='Workers'),
                go.Scatter(name='Capitalists'),
                go.Scatter(name='Firms')
            ],
            layout = {
                'margin': dict(zip(['t', 'l', 'b', 'r'], [60]+[20]*3)),
                'height': 250,
                'title': {
                    'text': 'Incomes',
                    'y': 0.85
                },
                'legend': {
                    'yanchor': 'top',
                    'y': 0.99,
                    'xanchor': 'left',
                    'x': 0.01,
                    'bgcolor': 'rgba(0,0,0,0)'
                }
            }
        )
        
        self.widgets['money_supply'] = go.FigureWidget(
            data=[
                go.Scatter()
            ],
            layout = {
                'margin': dict(zip(['t', 'l', 'b', 'r'], [60]+[20]*3)),
                'height': 250,
                'title': {
                    'text': 'TTM Average Money Supply',
                    'y': 0.85
                }
            }
        )
        
        self.widgets['inputs'] = [
            ipywidgets.IntSlider(
                value=50,
                min=1,
                max=100,
                description='Required Bank Reserves',
                style={'description_width': 'initial'},
                layout={'width': '400px'},
                readout_format='$.0f'
            ),
            ipywidgets.Button(
                description='Run', 
                layout={'width': '50px'}, 
                style=ipywidgets.ButtonStyle(button_color='green')
            )
        ]
        
        self.widgets['inputs'][1].on_click(self.controller.simulate_credit_econ)
    
    @staticmethod
    def make_gdp_plot():
        n = make_subplots(specs=[[{"secondary_y": True}]])
        n.add_trace(
            go.Scatter(x=[], y=[], name="GDP"),
            secondary_y=False
        )
        n.add_trace(
            go.Bar(x=[], y=[], name="New Businesses", marker={'color': 'rgba(99, 110, 250, 0.33)'}),
            secondary_y=True
        )
        n.update_layout(
            margin=dict(zip(['t', 'l', 'b', 'r'], [60]+[20]*3)),
            height=250,
            title={'text': 'TTM GDP & New Business Formation', 'y': 0.9},
            legend={'yanchor': 'top', 'y': 1, 'xanchor': 'left', 'x': 0.1, 'bgcolor': 'rgba(0,0,0,0)'}
        )
        n.update_yaxes(title_text='GDP', secondary_y=False)
        n.update_yaxes(title_text='New Businesses', secondary_y=True, range=[0, 30])

        return go.FigureWidget(n)
    
    @staticmethod
    def make_real_gdp_plot():
        n = make_subplots(specs=[[{"secondary_y": True}]])
        n.add_trace(
            go.Scatter(x=[], y=[], name="GDP"),
            secondary_y=False
        )
        n.add_trace(
            go.Scatter(x=[], y=[], name="Real GDP"),
            secondary_y=False
        )
        n.add_trace(
            go.Bar(x=[], y=[], name="New Businesses", marker={'color': 'rgba(99, 110, 250, 0.33)'}),
            secondary_y=True
        )
        n.update_layout(
            margin=dict(zip(['t', 'l', 'b', 'r'], [60]+[20]*3)),
            height=250,
            title={'text': 'TTM GDP & New Business Formation', 'y': 0.9},
            legend={'yanchor': 'top', 'y': 1, 'xanchor': 'left', 'x': 0.1, 'bgcolor': 'rgba(0,0,0,0)'}
        )
        n.update_yaxes(title_text='GDP', secondary_y=False)
        n.update_yaxes(title_text='New Businesses', secondary_y=True, range=[0, 30])

        return go.FigureWidget(n)
    
    def build_app(self):
        # title
        title = self.get_title()
        
        # inputs
        inputs = ipywidgets.HBox(self.widgets['inputs'])
        
        # create balance sheet boxes
        balance_sheets = []
        # split list of balance sheets into equal chunks of 2
        grids_partition = self.partition_list(self.widgets['datagrids'].keys(), 2)
        for l in grids_partition:
            # partition the displays to show a 2-column grid of balance sheets
            hbox_children = []
            for name in l:
                label = ipywidgets.HTML(f'<h5>{name}<h5>')
                datagrid = self.widgets['datagrids'][name]
                vbox = ipywidgets.VBox([label, datagrid], layout={'width': '350px'})
                hbox_children.append(vbox)
            balance_sheets.append(ipywidgets.HBox(hbox_children))
        balance_sheet_display = ipywidgets.VBox([
            title,
            inputs,
            ipywidgets.HTML('<br><h3>Balance Sheets</h3>'),
            ipywidgets.VBox(balance_sheets)
        ])
        
        # charts
        if self.controller.economy == 'credit':
            chart_widgets = ['gdp', 'incomes', 'money_supply']
        elif self.controller.economy == 'fiat':
            chart_widgets = ['gdp', 'unemployment', 'inflation']
        charts = [self.widgets[i] for i in chart_widgets]
        chart_display = ipywidgets.VBox(charts)
        
        # final ui display
        outer_box = ipywidgets.HBox([balance_sheet_display, chart_display])
        return outer_box
        
    def get_title(self):
        econ = self.controller.economy
        if econ == 'credit':
            title_string = 'Pure Credit'
        elif econ == 'fiat':
            title_string = 'Pure Fiat'
        else:
            title_string = 'Hybrid'
            
        return ipywidgets.HTML(f'<h1>{title_string} Economy Simulation</h1>')
    
    @staticmethod
    def partition_list(l, n):
        """Divide a list into equal chunks of n"""
        out = []
        l = list(l)
        for i in range(0, len(l), n):
            out.append(l[i:i + n])
        return out
        
    