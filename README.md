# 🏆 FIFA World Cup Analytics Dashboard

An interactive web-based visual analytics platform that explores historical FIFA World Cup data (1930-2022), revealing trends, patterns, and insights through charts and statistics.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)
![Chart.js](https://img.shields.io/badge/Chart.js-4.0-orange.svg)

## ✨ Features

### Interactive Visualizations
- **📈 Goals Trend Line Chart** - Track how scoring has evolved from 1930 to 2022
- **📊 Top Teams Bar Chart** - See which nations dominate by wins, goals, or titles
- **🥧 Continental Pie Chart** - Understand goal distribution by continent
- **⚔️ Team Comparison** - Compare any two teams head-to-head

### Key Questions Answered
1. **Are modern World Cups more defensive?** - Analyze goals per match over time
2. **Which teams have dominated?** - Rank teams by wins, goals, or titles
3. **Do knockout matches have fewer goals?** - Compare group vs knockout stages
4. **How do rivals compare?** - Brazil vs Germany, Argentina vs France, etc.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/prithvi-kaizen/fifa-wc-analytics.git
cd fifa-wc-analytics

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

### Access the Dashboard
Open your browser and navigate to: **http://localhost:5001**

## 📁 Project Structure

```
fifa-wc-analytics/
├── app.py                    # Flask application with API endpoints
├── data_processor.py         # Data processing & analytics logic
├── requirements.txt          # Python dependencies
├── data/
│   ├── matches.csv           # Historical match data (1930-2022)
│   └── tournaments.csv       # Tournament summaries
├── templates/
│   └── index.html            # Dashboard HTML
└── static/
    ├── css/
    │   └── styles.css        # Premium dark theme styling
    └── js/
        └── app.js            # Chart.js visualizations
```

## 🔌 API Endpoints

| Endpoint | Description | Parameters |
|----------|-------------|------------|
| `GET /api/goals-per-worldcup` | Goals and averages per tournament | - |
| `GET /api/top-teams` | Team rankings | `metric` (wins/goals/titles), `limit` |
| `GET /api/goals-by-stage` | Group vs Knockout comparison | - |
| `GET /api/goals-by-continent` | Goals by continent | - |
| `GET /api/team-comparison` | Compare two teams | `team1`, `team2` |
| `GET /api/available-teams` | List all teams | - |

### Example API Calls

```bash
# Top 5 teams by goals
curl "http://localhost:5001/api/top-teams?metric=goals&limit=5"

# Compare Brazil vs Argentina
curl "http://localhost:5001/api/team-comparison?team1=Brazil&team2=Argentina"
```

## 📊 Data Sources

The dashboard uses historical FIFA World Cup data covering:
- **22 World Cups** (1930-2022)
- **250+ matches** in the sample dataset
- **80+ nations** represented

Data fields include: year, host country, teams, scores, attendance, match stage, and more.

## 🎨 Design Features

- **Premium Dark Theme** - Football-inspired colors (deep green, gold accents)
- **Glassmorphism Cards** - Modern frosted glass effect
- **Responsive Layout** - Works on desktop, tablet, and mobile
- **Micro-animations** - Subtle hover effects and transitions
- **Chart Insights** - Dynamic text explaining each visualization

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python, Flask, Pandas |
| Frontend | HTML5, CSS3, JavaScript |
| Charts | Chart.js |
| Styling | Custom CSS with CSS Variables |
| Fonts | Inter (Google Fonts) |

## 📝 License

This project is for educational and demonstration purposes.

---

**Built with ❤️ for football fans and data enthusiasts**
