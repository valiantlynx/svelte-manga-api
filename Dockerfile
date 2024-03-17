FROM python:3.11-slim

WORKDIR /code 

COPY ./requirements.txt ./
RUN apt-get update && apt-get install git -y && apt-get install curl -y

RUN python -m venv venv
RUN chmod +x ./venv/bin/activate && ./venv/bin/activate
RUN pip install --no-cache-dir -r requirements.txt

COPY ./src ./src

EXPOSE 8000

ENV MANGANELO="https://ww7.manganelo.tv"
ENV CHAPMANGANELO="https://chapmanganelo.com"
ENV MANGACLASH="https://mangaclash.com"
ENV MANGAPARK="https://mangapark.net"

ENV ALLOWED_ORIGINS="https://www.animevariant.com,https://nebulamanga.com,http://localhost:3000,http://localhost:5173,http://localhost:4173"

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]