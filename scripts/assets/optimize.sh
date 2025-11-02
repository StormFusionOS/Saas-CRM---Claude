#!/usr/bin/env bash
# Copyright (c) 2025 RiverCityClean
# SPDX-License-Identifier: MIT
#
# This file is part of the RiverCityClean SaaS CRM system.

#==============================================================================
# Asset Optimization Script
#==============================================================================
# Optimizes and validates static assets for production:
# - Minifies SVGs (if svgo available)
# - Generates/verifies favicons
# - Creates/validates site.webmanifest
# - Verifies theme-color matches brand (#005AE0)
#
# Usage:
#   ./scripts/assets/optimize.sh [--app crm|ops-console|all]
#==============================================================================

set -euo pipefail

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
RESET='\033[0m'

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
THEME_COLOR="#005AE0"

echo -e "${BLUE}================================================================================================${RESET}"
echo -e "${BLUE}Asset Optimization${RESET}"
echo -e "${BLUE}================================================================================================${RESET}"
echo ""

# Parse arguments
APP="all"
if [[ $# -gt 0 ]]; then
  case "$1" in
    --app)
      APP="$2"
      ;;
    *)
      echo "Unknown option: $1"
      echo "Usage: $0 [--app crm|ops-console|all]"
      exit 1
      ;;
  esac
fi

APPS=()
if [[ "$APP" == "all" ]]; then
  APPS=("crm" "ops-console")
else
  APPS=("$APP")
fi

# Check for SVG optimization tool
HAS_SVGO=false
if command -v svgo &> /dev/null; then
  HAS_SVGO=true
  echo -e "${GREEN}✓ svgo found - will optimize SVG files${RESET}"
else
  echo -e "${YELLOW}⚠ svgo not found - SVG optimization skipped${RESET}"
  echo -e "  Install: npm install -g svgo"
fi
echo ""

EXIT_CODE=0

optimize_app() {
  local app_name="$1"
  local app_dir="$PROJECT_ROOT/$app_name"
  local public_dir="$app_dir/public"
  local index_html="$app_dir/index.html"

  echo -e "${BLUE}[App: $app_name]${RESET}"
  echo "---------------------------------------------------"

  # 1. Optimize SVGs
  echo -e "${BLUE}[1/4] Optimizing SVG files...${RESET}"
  if [[ "$HAS_SVGO" == true ]]; then
    local svg_count=0
    while IFS= read -r svg_file; do
      if [[ -f "$svg_file" ]]; then
        svgo "$svg_file" --multipass --quiet 2>/dev/null || true
        ((svg_count++))
      fi
    done < <(find "$public_dir" -type f -name "*.svg" 2>/dev/null || true)
    echo -e "${GREEN}✓ Optimized $svg_count SVG file(s)${RESET}"
  else
    echo -e "${YELLOW}⚠ Skipped (svgo not installed)${RESET}"
  fi

  # 2. Check/generate favicons
  echo -e "${BLUE}[2/4] Checking favicons...${RESET}"
  local favicon_ico="$public_dir/favicon.ico"
  local icon_192="$public_dir/icon-192.png"
  local icon_512="$public_dir/icon-512.png"
  local apple_icon="$public_dir/apple-touch-icon.png"

  local missing_favicons=()
  [[ ! -f "$favicon_ico" ]] && missing_favicons+=("favicon.ico")
  [[ ! -f "$icon_192" ]] && missing_favicons+=("icon-192.png")
  [[ ! -f "$icon_512" ]] && missing_favicons+=("icon-512.png")
  [[ ! -f "$apple_icon" ]] && missing_favicons+=("apple-touch-icon.png")

  if [[ ${#missing_favicons[@]} -eq 0 ]]; then
    echo -e "${GREEN}✓ All favicons present${RESET}"
  else
    echo -e "${YELLOW}⚠ Missing favicons: ${missing_favicons[*]}${RESET}"
    echo -e "  Recommendation: Generate from public/brand/logo-icon.svg using:"
    echo -e "    - https://realfavicongenerator.net/"
    echo -e "    - imagemagick: convert logo-icon.svg -resize 192x192 icon-192.png"
    EXIT_CODE=1
  fi

  # 3. Check/generate site.webmanifest
  echo -e "${BLUE}[3/4] Checking site.webmanifest...${RESET}"
  local manifest_file="$public_dir/site.webmanifest"

  if [[ -f "$manifest_file" ]]; then
    echo -e "${GREEN}✓ site.webmanifest exists${RESET}"

    # Validate theme_color
    if grep -q "\"theme_color\": \"$THEME_COLOR\"" "$manifest_file"; then
      echo -e "${GREEN}✓ theme_color matches $THEME_COLOR${RESET}"
    else
      echo -e "${RED}✗ theme_color mismatch (expected: $THEME_COLOR)${RESET}"
      EXIT_CODE=1
    fi
  else
    echo -e "${YELLOW}⚠ site.webmanifest missing - creating template${RESET}"

    local app_display_name
    if [[ "$app_name" == "crm" ]]; then
      app_display_name="RiverCityClean CRM"
    else
      app_display_name="RiverCityClean Ops Console"
    fi

    cat > "$manifest_file" <<EOF
{
  "name": "$app_display_name",
  "short_name": "$(echo $app_display_name | sed 's/RiverCityClean //')",
  "description": "Enterprise SaaS platform for RiverCityClean operations",
  "start_url": "/",
  "display": "standalone",
  "theme_color": "$THEME_COLOR",
  "background_color": "#FFFFFF",
  "icons": [
    {
      "src": "/icon-192.png",
      "sizes": "192x192",
      "type": "image/png",
      "purpose": "any maskable"
    },
    {
      "src": "/icon-512.png",
      "sizes": "512x512",
      "type": "image/png",
      "purpose": "any maskable"
    }
  ]
}
EOF
    echo -e "${GREEN}✓ Created site.webmanifest template${RESET}"
  fi

  # 4. Check index.html for theme-color meta tag
  echo -e "${BLUE}[4/4] Checking index.html theme-color...${RESET}"
  if [[ -f "$index_html" ]]; then
    if grep -q "theme-color" "$index_html"; then
      if grep -q "content=\"$THEME_COLOR\"" "$index_html"; then
        echo -e "${GREEN}✓ theme-color meta tag correct${RESET}"
      else
        echo -e "${RED}✗ theme-color meta tag incorrect (expected: $THEME_COLOR)${RESET}"
        EXIT_CODE=1
      fi
    else
      echo -e "${YELLOW}⚠ theme-color meta tag missing - adding to <head>${RESET}"

      # Backup
      cp "$index_html" "$index_html.bak"

      # Add theme-color and manifest link after viewport meta
      sed -i '/<meta name="viewport"/a\    <meta name="theme-color" content="'"$THEME_COLOR"'" />\n    <link rel="manifest" href="/site.webmanifest" />\n    <link rel="icon" href="/favicon.ico" sizes="any" />\n    <link rel="icon" href="/icon-192.png" type="image/png" sizes="192x192" />\n    <link rel="apple-touch-icon" href="/apple-touch-icon.png" />' "$index_html"

      echo -e "${GREEN}✓ Added theme-color and manifest links${RESET}"
    fi
  else
    echo -e "${RED}✗ index.html not found${RESET}"
    EXIT_CODE=1
  fi

  echo ""
}

# Process each app
for app in "${APPS[@]}"; do
  optimize_app "$app"
done

echo -e "${BLUE}================================================================================================${RESET}"
if [[ $EXIT_CODE -eq 0 ]]; then
  echo -e "${GREEN}✓ Asset optimization complete${RESET}"
else
  echo -e "${YELLOW}⚠ Asset optimization complete with warnings${RESET}"
  echo -e "  Some assets are missing or misconfigured."
  echo -e "  See recommendations above."
fi
echo -e "${BLUE}================================================================================================${RESET}"
echo ""

exit $EXIT_CODE
