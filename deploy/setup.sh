#!/bin/bash
set -e

# ============================================================
#  AI-HCP one-click server setup
#  Run this ON the EC2 server, from inside the project folder:
#      sudo bash deploy/setup.sh
# ============================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
SERVER_USER="${SUDO_USER:-ubuntu}"

echo "=============================================="
echo " AI-HCP Deployment Setup Started"
echo " Project folder: $PROJECT_DIR"
echo "=============================================="

# ---------- 1. System packages ----------
echo "[1/7] Installing system packages..."
apt-get update -y
DEBIAN_FRONTEND=noninteractive apt-get install -y \
    nginx \
    python3-venv \
    python3-pip \
    git \
    curl \
    build-essential

# ---------- 2. Node.js ----------
echo "[2/7] Installing Node.js 20..."
if ! command -v node >/dev/null 2>&1; then
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
    DEBIAN_FRONTEND=noninteractive apt-get install -y nodejs
fi
echo "Node version: $(node -v)"

# ---------- 3. Backend setup ----------
echo "[3/7] Setting up Python backend..."
cd "$PROJECT_DIR/crm_backend"

python3 -m venv venv
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt

# Create .env if missing
if [ ! -f .env ]; then
    echo "Creating .env with random JWT secret..."
    cat > .env <<EOF
DATABASE_URL=sqlite:///./crm_fallback.db
JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))")
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
GROQ_API_KEY=
DEFAULT_MODEL=gemma2-9b-it
ALTERNATIVE_MODEL=llama-3.3-70b-versatile
AI_HCP_RELOAD=0
EOF
fi

echo "Seeding database (only first time)..."
if [ ! -f crm_fallback.db ]; then
    ./venv/bin/python seed.py
else
    echo "Database already exists - skipping seed to keep data."
fi

# ---------- 4. Frontend build ----------
echo "[4/7] Building React frontend..."
cd "$PROJECT_DIR/frontend"
npm install --no-audit --no-fund
npm run build

echo "Copying frontend files to /var/www/html..."
rm -rf /var/www/html
mkdir -p /var/www/html
cp -r dist/* /var/www/html/

# ---------- 5. Backend systemd service ----------
echo "[5/7] Installing backend as a service..."
chown -R "$SERVER_USER:$SERVER_USER" "$PROJECT_DIR"

sed -i "s|/home/ubuntu/ai-hcp|$PROJECT_DIR|g" "$SCRIPT_DIR/ai-hcp.service"
sed -i "s|User=ubuntu|User=$SERVER_USER|g" "$SCRIPT_DIR/ai-hcp.service"

cp "$SCRIPT_DIR/ai-hcp.service" /etc/systemd/system/ai-hcp.service
systemctl daemon-reload
systemctl enable ai-hcp
systemctl restart ai-hcp

# ---------- 6. Nginx ----------
echo "[6/7] Configuring Nginx..."
cp "$SCRIPT_DIR/nginx.conf" /etc/nginx/sites-available/ai-hcp
rm -f /etc/nginx/sites-enabled/default
ln -sf /etc/nginx/sites-available/ai-hcp /etc/nginx/sites-enabled/ai-hcp
nginx -t
systemctl enable nginx
systemctl restart nginx

# ---------- 7. Done ----------
echo "[7/7] Setup complete!"

sleep 3
IP=$(curl -s http://checkip.amazonaws.com || curl -s ifconfig.me)
PUBLIC_IP="${IP:-your-server-ip}"

echo ""
echo "=============================================="
echo "  DEPLOYMENT COMPLETE"
echo "=============================================="
echo ""
echo "  Frontend (website):  http://$PUBLIC_IP"
echo "  Backend docs:        http://$PUBLIC_IP/docs"
echo ""
echo "  Login credentials:"
echo "    Username: rep1   Password: password123"
echo "    Username: admin  Password: password123"
echo ""
echo "  NOTE: Make sure AWS Security Group allows"
echo "  HTTP (port 80) from 0.0.0.0/0"
echo "=============================================="