#!/usr/bin/env bash
set -euo pipefail

check_json_health() {
  local url="$1"
  local label="$2"
  local body

  body="$(curl -fsS --max-time 20 "${url}")"
  echo "${label} ${url}"
  echo "${body}"
}

check_head() {
  local url="$1"
  echo "HEAD ${url}"
  curl -fsSI --max-time 20 "${url}" | sed -n '1p'
}

check_json_health "https://api.lavprishjemmeside.dk/health" "lavpris-api"
check_json_health "https://api.ljdesignstudio.dk/health" "ljdesign-api"
check_json_health "https://reporting.theartisan.dk/health" "artisan-reporting"
check_head "https://theartisan.dk/"
