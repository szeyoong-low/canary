# One-shot adoption of the DNS records that already exist in Cloudflare.
#
# These blocks tell Terraform to pull each live record into state instead of
# trying to create it. They are safe to delete once `terraform apply` has run
# and the state is populated — keeping them is harmless but adds noise.

# --- Frontend (Vercel) -------------------------------------------------------

import {
  to = cloudflare_dns_record.apex
  id = "${local.zone_id}/b0e7afbeed96ba1a33644dbf3d0a5685"
}

import {
  to = cloudflare_dns_record.www
  id = "${local.zone_id}/e9783dac62cecc8710e938088f54e5fe"
}

# --- Backend (Railway) -------------------------------------------------------

import {
  to = cloudflare_dns_record.api
  id = "${local.zone_id}/625d8c3b9b5d5aa894434d5925f268cc"
}

import {
  to = cloudflare_dns_record.www_api
  id = "${local.zone_id}/b68c74db0f546935f639e3dbc717662d"
}

import {
  to = cloudflare_dns_record.railway_verify_api
  id = "${local.zone_id}/035ba60b8b0e3ad6dc62f6b05ff144db"
}

import {
  to = cloudflare_dns_record.railway_verify_www_api
  id = "${local.zone_id}/aa2f32239195961c45b482c1b5a366de"
}

# --- Mail --------------------------------------------------------------------
# Addressed by map key, so these must match the keys in local.mx_records.

import {
  to = cloudflare_dns_record.mx["eforward1.registrar-servers.com"]
  id = "${local.zone_id}/10d759b0756990d0ada45d4e7f5dd290"
}

import {
  to = cloudflare_dns_record.mx["eforward2.registrar-servers.com"]
  id = "${local.zone_id}/c57dfb1d58324efc80fc69666968f8e7"
}

import {
  to = cloudflare_dns_record.mx["eforward3.registrar-servers.com"]
  id = "${local.zone_id}/5b15c3e2697f8e4af83e20a3f70136e2"
}

import {
  to = cloudflare_dns_record.mx["eforward4.registrar-servers.com"]
  id = "${local.zone_id}/32b68cf41c3c94d4767297fa6675e00a"
}

import {
  to = cloudflare_dns_record.mx["eforward5.registrar-servers.com"]
  id = "${local.zone_id}/c9606e045c1dd6c947f59cb75a074243"
}

# --- Unclassified ------------------------------------------------------------
# Addressed by IP, matching the toset() keys in dns.tf.

import {
  to = cloudflare_dns_record.mailboxes_www["64.29.17.1"]
  id = "${local.zone_id}/cb840898d0a7f34bd87b09c81b6640b5"
}

import {
  to = cloudflare_dns_record.mailboxes_www["64.29.17.65"]
  id = "${local.zone_id}/e1c48c87e6cf9e3d668533c052bdddba"
}
