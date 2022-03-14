from dash import Dash, html, dcc, Input, Output
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np


app = Dash(__name__)
server = app.server

app.config.suppress_callback_exceptions = True


file_path = ('carteira.csv')

df = pd.read_csv(file_path)
df.Date = pd.to_datetime(df.Date)
df.index = df.Date


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


index_page = html.Div([
    html.H1(
            children='Dashboard exibindo informações como o Preço e Volume de ações feito por Douglas Paulino'),

    html.Div(
            children='Alguns conceitos utilizando dash foram treinados. O foco não foi desenvolver o html e sim os gráficos e suas exibições, apesar disso, o uso foi inevitável.'),

    html.Br(),

    dcc.Link('Ver o Preço das ações', href='/preco'),

    html.Br(),

    dcc.Link('Ver o Volume de negociação das ações', href='/volume'),
])

page_price = html.Div(
    children=[   
        html.H1(
            children='Preço das ações'),

        html.Div(
            id = 'PrecoPagina',
            children='Nessa tela, podemos ver um gráfico sobre ações de Itaú, Ambev, Banco do Brasil e Cielo, assim como sua média mensal e semanal'),
        
        html.Br(),

        dcc.Dropdown(
            id='dropdown',
            options=df.Stock.unique(),
            value=df.Stock[0]),
        
        dcc.Checklist(
            id='checklist',
            options=['ITUB3', 'Média de 30 dias','Média de 7 dias'], #pegar valor do Dropdown 
            value=['ITUB3', 'Média de 30 dias','Média de 7 dias']),

        dcc.Graph(
            id='graph',
            figure = {}),
        
        dcc.Link('Voltar à tela inicial', href='/'),

        html.Br(),

        dcc.Link('Volume de negociação', href='/volume'),
    ])

@app.callback(
    Output(component_id='graph', component_property='figure'),
    Output(component_id='checklist', component_property='options'),
    Input(component_id='dropdown', component_property='value'),
    Input(component_id='checklist', component_property='value')
)

def changeText(value, value2): #tentar referenciar outro nome ao inves de 'values'
    df_selected = df.loc[df['Stock']==value]
    med7 = df_selected.Close.rolling(window=7, min_periods=1).mean()
    med30 = df_selected.Close.rolling(window=30, min_periods=1).mean()
    
    fig = go.Figure()

    if str(value) in value2:
        fig.add_trace(go.Candlestick(name=str(value),x=df_selected['Date'],
                open=df_selected['Open'], high=df_selected['High'],
                low=df_selected['Low'], close=df_selected['Close'])
                      )   
                           
    if 'Média de 7 dias' in value2:
        fig.add_trace(go.Scatter(name='Média de 7 dias',x=df_selected.index, y=med7))

    if 'Média de 30 dias' in value2:    
        fig.add_trace(go.Scatter(name='Média de 30 dias', x=df_selected.index, y=med30))
    
    return fig, [value, 'Média de 30 dias','Média de 7 dias']

page_volume = html.Div([
    html.H1('Comparação do Volume diário de negociação das ações'),

    dcc.Checklist(
        id='checklistNomes',
        options=df.Stock.unique(), #pegar valor do Dropdown 
        value=df.Stock.unique()),

    dcc.Graph(
        id='pie-chart',
        figure= {},
        className='Pizza gráfico',
        style={'width': '25%', 'display': 'inline-block'}),

    dcc.Graph(
        id='linhas-chart',
        figure={},
        clickData=None,
        hoverData=None,
        config={
            'staticPlot': False,
            'scrollZoom': True,
            'doubleClick': 'reset',
            'showTips': False,
            'displayModeBar': True,
            'watermark': True},
        className='Linhas Grafico',
        style={'width': '75%', 'display': 'inline-block'}),

    html.Div(id='VolumePagina'),
    html.Br(),
    dcc.Link('Voltar à tela inicial', href='/'),
    html.Br(),
    dcc.Link('Ir para o valor das ações', href='/preco')
    
])

@app.callback(
    Output(component_id='linhas-chart', component_property='figure'),
    Input(component_id='checklistNomes', component_property='value')
    )

def update_graph(nomes):
    dff = df[df.Stock.isin(nomes)]
    fig = px.line(data_frame=dff, x='Date', y = 'Volume', color = 'Stock', labels={'Stock':'Ação', 'Date':'Data'})
    fig.update_layout(
        title='<b>Clique sobre um ponto para atualizar o gráfico de pizza</b>',
        font=dict(family="Arial",size=18))
    fig.update_traces(mode='lines+markers')
    return fig

@app.callback(
    Output(component_id='pie-chart', component_property='figure'),
    Input(component_id='linhas-chart', component_property='hoverData'),
    Input(component_id='linhas-chart', component_property='clickData'),
    Input(component_id='checklistNomes', component_property='value')
)

def update_side_graph(hov_data, clk_data, nomes):
    if hov_data is None:
        dff2 = df[df.Stock.isin(nomes)]
        dff2 = dff2[dff2.Date=='2019-01-14']        
        fig2 = px.pie(data_frame=dff2, values='Volume', names='Stock', labels={'Stock':'Ação'},
        title= 'Volume para: 2019-01-14' )
        return fig2
    else:
        dff2 = df[df.Stock.isin(nomes)]
        hov_year = hov_data['points'][0]['x']
        dff2 = dff2[dff2.Date == hov_year]
        print(dff2.Date == hov_year)
        fig2 = px.pie(data_frame=dff2, values='Volume', names='Stock', 
                    title= 'Volume para: {}' .format(hov_year))
        return fig2




@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])

def display_page(pathname):
    if pathname == '/preco':
        return page_price
    elif pathname == '/volume':
        return page_volume
    else:
        return index_page

if __name__ == '__main__':
    app.run_server()