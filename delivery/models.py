# Etapa 3 — integrare Delivery (Glovo / Bolt / Wolt) prin webhook-uri.
#
# Platformele de delivery *împing* comenzi prin webhook semnat; mapăm item-ul extern
# la rețeta internă și scădem ingredientele (event-driven), spre deosebire de feed-ul
# SoftOK care e citit din MariaDB (pull).
#
# Design complet (webhook HMAC → persist-then-enqueue → idempotență cu ledger,
# POSProvider/Location/ItemMapping/ModifierMapping): docs/architecture.md.
# Roadmap de învățare: milestone-urile M2/M3 din docs/learning-roadmap.md.
#
# Se implementează DUPĂ Fundație + Etapele 1-2 și DOAR după ce accesul la API-ul de
# listare comenzi (Glovo/Bolt/Wolt) e confirmat de client. Până atunci: placeholder gol.

from django.db import models  # noqa: F401
