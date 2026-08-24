# Easy Trade 📈

A web-based trading app designed to make tracking trades, calculating P&L, and managing trading strategies faster and easier.

## 🎯 Project Vision

**Easy Trade** aims to simplify trading by providing:
- Quick trade entry/exit logging
- Automatic P&L calculations
- Trade performance analytics
- MetaTrader 5 integration (planned)
- Plugin support system (planned)
- Desktop app via Electron (Phase 2)
- Trading Robot automation (Phase 3)

## 📋 Development Phases

### Phase 1: MVP (Current - Weeks 1-4)
- ✅ Core trade tracking system
- ✅ P&L calculation engine
- ✅ Web interface (HTML/JS)
- ✅ Basic statistics dashboard

### Phase 2: Stabilization (Weeks 5-8)
- PostgreSQL database
- User authentication
- Trade analytics & reporting
- Data export (CSV/PDF)

### Phase 3: Integrations (Weeks 9-12)
- MetaTrader 5 connection
- Auto-trade logging
- Real-time account balance sync
- Plugin system architecture

### Phase 4: Desktop (Weeks 13+)
- Electron app wrapper
- Local storage
- System tray integration

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- pip (Python package manager)
- Git

### Backend Setup

```bash
# Clone repository
git clone https://github.com/MB-Bidram/Easy-Trade.git
cd Easy-Trade

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn backend.main:app --reload
```

The API will be available at `http://localhost:8000`

### Frontend Setup

Simply open `frontend/index.html` in your browser, or:

```bash
# If you have Python installed:
cd frontend
python -m http.server 8080
```

Then visit `http://localhost:8080`

## 📁 Project Structure

```
easy-trade/
├── backend/
│   ├── main.py              # FastAPI application entry
│   ├── models.py            # Data models & schemas
│   ├── database.py          # Database configuration
│   ├── api/
│   │   ├── trades.py        # Trade endpoints
│   │   ├── stats.py         # Statistics endpoints
│   │   └── metatrader.py    # MetaTrader integration (planned)
│   └── utils/
│       ├── calculations.py  # P&L calculation logic
│       └── helpers.py       # Utility functions
├── frontend/
│   ├── index.html           # Main page
│   ├── css/
│   │   └── style.css        # Styling
│   ├── js/
│   │   ├── app.js           # Main application logic
│   │   ├── api.js           # API calls
│   │   └── charts.js        # Chart rendering
│   └── assets/              # Images, icons, etc.
├── requirements.txt         # Python dependencies
├── .gitignore              # Git ignore file
└── README.md               # This file
```

## 🔧 Technology Stack

- **Backend**: Python, FastAPI, SQLAlchemy
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Database**: SQLite (MVP), PostgreSQL (Phase 2)
- **Charts**: Chart.js
- **Future**: MetaTrader 5 SDK, Electron, Plugin System

## 📊 API Endpoints (MVP)

### Trades
- `POST /api/trades/` - Create new trade
- `GET /api/trades/` - Get all trades
- `GET /api/trades/{id}` - Get trade details
- `PUT /api/trades/{id}` - Update trade
- `DELETE /api/trades/{id}` - Delete trade

### Statistics
- `GET /api/stats/summary` - P&L summary
- `GET /api/stats/performance` - Win rate, average gain/loss
- `GET /api/stats/monthly` - Monthly breakdown

## 🎮 Usage Example

1. **Log a Trade**
   - Click "New Trade"
   - Enter ticker (e.g., EURUSD)
   - Set entry price and quantity
   - Submit

2. **Close Trade**
   - Click on trade from history
   - Enter exit price
   - System automatically calculates P&L

3. **View Analytics**
   - Dashboard shows total wins/losses
   - Win rate percentage
   - Trade history with color-coded gains/losses

## 🔐 Security Notes

- Currently MVP (no authentication)
- Phase 2 will add user authentication
- MetaTrader credentials will be encrypted
- Plugin system will have sandboxing (Phase 3)

## 🤝 Contributing

Since this is a personal project currently, we'll outline contribution guidelines as it scales.

## 📝 Roadmap

- [ ] Phase 1: Core MVP
- [ ] Phase 2: Database & Authentication
- [ ] Phase 3: MetaTrader Integration
- [ ] Phase 4: Electron Desktop App
- [ ] Plugin Support System
- [ ] Trading Robot Automation

## 📞 Support

For issues or feature requests, use GitHub Issues.

## 📄 License

MIT License - See LICENSE file for details

---

**Created**: August 2026
**Status**: 🚧 In Development (Phase 1)
