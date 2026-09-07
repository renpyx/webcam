# Webcam Archiver

Ein Tool, das öffentliche Webcam-Bilder (zb. von Strand-Webcams) herunterlädt und archiviert. Kombinierbar mit ein cronjob.

## Bestandteile

- **`main.py`** - lädt für jede in `settings/webcams/*.json` konfigurierte Kamera das aktuelle Bild per `curl` herunter und legt es unter `archive/<kamera>/<datum>/<stunde>.jpg` ab.
- **`cronjob.sh`** - Script zum Aufruf per Cronjob.
- **`settings/config.json`** - Einstellungen
- **`settings/webcams/*.json`** - eine Datei pro Kamera.

## Konfiguration

Jede Kamera wird über eine JSON-Datei in `settings/webcams/` definiert,
zb. `settings/webcams/example.json`:

```json
{
  "name": "example_webcam",
  "url": "https://example.com/webcam/bild.jpg"
}
```

- `name` - Ordnername, unter dem die Bilder archiviert werden
- `url` - Bild-URL der Kamera

## Video-Stream

Liefert eine Kamera einen Videostream (zb. `.m3u8`), wird statt `curl` `ffmpeg` genutzt, um daraus das erste Frame als Bild zu extrahieren. Dafür in der jeweiligen Kamera-JSON zusätzlich `"custom": "ffmpeg_first_frame"` setzen:

```json
{
  "name": "example_stream_webcam",
  "url": "https://example.com/video-stream.m3u8",
  "custom": "ffmpeg_first_frame"
}
```

Voraussetzung: `ffmpeg` ist installiert und der Pfad dazu in `settings/config.json` hinterlegt (Standard: `ffmpeg`). Bei fehlern wird es bis zu dreimal mit 30 Sekunden Abstand erneut versucht.

## Ausführen

```bash
python3 main.py
```

Für den Dauerbetrieb per Cron `cronjob.sh` eintragen, zb. stündlich:

```
0 * * * * /pfad/zu/cronjob.sh

# Optional mit log:
0 * * * * /pfad/zu/cronjob.sh >> /var/log/webcam.log 2>&1
```
