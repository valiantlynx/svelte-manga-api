# Base image for both environments
FROM python:3.12-slim AS base

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    build-essential \
    portaudio19-dev \
    libsdl2-dev \
    alsa-utils \
    pulseaudio \
    git \
    curl \
    wget \
    unzip \
    sudo \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace 

COPY ./requirements.txt ./
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Set environment variables
ENV MANGANELO="https://ww8.manganelo.tv"
ENV CHAPMANGANELO="https://chapmanganelo.com"
ENV MANGACLASH="https://mangaclash.com"
ENV MANGAPARK="https://mangapark.net"

ENV ALLOWED_ORIGINS="https://www.animevariant.com,https://animevariant.com,https://www.astromanga.com,https://astromanga.com,https://www.auramanga.com,https://auramanga.com,https://www.comicbreeze.com,https://comicbreeze.com,https://www.comicharbor.com,https://comicharbor.com,https://www.ghostscans.com,https://ghostscans.com,https://www.ethermanga.com,https://ethermanga.com,https://www.knightscans.com,https://knightscans.com,https://www.mangaburst.com,https://mangaburst.com,https://www.mangafable.com,https://mangafable.com,https://www.mangacrest.com,https://mangacrest.com,https://www.mangaloom.com,https://mangaloom.com,https://www.mangaorbit.com,https://mangaorbit.com,https://www.mangawhiz.com,https://mangawhiz.com,https://www.mangaspectra.com,https://mangaspectra.com,https://www.mangazenith.com,https://mangazenith.com,https://www.nebulamanga.com,https://nebulamanga.com,https://www.owlscans.com,https://owlscans.com,https://www.otakureads.com,https://otakureads.com,https://www.pageturnmanga.com,https://pageturnmanga.com,https://www.pangeamanga.com,https://pangeamanga.com,https://www.quasarreads.com,https://quasarreads.com,https://www.pixelmanga.com,https://pixelmanga.com,https://www.redscans.com,https://redscans.com,https://www.scanshub.com,https://scanshub.com,https://www.starletmanga.com,https://starletmanga.com,https://www.stellarmanga.com,https://stellarmanga.com,https://www.waterscans.com,https://waterscans.com,https://www.whalescans.com,http://localhost:3000,http://localhost:5173,http://localhost:4173,https://monitor.valiantlynx.com"
ENV MANGANELO_CDN="https://cm.blazefast.co"

# Development-specific stage
FROM base AS dev

# Install Neovim dependencies
RUN curl -LO https://github.com/neovim/neovim/releases/latest/download/nvim-linux64.tar.gz \
    && sudo rm -rf /opt/nvim \
    && sudo tar -C /opt -xzf nvim-linux64.tar.gz \
    && echo 'export PATH="$PATH:/opt/nvim-linux64/bin"' >> ~/.bashrc \
    && chmod +x ~/.bashrc \
    && ~/.bashrc \
    && git clone https://github.com/nvim-lua/kickstart.nvim.git "${XDG_CONFIG_HOME:-$HOME/.config}"/nvim

# Expose ports used in development
EXPOSE 8000 8001 5173 5174 4173

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]

# Production-specific stage
FROM base AS prod

# Expose only the necessary production port
EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
