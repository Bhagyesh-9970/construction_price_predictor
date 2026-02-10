from flask import Flask, render_template_string, request
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import plotly.graph_objs as go
from plotly.offline import plot
import datetime

app = Flask(__name__)

# -------- Generate Dataset (2000 days) --------
dates = pd.date_range(start="2019-01-01", periods=2000, freq="D")
cement_base = np.linspace(300, 500, 2000) + np.random.normal(0, 3, 2000)
steel_base = np.linspace(50000, 65000, 2000) + np.random.normal(0, 800, 2000)
brick_base = np.linspace(6.5, 9.5, 2000) + np.random.normal(0, 0.1, 2000)
sand_base = np.linspace(800, 1200, 2000) + np.random.normal(0, 15, 2000)

data = pd.DataFrame({
    "Date": dates,
    "Cement_Price": cement_base.round(2),
    "Steel_Price": steel_base.round(2),
    "Brick_Price": brick_base.round(2),
    "Sand_Price": sand_base.round(2)
})

# Train models
data['Days'] = (data['Date'] - data['Date'].min()).dt.days
X = data[['Days']]
models = {
    'Cement_Price': LinearRegression().fit(X, data['Cement_Price']),
    'Steel_Price': LinearRegression().fit(X, data['Steel_Price']),
    'Brick_Price': LinearRegression().fit(X, data['Brick_Price']),
    'Sand_Price': LinearRegression().fit(X, data['Sand_Price'])
}

# -------- Flask HTML Template (Animated UI) --------
TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Construction Material Price Predictor</title>
  <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
  <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;500;700&display=swap" rel="stylesheet">
  <style>
    body {
      margin: 0; font-family: "Poppins", sans-serif;
      color: white; background: radial-gradient(circle at top, #1b2735, #090a0f);
      overflow-x: hidden;
    }
    .background { position: fixed; width: 100%; height: 100%; z-index: -1; overflow: hidden; }
    .bubble { position: absolute; bottom: -40px; background: rgba(255,255,255,0.15); border-radius: 50%; animation: floatUp linear infinite; }
    @keyframes floatUp { from { transform: translateY(0); opacity: 0.6; } to { transform: translateY(-120vh); opacity: 0; } }

    .container { text-align: center; padding: 40px; }
    h1 { font-size: 2.5rem; color: #00e5ff; animation: glow 2s ease-in-out infinite alternate; }
    @keyframes glow { from { text-shadow: 0 0 10px #00e5ff; } to { text-shadow: 0 0 25px #00b4d8; } }
    .card { margin: 20px auto; max-width: 650px; background: rgba(255,255,255,0.1); backdrop-filter: blur(10px);
      padding: 30px; border-radius: 20px; box-shadow: 0 0 20px rgba(0,229,255,0.2); animation: fadeIn 1s ease-in-out; }
    @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
    input { margin-top: 10px; padding: 12px; border-radius: 8px; border: none; width: 70%; font-size: 1rem; }
    .btn { margin-top: 15px; padding: 12px 25px; border: none; border-radius: 8px; font-size: 1.1rem;
      background: linear-gradient(135deg, #00e5ff, #00b4d8); color: black; cursor: pointer; transition: all 0.3s; }
    .btn:hover { transform: scale(1.05); box-shadow: 0 0 20px #00e5ff; }

    .result-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; margin-top: 20px; }
    .result-card { padding: 15px; border-radius: 12px; font-size: 1.1rem; transition: transform 0.3s ease; }
    .result-card:hover { transform: translateY(-5px) scale(1.05); }
    .cement { background: rgba(0,229,255,0.2); }
    .steel { background: rgba(255,214,0,0.2); }
    .brick { background: rgba(255,87,34,0.2); }
    .sand { background: rgba(76,175,80,0.2); }

    footer { margin-top: 30px; color: #ccc; font-size: 0.9rem; }
  </style>
</head>
<body>

<div class="background"></div>
<div class="container">
  <h1>🏗️ Construction Material Price Predictor</h1>
  <p>Predict future cost trends for Cement, Steel, Bricks & Sand</p>

  <div class="card">
    <form method="POST">
      <input type="date" name="future_date" required>
      <button type="submit" class="btn">Predict</button>
    </form>

    {% if result %}
      {% if result.error %}
        <p style="color:red">{{ result.error }}</p>
      {% else %}
        <div class="result-grid">
          <div class="result-card cement">Cement: ₹{{ result.Cement_Price }}</div>
          <div class="result-card steel">Steel: ₹{{ result.Steel_Price }}</div>
          <div class="result-card brick">Brick: ₹{{ result.Brick_Price }}</div>
          <div class="result-card sand">Sand: ₹{{ result.Sand_Price }}</div>
        </div>
      {% endif %}
    {% endif %}
  </div>

  <div class="card">
    <h3>📈 Historical Trends</h3>
    {{ plot_html|safe }}
  </div>

  </div>

<script>
  const background = document.querySelector('.background');
  for (let i = 0; i < 25; i++) {
    const bubble = document.createElement('span');
    bubble.classList.add('bubble');
    bubble.style.left = Math.random() * 100 + '%';
    bubble.style.animationDuration = 5 + Math.random() * 10 + 's';
    bubble.style.width = bubble.style.height = 10 + Math.random() * 30 + 'px';
    background.appendChild(bubble);
  }
</script>

</body>
</html>
"""

# -------- Flask Routes --------
@app.route("/", methods=["GET", "POST"])
def index():
    result = None

    # Plotly visualization
    fig = go.Figure()
    for mat in ["Cement_Price", "Steel_Price", "Brick_Price", "Sand_Price"]:
        fig.add_trace(go.Scatter(x=data["Date"], y=data[mat], mode='lines', name=mat))
    fig.update_layout(title="Historical Construction Material Prices", template="plotly_dark", height=400)
    plot_html = plot(fig, output_type='div')

    if request.method == "POST":
        try:
            future_date = pd.to_datetime(request.form["future_date"])
            days_ahead = (future_date - data["Date"].min()).days
            if days_ahead <= 0:
                result = {"error": "Please enter a future date!"}
            else:
                predicted = {
                    mat: round(models[mat].predict([[days_ahead]])[0], 2)
                    for mat in models
                }
                result = {"date": future_date.date(), **predicted}
        except Exception as e:
            result = {"error": str(e)}

    return render_template_string(TEMPLATE, result=result, plot_html=plot_html)

if __name__ == "__main__":
    app.run(debug=True)
