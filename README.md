# Chi-Square Goodness of Fit Test App

An interactive Streamlit application to perform Chi-Square Goodness of Fit tests. This tool helps you statistically determine if your observed data matches expected theoretical values.

## 🌟 Features

*   **Easy Data Import**: Upload your own CSV/Excel files or use the manual entry table.
*   **Automatic Calculation**: Instantly computes Chi-Square Score, P-Value, Critical Value, and Degrees of Freedom.
*   **Interactive Visualizations**:
    *   **Observed vs Expected**: Bar charts with exact count tooltips.
    *   **Chi-Square Distribution**: Dynamic curve showing the critical region and test statistic.
*   **Clear Conclusions**: Automatic "Reject" or "Fail to Reject" null hypothesis interpretations.
*   **Responsive Design**: Clean UI with a configuration sidebar.

## 🛠️ Installation

1.  Clone this repository.
2.  Install the required dependencies:

```bash
pip install -r requirements.txt
```

## 🚀 Usage

Run the application locally:

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`.

### Data Format
Your data should be in separate columns:
*   **Category**: Names/Labels for the groups.
*   **Observed**: Actual counts.
*   **Expected**: Theoretical counts (or proportions converted to counts).

*Note: The app handles basic data validation logic to ensure you pick numeric columns for calculations.*

## 📊 Visuals powered by Plotly
We replaced static Matplotlib charts with **Plotly** for a richer, interactive user experience.

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
