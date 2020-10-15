try:
    
    import streamlit as st
    import pandas as pd
    import base64
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    import yfinance as yf

    st.title('S&P500 Stock Price App')

    st.markdown("""
    This app retrieves the list of the **S&P500** (from Wikipedia) and its corresponding **stock closing price** (year-to-date).
    * **Python libraries:** streamlit, pandas, base64, matplotlib, yfinance.
    * **Data source:** [Wikipedia](https://en.wikipedia.org/wiki/List_of_S%26P_500_companies).
    """)

    st.sidebar.header('User Input Features')

    # Web scraping of S&P500 data

    @st.cache
    def load_data():
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        html = pd.read_html(url, header = 0)
        df = html[0]
        return df

    df = load_data()
    # sector = df.groupby('GICS Sector')

    # Sidebar - Sector selection

    sorted_sector_unique = sorted(df['GICS Sector'].unique())
    selected_sector = st.sidebar.multiselect('Select Company Sector:', sorted_sector_unique)

    # Filter data
    df_selected_sector = df[(df['GICS Sector'].isin(selected_sector))]

    st.header('Display Companies in Selected Sector')
    st.write('Data Dimension: ' + str(df_selected_sector.shape[0]) + ' rows and ' + str(df_selected_sector.shape[1]) + ' columns.')
    st.dataframe(df_selected_sector)

    # Download S&P500 data
    # https://discuss.streamlit.io/t/how-to-download-file-in-streamlit/1806

    def filedownload(df):
        csv = df.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
        href = f'<a href="data:file/csv;base64,{b64}" download="SP500.csv">Download CSV File</a>'
        return href

    st.markdown(filedownload(df_selected_sector), unsafe_allow_html=True)

    # Ajust yfinance variables
    # https://pypi.org/project/yfinance/

    data = yf.download(
            tickers = list(df_selected_sector[:].Symbol),
            period = "ytd",
            interval = "1d",
            group_by = 'ticker',
            auto_adjust = True,
            prepost = True,
            threads = True,
            proxy = None
        )

    # Plot Closing Price of Query Symbol
    def price_plot(symbol):
        df = pd.DataFrame(data[symbol].Close)
        df['Date'] = df.index
        fig, ax = plt.subplots()
        locator = mdates.AutoDateLocator()
        formatter = mdates.ConciseDateFormatter(locator)
        ax.xaxis.set_major_locator(locator)
        ax.xaxis.set_major_formatter(formatter)
        ax.fill_between(df.Date, df.Close, color='skyblue', alpha=0.3)
        ax.plot(df.Date, df.Close, color='skyblue', alpha=0.8)
        ax.set_title(symbol, fontweight='bold')
        ax.set_xlabel('Date', fontweight='bold')
        ax.set_ylabel('Closing Price', fontweight='bold')
        return st.pyplot(fig)
    
    try:

        sorted_symbol_unique = sorted(df_selected_sector['Symbol'].unique())
        selected_symbol = st.sidebar.multiselect('Select Company:', sorted_symbol_unique)
    
        if len(selected_symbol) > 0:
            if len(selected_symbol) > 1:
                num_company = st.sidebar.slider('Select the Number of Companies:', 1, len(selected_symbol))      
                st.write('You selected ' + str(num_company) + ' companies. Click the button below and ASAP your graphs will be displayed.')
                
            else:
                num_company = 1
                st.sidebar.write('You can select more then 1 company.')
        else:       
            st.write('&#9888 Select at least 1 company at sidebar, click the button below and wait your data be plotted.')       

        if st.button('Show Plots'):
            st.header('Stock Closing Price')
            for i in list(selected_symbol)[:num_company]:
                price_plot(i)
    
    except ValueError:
            st.error('&#9888 You must select at least 1 company to plot its stock price graph.')

except ValueError:
    st.error('&#9888 Choose a company sector at sidebar and wait your data be loaded.')