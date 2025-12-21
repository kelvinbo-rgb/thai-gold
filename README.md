# Thai Gold Live (泰国黄金)

A real-time gold price monitoring and calculation tool for Thailand, optimized for investors and tourists.

## Features
- **Real-time Prices**: Fetches live data from the Gold Traders Association of Thailand (GTA).
- **Exchange Rates**: Live RMB/THB (SuperRich Buying) and THB/USD rates.
- **Integrated Calculators**: Calculate final prices for Bullion and Ornaments with processing fees (Gamnuy) instantly.
- **Historical Charts**: Interactive price trend charts (Week, Month, Year, etc.) powered by Plotly.
- **Unit Converter**: Seamless conversion between Baht (Thai unit), Grams, and Ounces.
- **Multilingual Support**: Available in Chinese (CN), Thai (TH), and English (EN).

## How to Run Locally

1. **Prerequisites**: Python 3.8+
2. **Install Dependencies**:
   ```bash
   pip install streamlit requests beautifulsoup4 pandas plotly
   ```
3. **Run the App**:
   ```bash
   streamlit run app.py
   ```

## Technology Stack
- **Frontend**: Streamlit
- **Scraping**: BeautifulSoup4
- **Data Visualization**: Plotly
- **Data Processing**: Pandas

## Project Structure
- `app.py`: Main Streamlit application UI and logic.
- `utils.py`: Scrapers and conversion utilities.
- `gold_history.csv`: Local storage for price history.

## Credits
Data sourced from Gold Traders Association (GTA) and SuperRich Thailand.
