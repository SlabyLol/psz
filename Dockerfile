# PSZ – Encrypted archive tool
FROM python:3.12-slim

LABEL org.opencontainers.image.title="psz"
LABEL org.opencontainers.image.description="Encrypted project archive format with paired unpacker"
LABEL org.opencontainers.image.source="https://github.com/SlabyLol/psz"

WORKDIR /app

# Install the tool
COPY pyproject.toml requirements.txt ./
COPY psz/ ./psz/

RUN pip install --no-cache-dir -e .

# Default entrypoint
ENTRYPOINT ["psz"]
CMD ["--help"]
