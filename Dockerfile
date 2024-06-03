FROM python:3.12-slim

WORKDIR /code 

COPY ./requirements.txt ./
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    portaudio19-dev \
    libsdl2-dev \
    alsa-utils \
    pulseaudio \
    git \
    curl \
    wget \
    unzip \
    && rm -rf /var/lib/apt/lists/*
 
RUN python3 -m venv venv
RUN chmod +x /code/venv/bin/activate && . /code/venv/bin/activate
RUN pip3 install --upgrade pip \
    && pip3 install --no-cache-dir -r requirements.txt

COPY ./src ./src

EXPOSE 8000

ENV MANGANELO="https://ww8.manganelo.tv"
ENV CHAPMANGANELO="https://chapmanganelo.com"
ENV MANGACLASH="https://mangaclash.com"
ENV MANGAPARK="https://mangapark.net"

ENV ALLOWED_ORIGINS="https://www.animevariant.com,https://animevariant.com,https://www.astromanga.com,https://astromanga.com,https://www.auramanga.com,https://auramanga.com,https://www.comicbreeze.com,https://comicbreeze.com,https://www.comicharbor.com,https://comicharbor.com,https://www.ghostscans.com,https://ghostscans.com,https://www.ethermanga.com,https://ethermanga.com,https://www.knightscans.com,https://knightscans.com,https://www.mangaburst.com,https://mangaburst.com,https://www.mangafable.com,https://mangafable.com,https://www.mangacrest.com,https://mangacrest.com,https://www.mangaloom.com,https://mangaloom.com,https://www.mangaorbit.com,https://mangaorbit.com,https://www.mangawhiz.com,https://mangawhiz.com,https://www.mangaspectra.com,https://mangaspectra.com,https://www.mangazenith.com,https://mangazenith.com,https://www.nebulamanga.com,https://nebulamanga.com,https://www.owlscans.com,https://owlscans.com,https://www.otakureads.com,https://otakureads.com,https://www.pageturnmanga.com,https://pageturnmanga.com,https://www.pangeamanga.com,https://pangeamanga.com,https://www.quasarreads.com,https://quasarreads.com,https://www.pixelmanga.com,https://pixelmanga.com,https://www.redscans.com,https://redscans.com,https://www.scanshub.com,https://scanshub.com,https://www.starletmanga.com,https://starletmanga.com,https://www.stellarmanga.com,https://stellarmanga.com,https://www.waterscans.com,https://waterscans.com,https://www.whalescans.com,https://whalescans.com,http://localhost:3000,http://localhost:5173,http://localhost:4173,https://monitor.valiantlynx.com"
ENV MANGANELO_CDN="https://cm.blazefast.co"
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
