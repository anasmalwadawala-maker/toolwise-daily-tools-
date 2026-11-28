# LINKORA storage and download-history design

## What is implemented

- Download job metadata is stored in SQLite at `LINKORA_HISTORY_DB`.
- The default database path is `$DOWNLOAD_DIR/linkora-history.sqlite3`.
- Up to 200 most recent records are restored when the service starts.
- Jobs interrupted by a restart are marked as failed with a clear explanation.
- A finished job whose media file is missing is marked expired; the API does not pretend that the file is still downloadable.
- Job records and media files are still subject to the configured retention window (`JOB_RETENTION_SECONDS`, default two hours).

## Important hosting limitation

SQLite persistence only survives a restart when its database file is on persistent storage. The downloaded media files must also be on persistent storage if users are expected to retrieve them after a restart.

The current Render free service uses an ephemeral filesystem and does not provide a persistent disk. Therefore, on the current free preview host:
- history can be lost when the instance is replaced or restarted;
- completed media files can disappear;
- SQLite adds restart recovery for hosts with a persistent mount, but does not turn an ephemeral filesystem into durable storage.

Do not describe the free preview as providing permanent history or permanent downloads.

## Persistent-host configuration

On a host that provides a persistent disk, mount it at a private application path such as `/var/data/linkora`, then configure both:

- `LINKORA_HISTORY_DB=/var/data/linkora/linkora-history.sqlite3`
- `DOWNLOAD_DIR=/var/data/linkora/downloads`

The application process must have read/write access to that directory. Keep API keys in the hosting provider's secret manager, not in source code. Restrict disk access to the service account and apply a retention policy.

## Not included

- No external object storage provider has been selected or connected.
- No paid storage or hosting has been purchased.
- No production environment has been changed.
- No promise of permanent download availability is made.
