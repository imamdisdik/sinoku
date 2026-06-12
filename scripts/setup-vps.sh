#!/bin/bash
# =============================================================================
# SINOKU VPS Setup Script
# Jalankan sekali saat pertama deploy atau saat .env hilang:
#   chmod +x scripts/setup-vps.sh
#   ./scripts/setup-vps.sh
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
ENV_FILE="$PROJECT_DIR/backend/.env"

echo "=== SINOKU VPS Setup ==="
echo "Project dir: $PROJECT_DIR"

# ── 1. Buat .env jika belum ada ───────────────────────────────────────────────
if [ -f "$ENV_FILE" ]; then
  echo ""
  echo "✔ backend/.env sudah ada:"
  cat "$ENV_FILE"
  echo ""
  read -p "Buat ulang? (y/N): " RECREATE
  if [ "$RECREATE" != "y" ] && [ "$RECREATE" != "Y" ]; then
    echo "Lewati pembuatan .env"
  else
    CREATE_ENV=true
  fi
else
  CREATE_ENV=true
fi

if [ "${CREATE_ENV:-false}" = "true" ]; then
  # Generate secret key otomatis
  SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))")

  cat > "$ENV_FILE" <<EOF
DATABASE_URL=postgresql+asyncpg://sinoku:sinoku123@db:5432/sinoku_db
SECRET_KEY=$SECRET
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=30
CORS_ORIGINS=["http://$(curl -s ifconfig.me 2>/dev/null || echo 'YOUR_VPS_IP')"]
EOF

  echo "✔ backend/.env berhasil dibuat:"
  cat "$ENV_FILE"
fi

# ── 2. Pull kode terbaru ───────────────────────────────────────────────────────
echo ""
echo "=== Pull kode terbaru dari GitHub ==="
cd "$PROJECT_DIR"

# Simpan perubahan lokal (jika ada) tanpa menyentuh .env
STASH_OUT=$(git stash --include-untracked 2>&1 || true)
echo "$STASH_OUT"

git pull --rebase origin main

# ── 3. Build dan restart container ───────────────────────────────────────────
echo ""
echo "=== Build dan restart Docker containers ==="
docker compose down
docker compose up -d --build

# ── 4. Tunggu DB siap ────────────────────────────────────────────────────────
echo ""
echo "=== Menunggu database siap... ==="
for i in $(seq 1 15); do
  if docker compose exec -T db pg_isready -U sinoku -d sinoku_db > /dev/null 2>&1; then
    echo "✔ Database siap (percobaan $i)"
    break
  fi
  echo "  Menunggu... ($i/15)"
  sleep 2
done

# ── 5. Jalankan migration jika ada yang belum ─────────────────────────────────
echo ""
echo "=== Cek dan jalankan migration ==="
for sql in "$PROJECT_DIR"/backend/migrations/*.sql; do
  FNAME=$(basename "$sql")
  echo "Menjalankan $FNAME..."
  docker compose exec -T db psql -U sinoku -d sinoku_db < "$sql" 2>&1 | tail -5
done

echo ""
echo "=== Selesai! ==="
echo "Status container:"
docker compose ps
