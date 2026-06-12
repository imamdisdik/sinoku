#!/bin/bash
# =============================================================================
# SINOKU Deploy Script — untuk update rutin setelah git push
# Jalankan di VPS:
#   cd /var/www/sinoku/sinoku
#   ./scripts/deploy.sh
# =============================================================================

set -e
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

echo "=== SINOKU Deploy ==="

# ── Cek .env ada ──────────────────────────────────────────────────────────────
if [ ! -f backend/.env ]; then
  echo "❌ ERROR: backend/.env tidak ditemukan!"
  echo "   Jalankan: ./scripts/setup-vps.sh"
  exit 1
fi

# Verifikasi DATABASE_URL pakai host 'db' bukan 'localhost'
if grep -q "localhost" backend/.env 2>/dev/null; then
  echo "❌ ERROR: DATABASE_URL masih pakai 'localhost' — harus 'db'"
  echo "   Edit: nano backend/.env"
  exit 1
fi

echo "✔ backend/.env OK"

# ── Pull tanpa menyentuh .env ─────────────────────────────────────────────────
echo ""
echo "=== Pull dari GitHub ==="
# Jika ada unstaged changes pada file tracked, stash dulu
if ! git diff --quiet 2>/dev/null; then
  echo "Ada perubahan lokal — stash sementara..."
  git stash
fi

git pull --rebase origin main

# ── Build dan restart ─────────────────────────────────────────────────────────
echo ""
echo "=== Docker build & restart ==="
docker compose up -d --build

# ── Tunggu backend siap ───────────────────────────────────────────────────────
echo ""
echo "=== Menunggu backend siap ==="
for i in $(seq 1 15); do
  if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
    echo "✔ Backend siap (percobaan $i)"
    break
  fi
  echo "  Menunggu... ($i/15)"
  sleep 2
done

# ── Jalankan migration terbaru ────────────────────────────────────────────────
echo ""
echo "=== Jalankan migration ==="
LATEST=$(ls backend/migrations/*.sql 2>/dev/null | sort | tail -1)
if [ -n "$LATEST" ]; then
  echo "Migration terakhir: $(basename $LATEST)"
  read -p "Jalankan semua migration? (y/N): " RUN_MIG
  if [ "$RUN_MIG" = "y" ] || [ "$RUN_MIG" = "Y" ]; then
    for sql in backend/migrations/*.sql; do
      echo "  → $(basename $sql)"
      docker compose exec -T db psql -U sinoku -d sinoku_db < "$sql" 2>&1 | tail -3
    done
  fi
fi

echo ""
echo "=== Deploy selesai! ==="
docker compose ps
