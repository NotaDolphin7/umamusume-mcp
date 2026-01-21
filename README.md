# Umamusume MCP Server

Server per esporre il database Umamusume a Claude via HTTP.

## Endpoints

- `GET /` - Health check
- `POST /query` - Esegui query SQL (solo SELECT)
- `GET /tables` - Lista tabelle
- `GET /schema/<table>` - Schema tabella
- `GET /info` - Istruzioni per Claude

## Deploy su Render

1. Push su GitHub
2. Connetti repo a Render
3. Deploy automatico

## Aggiornamento Database

Usa lo script `upload_db.py` per caricare il database aggiornato.
